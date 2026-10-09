from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R47_build_report.json').read_text());P=json.loads((B/'config/reading_lantern_finish.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));dg=bpy.context.evaluated_depsgraph_get();fail=[];solids=[];panels=[]
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(dg);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
 bm.free();ob.to_mesh_clear()
for name in r['source_objects_superseded']:
 if not bpy.data.objects[name].hide_render:fail.append(dict(duplicate_skin=name))
for f in r['facets']:
 for c in f['cells']:
  mat=bpy.data.objects[c['name']].data.materials[0];is_glass='GLASS' in mat.name.upper()
  if is_glass==c['opaque']:fail.append(dict(wrong_surface_family=c['name']))
  ps=[Vector(v) for v in c['source_polygon']];n=Vector(c['normal']);ob=bpy.data.objects[c['name']];vs=[ob.matrix_world@v.co for v in ob.data.vertices];dist=[(p-ps[0]).dot(n) for p in vs];q=dict(name=ob.name,min_depth=min(dist),max_depth=max(dist),vertices=len(vs));panels.append(q)
  if abs(min(dist)+P['glass_thickness_m'])>1e-5 or abs(max(dist))>1e-5:fail.append(q)
roof=bpy.data.objects['P05_MAIN_ROOF_DECK']
for fi in r['roof_top_faces']:
 if roof.data.materials[roof.data.polygons[fi].material_index].name!=r['roof_material']:fail.append(dict(roof_finish_face=fi))
result=dict(file=r['file'],solids=solids,panel_depth_checks=panels,unique_frames=len(r['frames']),failures=fail,construction_acceptance=False);(B/'reports/R47_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),panels=len(panels),frames=len(r['frames']),failures=fail),indent=2));assert not fail,fail
