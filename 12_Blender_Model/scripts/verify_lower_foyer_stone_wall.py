from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R143_build_report.json').read_text())
def geometry(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));dep=bpy.context.evaluated_depsgraph_get();snap={}
 for ob in bpy.context.scene.objects:
  if ob.type not in ['MESH','CURVE']:continue
  eo=ob.evaluated_get(dep);me=eo.to_mesh()
  if me is None:continue
  data=[[list(eo.matrix_world@v.co) for v in me.vertices],[list(f.vertices) for f in me.polygons],ob.hide_render,ob.hide_get()];snap[ob.name]=hashlib.sha256(repr(data).encode()).hexdigest();eo.to_mesh_clear()
 return snap
before=geometry(B/'scenes'/r['base_scene']);after=geometry(R/r['file']);differences=[n for n in before.keys()|after.keys() if before.get(n)!=after.get(n)];fail=[];checks=[]
if differences:fail.append(dict(evaluated_geometry_changes=differences))
for t in r['surface_objects']:
 ob=bpy.data.objects[t['name']];me=ob.data;uv=me.uv_layers[r['uv_map']];errors=[];areas=[]
 for row in t['faces']:
  f=me.polygons[row['face']];u,v=Vector(row['u']),Vector(row['v']);sx,sy=row['repeat_m'];coords=[]
  if me.materials[f.material_index].name!=row['material']:fail.append(dict(material=t['name'],face=f.index))
  for li in f.loop_indices:
   p=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;expected=Vector((p.dot(u)/sx,p.dot(v)/sy));actual=uv.data[li].uv;errors.append((actual-expected).length);coords.append(actual.copy())
  area=abs(sum(a.x*b.y-b.x*a.y for a,b in zip(coords,coords[1:]+coords[:1])))/2;areas.append(area)
  if area<1e-11 or not all(math.isfinite(x) for p in coords for x in p):fail.append(dict(collapsed_uv=t['name'],face=f.index))
 q=dict(name=t['name'],faces=len(t['faces']),max_uv_error=max(errors),min_uv_area=min(areas));checks.append(q)
 if q['max_uv_error']>3e-6:fail.append(q)
images=[]
for name in r['materials']:
 for node in bpy.data.materials[name].node_tree.nodes:
  if node.type=='TEX_IMAGE':
   q=dict(material=name,image=node.image.name,packed=bool(node.image.packed_file),size=list(node.image.size));images.append(q)
   if not q['packed']:fail.append(q)
result=dict(file=r['file'],evaluated_geometry_objects_checked=len(before),geometry_identical=not differences,uv_checks=checks,packed_images=images,failures=fail,construction_acceptance=False);(B/'reports/R143_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(objects=len(checks),mapped_faces=sum(q['faces'] for q in checks),geometry_identical=not differences,failures=fail),indent=2));assert not fail,fail
