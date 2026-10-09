from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R56_build_report.json').read_text());P=json.loads((B/'config/park_landings.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];envelopes=[]
for name in r['closed_objects']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
 bm.free()
for t in r['trees']:
 x,y=t['xy'];fol=bpy.data.objects[t['foliage']];world=fol.matrix_world.copy();vs=[world@v.co for v in fol.data.vertices];rr=max(math.hypot(v.x-x,v.y-y) for v in vs);lo=min(v.z for v in vs);hi=max(v.z for v in vs);old=bpy.data.objects[t['old_crown']];tr=bpy.data.objects[t['trunk']];ts=[tr.matrix_world@v.co for v in tr.data.vertices];c=sum(ts,Vector())/len(ts);q=dict(id=t['id'],xy_error_m=math.hypot(c.x-x,c.y-y),radius_m=rr,z_min=lo,z_max=hi,old_crown_hidden=old.hide_render and old.hide_get());envelopes.append(q)
 if q['xy_error_m']>1e-4 or rr>t['radius']+1e-5 or lo<P['ground_z']+2.5 or hi>P['ground_z']+t['height']+1e-4 or not q['old_crown_hidden']:fail.append(q)
result=dict(file=r['file'],closed_meshes=solids,trees=envelopes,failures=fail,construction_acceptance=False);(B/'reports/R56_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(meshes=len(solids),trees=len(envelopes),failures=fail),indent=2));assert not fail,fail
