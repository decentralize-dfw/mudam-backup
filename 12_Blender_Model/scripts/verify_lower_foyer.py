"""Reopen R06, inspect evaluated topology and measured vertical clearance."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R06_build_report.json').read_text());args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];r['file']=args[0] if args else r['file'];report_name=args[1] if len(args)>1 else 'R06_verification.json';bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[];obj=bpy.data.objects[r['closed_objects'][0]].evaluated_get(deps);me=obj.to_mesh();bm=bmesh.new();bm.from_mesh(me)
summary=dict(name=obj.name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(summary)
if summary['volume']<=0 or summary['nonmanifold'] or summary['zero_faces']:fail.append(summary)
bm.free();bottom=r['ceiling_underside_m'];up=Vector((0,0,1));base=bpy.data.objects[r['source_footprint_104_object']].evaluated_get(deps);floor=bpy.data.objects[r['source_ground_footprint_object']].evaluated_get(deps);samples=[]
def hit(ob,p,d,dist):
 inv=ob.matrix_world.inverted();ok,loc,_,_=ob.ray_cast(inv@p,inv.to_3x3()@d,distance=dist);return ob.matrix_world@loc if ok else None
# Sample centroids of all horizontal underside triangles. Every retained ceiling
# patch must be supported by the registered basement and covered by L00 above.
me.calc_loop_triangles()
for tri in me.loop_triangles:
 vertices=[obj.matrix_world@me.vertices[i].co for i in tri.vertices]
 if not all(abs(v.z-bottom)<1e-4 for v in vertices):continue
 p=sum(vertices,Vector())/3;low=hit(base,p-up*.01,-up,8);high=hit(floor,p+up*.01,up,1);clear=abs((p.z-low.z)-r['published_clear_height_m']) if low else None
 ok=low is not None and high is not None and clear<1e-4;samples.append(dict(point=list(p),clearance_error_m=clear,ground_above=high is not None,passed=ok))
 if not ok:fail.append(samples[-1])
obj.to_mesh_clear()
if not samples:fail.append('No underside samples')
assert all(bpy.data.objects[n].hide_render for n in r['cutters'])
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,underside_clearance_samples=samples,published_room_clearance_applied_conditionally=True,construction_acceptance=False);(B/'reports'/report_name).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(file=r['file'],solids=solids,samples=len(samples),failures=fail),indent=2));assert not fail,fail
