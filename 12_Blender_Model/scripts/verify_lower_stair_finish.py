from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R49_build_report.json').read_text())
def geometry(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));deps=bpy.context.evaluated_depsgraph_get();snap={}
 for ob in bpy.context.scene.objects:
  if ob.type not in ['MESH','CURVE']:continue
  o=ob.evaluated_get(deps);me=o.to_mesh()
  if me is None:continue
  data=[[list(o.matrix_world@v.co) for v in me.vertices],[list(f.vertices) for f in me.polygons],ob.hide_render,ob.hide_get()];snap[ob.name]=hashlib.sha256(repr(data).encode()).hexdigest();o.to_mesh_clear()
 return snap
before=geometry(B/'scenes'/r['base_scene']);after=geometry(R/r['file']);fail=[];checks=[]
if before!=after:fail.append(dict(geometry_differences=[n for n in set(before)|set(after) if before.get(n)!=after.get(n)]))
for target in r['surface_objects']:
 ob=bpy.data.objects[target['name']];uv=ob.data.uv_layers[r['uv_map']];errors=[];areas=[]
 for row in target['faces']:
  f=ob.data.polygons[row['face']];u,v=Vector(row['u']),Vector(row['v']);coords=[]
  if ob.data.materials[f.material_index].name!=r['material']:fail.append(dict(material=ob.name))
  for li in f.loop_indices:
   p=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;expected=Vector((p.dot(u)/2,p.dot(v)/2));actual=uv.data[li].uv;errors.append((actual-expected).length);coords.append(actual.copy())
  area=abs(sum(a.x*b.y-b.x*a.y for a,b in zip(coords,coords[1:]+coords[:1])))/2;areas.append(area)
  if area<1e-11 or not all(math.isfinite(x) for p in coords for x in p):fail.append(dict(collapsed_uv=ob.name,face=f.index,area=area))
 q=dict(name=ob.name,faces=len(target['faces']),max_uv_error=max(errors),min_uv_area=min(areas));checks.append(q)
 if q['max_uv_error']>3e-6:fail.append(q)
for name in r['metal_objects']:
 if bpy.data.objects[name].data.materials[0].name!=r['metal_material']:fail.append(dict(metal_material=name))
images=[n.image for n in bpy.data.materials[r['material']].node_tree.nodes if n.type=='TEX_IMAGE']
if len(images)!=2 or any(not i.packed_file for i in images):fail.append('Missing packed mineral maps')
result=dict(file=r['file'],evaluated_geometry_objects_checked=len(before),geometry_identical=before==after,uv_checks=checks,metal_objects_checked=len(r['metal_objects']),packed_images=[i.name for i in images],failures=fail,construction_acceptance=False);(B/'reports/R49_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(objects=len(checks),metals=len(r['metal_objects']),geometry_identical=before==after,failures=fail),indent=2));assert not fail,fail
