"""Reopen R97; test walking surfaces, headroom, well, and entry continuity."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R97_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=r['upper_z'];output='R97_verification.json'
if '--' in sys.argv:
 args=sys.argv[sys.argv.index('--')+1:];r['file']=args[0];output=args[1]
bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
def pt(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get();rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get():continue
 eo=o.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(o.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs,epsilon=.000001);up=Vector((0,0,1))
for step in r['steps']:
 a=Vector(step['center']);hit=t.ray_cast(a+up*.03,-up,.06);rows.append(dict(id=step['name']+'_surface',passed=hit[0] is not None and owners[hit[2]]==step['name'],hit=owners[hit[2]] if hit[0] is not None else None))
 hit=t.ray_cast(a+up*.02,up,2.08);rows.append(dict(id=step['name']+'_headroom_2_1m',passed=hit[0] is None,hit=owners[hit[2]] if hit[0] is not None else None))
for first,second in zip(r['steps'],r['steps'][1:]):
 a=bpy.data.objects[first['name']];b=bpy.data.objects[second['name']];av=[a.matrix_world@v.co for v in a.data.vertices];bv=[b.matrix_world@v.co for v in b.data.vertices];contacts=sum(any((p-q).length<.0001 for q in bv) for p in av);rows.append(dict(id=first['name']+'_next_underside_contact',passed=contacts>=2,contacts=contacts))
for x,y,z,label in [(651,653,0,'ground_entry_floor'),(651,653,UP,'upper_entry_floor'),(651,657,UP,'upper_landing')]:
 a=pt(x,y,z);hit=t.ray_cast(a+up*.03,-up,.26);rows.append(dict(id=label,passed=hit[0] is not None,hit=owners[hit[2]] if hit[0] is not None else None))
for z,label in [(1.1,'ground_portal'),(UP+1.1,'upper_portal')]:
 a=pt(651,651,z);b=pt(651,660,z);hit=t.ray_cast(a,(b-a).normalized(),(b-a).length);rows.append(dict(id=label,passed=hit[0] is None,hit=owners[hit[2]] if hit[0] is not None else None))
a=pt(*r['center_canonical'],UP);rows.append(dict(id='inner_well_open',passed=t.ray_cast(a+up*.05,-up,.1)[0] is None))
for name in r['closed_objects']+r['changed_inherited_objects']:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);rows.append(dict(id=name+'_solid',passed=all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0));bm.free()
out=dict(file=r['file'],checks=rows,failures=[x for x in rows if not x['passed']],construction_acceptance=False,limits=r['limits']);(B/'reports'/output).write_text(json.dumps(out,indent=2));print('R97',len(rows),'checks',out['failures']);assert not out['failures']
