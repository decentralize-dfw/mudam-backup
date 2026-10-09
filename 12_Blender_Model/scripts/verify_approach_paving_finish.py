from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R59_build_report.json').read_text());name=r['surface_object']
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));ob=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());me=ob.to_mesh();vs=[ob.matrix_world@v.co for v in me.vertices];fs=[list(f.vertices) for f in me.polygons];bm=bmesh.new();bm.from_mesh(me);q=dict(volume=bm.calc_volume(signed=True),area=sum(f.calc_area() for f in bm.faces),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();ob.to_mesh_clear();return vs,fs,q
v0,f0,q0=snap(B/'scenes'/r['base_scene']);v1,f1,q1=snap(R/r['file']);tree0=BVHTree.FromPolygons(v0,f0);tree1=BVHTree.FromPolygons(v1,f1);err10=max(tree0.find_nearest(v)[3] for v in v1);err01=max(tree1.find_nearest(v)[3] for v in v0);fail=[]
if q1['nonmanifold'] or q1['zero_faces'] or q1['volume']<=0 or abs(q1['volume']-q0['volume'])>1e-3 or abs(q1['area']-q0['area'])>2e-3 or max(err10,err01)>2e-5:fail.append(dict(surface_changed=[q0,q1,err10,err01]))
ob=bpy.data.objects[name];me=ob.data;uv=me.uv_layers[r['uv_map']];maxerr=0;minarea=1e9
for row in r['faces']:
 f=me.polygons[row['index']];u,v=Vector(row['u']),Vector(row['v']);sx,sy=row['repeat'];coords=[]
 if me.materials[f.material_index].name!=row['material']:fail.append(dict(wrong_material=f.index))
 for li in f.loop_indices:
  p=me.vertices[me.loops[li].vertex_index].co;want=Vector((p.dot(u)/sx,p.dot(v)/sy));actual=uv.data[li].uv;maxerr=max(maxerr,(actual-want).length);coords.append(actual.copy())
 area=abs(sum(a.x*b.y-b.x*a.y for a,b in zip(coords,coords[1:]+coords[:1])))/2;minarea=min(area,minarea)
 if area<1e-11:fail.append(dict(collapsed_uv=f.index))
if maxerr>3e-6:fail.append(dict(uv_error=maxerr))
result=dict(file=r['file'],before=q0,after=q1,max_new_vertex_distance_to_old_surface_m=err10,max_old_vertex_distance_to_new_surface_m=err01,uv_faces=len(r['faces']),uv_max_error=maxerr,uv_min_area=minarea,failures=fail,construction_acceptance=False,limits='Surface extent/area/volume check; only face subdivision and materials intended. It does not verify source dimensions.');(B/'reports/R59_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2));assert not fail,fail
