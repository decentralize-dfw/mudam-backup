from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;r=json.loads((B/'reports/R130_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];trees=[]
for name in r['closed_objects']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
for t in r['trees']:
 x,y=t['xy'];fol=bpy.data.objects[t['foliage']];vs=[fol.matrix_world@v.co for v in fol.data.vertices];tr=bpy.data.objects[t['trunk']];ts=[tr.matrix_world@v.co for v in tr.data.vertices];c=sum(ts,Vector())/len(ts)
 q=dict(id=t['id'],radius=max(math.hypot(v.x-x,v.y-y) for v in vs),z_min=min(v.z for v in vs),z_max=max(v.z for v in vs),xy_error=math.hypot(c.x-x,c.y-y),old_generic_hidden=all(bpy.data.objects[n].hide_render and bpy.data.objects[n].hide_get() for n in t['hidden']),needle_solids=t['needle_solids']);trees.append(q)
 if q['radius']>t['radius']+1e-4 or q['z_min']<2.5-1e-4 or q['z_max']>t['height']+1e-4 or q['xy_error']>1e-4 or not q['old_generic_hidden']:fail.append(q)
(B/'reports/R130_verification.json').write_text(json.dumps(dict(file=r['file'],closed_meshes=solids,trees=trees,failures=fail,construction_acceptance=False),indent=2),encoding='utf8');print('R130 failures',fail);assert not fail
