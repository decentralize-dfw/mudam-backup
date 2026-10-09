from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R45_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));dg=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(dg);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
 bm.free();ob.to_mesh_clear()
walls=[o.evaluated_get(dg) for o in bpy.context.scene.objects if o.name=='R45_STAIR_RECESS_CONTINUOUS' and not o.hide_render];grip=bpy.data.objects['R45_STONE_GRIP_FINISH_CANDIDATE'].evaluated_get(dg)
def hits(obs,p,d,length):
 result=[]
 for ob in obs:
  inv=ob.matrix_world.inverted();ok,loc,no,idx=ob.ray_cast(inv@p,inv.to_3x3()@d,distance=length)
  if ok:result.append(((ob.matrix_world@loc-p).length,ob.name))
 return sorted(result)
visible=[o.evaluated_get(dg) for o in bpy.context.scene.objects if o.type=="MESH" and not o.hide_render and o.visible_get()]
samples=[]
for row in r['cavity_samples']:
 p=Vector(row['front']);n=Vector(row['normal']);recess=hits(visible,p,-n,.3);below=p+Vector((0,0,-.25));base=hits(walls,below,-n,.3);lip=hits([grip],p+n*.1+Vector((0,0,-.14)),-n,.3);q=dict(s=row['s'],recess_hits=recess,retained_wall_hits=base,stone_grip_hits=lip);samples.append(q)
 if not recess or abs(recess[0][0]-.13)>.007 or not base or abs(base[0][0]-.02)>.007 or not lip:fail.append(q)
for row in r['volumes']:
 if row['after']<=0 or row['after']>=row['before']:fail.append(row)
result=dict(file=r['file'],solids=solids,recess_and_lip_samples=samples,failures=fail,construction_acceptance=False);(B/'reports/R45_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),samples=len(samples),failures=fail),indent=2));assert not fail,fail
