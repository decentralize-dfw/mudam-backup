"""Check main-roof rectangular frame end sections against other active frames.

Read-only sampling: a flagged cap needs visual/source review before extension.
"""
from pathlib import Path
import bpy,json,sys,math,re,itertools
from mathutils import Vector
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
r=verified_current_scene();bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));beams=[];skipped=[];cells={};step=.5
for ob in bpy.context.scene.objects:
 if not ob.name.startswith('P10_') or not any(x in ob.name for x in ['_GRID_','_EDGE_']) or ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 ps=[ob.matrix_world@v.co for v in ob.data.vertices]
 if len(ps)!=8:skipped.append(ob.name);continue
 axes=[ps[1]-ps[0],ps[3]-ps[0],ps[4]-ps[0]];lengths=[a.length for a in axes];axes=[a.normalized() for a in axes]
 if any(abs(axes[i].dot(axes[j]))>.0001 for i,j in [(0,1),(0,2),(1,2)]):skipped.append(ob.name);continue
 row=dict(name=ob.name,origin=ps[0],axes=axes,lengths=lengths,points=ps);idx=len(beams);beams.append(row)
 lo=[math.floor((min(p[i] for p in ps)-.002)/step) for i in range(3)];hi=[math.floor((max(p[i] for p in ps)+.002)/step) for i in range(3)]
 for key in itertools.product(*(range(lo[i],hi[i]+1) for i in range(3))):cells.setdefault(key,[]).append(idx)
def supports(point,own):
 found=[]
 for j in cells.get(tuple(math.floor(v/step) for v in point),[]):
  if j==own:continue
  b=beams[j];q=point-b['origin'];coordinates=[q.dot(a) for a in b['axes']]
  if all(-.001<=v<=length+.001 for v,length in zip(coordinates,b['lengths'])):found.append(b['name'])
 return found
rows=[];missing=[]
for i,b in enumerate(beams):
 for end in [0,1]:
  found=set();center=b['origin']+b['axes'][0]*b['lengths'][0]*end+b['axes'][1]*b['lengths'][1]*.5+b['axes'][2]*b['lengths'][2]*.5
  for u,v in itertools.product([.05,.5,.95],repeat=2):
   p=b['origin']+b['axes'][0]*b['lengths'][0]*end+b['axes'][1]*b['lengths'][1]*u+b['axes'][2]*b['lengths'][2]*v;found.update(supports(p,i))
  row=dict(name=b['name'],end=end,center=list(center),touching_frames=sorted(found));rows.append(row)
  if not found:missing.append(row)
revision='R'+re.search(r'_R(\d+)_',r['file'])[1];q=dict(file=r['file'],frame_count=len(beams),end_sections=len(rows),findings=missing,skipped_nonrectangular=skipped,construction_acceptance=False,limits=['Nine points per end section with1mm geometric tolerance; not exact Boolean/SAT contact proof.','Only active P10 grid and perimeter profiles; contact with stone, replacement systems or structural nodes may explain a finding.','No connection hardware or unmeasured steel detail is inferred.'])
(B/'reports'/f'{revision}_main_frame_end_contacts.json').write_text(json.dumps(q,indent=2));print(len(beams),'frames',len(rows),'ends',len(missing),'review findings',len(skipped),'skipped');print(json.dumps(missing[:8],indent=2))
