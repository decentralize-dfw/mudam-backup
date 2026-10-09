"""Check pavilion-roof rectangular frame end sections against other active frames.

Read-only sampling: a flagged cap needs visual/source review before extension.
"""
from pathlib import Path
import bpy,json,sys,math,re,itertools
from mathutils import Vector,Matrix
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
r=verified_current_scene();bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));beams=[];skipped=[];cells={};step=.5
for ob in bpy.context.scene.objects:
 if not ob.name.startswith('R13_FRAME_') or not any(x in ob.name for x in ['_FRAME_','_EDGE_']) or ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 ps=[ob.matrix_world@v.co for v in ob.data.vertices]
 if len(ps)!=8:skipped.append(ob.name);continue
 axes=[ps[1]-ps[0],ps[3]-ps[0],ps[4]-ps[0]];lengths=[a.length for a in axes];axes=[a.normalized() for a in axes]
 basis=Matrix(axes).transposed()
 if abs(basis.determinant())<.0001:skipped.append(ob.name);continue
 expected={2:ps[1]+ps[3]-ps[0],5:ps[1]+ps[4]-ps[0],6:ps[1]+ps[3]+ps[4]-2*ps[0],7:ps[3]+ps[4]-ps[0]}
 if any((ps[i]-p).length>.0001 for i,p in expected.items()):skipped.append(ob.name);continue
 row=dict(name=ob.name,origin=ps[0],axes=axes,lengths=lengths,points=ps,inverse=basis.inverted());idx=len(beams);beams.append(row)
 lo=[math.floor((min(p[i] for p in ps)-.002)/step) for i in range(3)];hi=[math.floor((max(p[i] for p in ps)+.002)/step) for i in range(3)]
 for key in itertools.product(*(range(lo[i],hi[i]+1) for i in range(3))):cells.setdefault(key,[]).append(idx)
def supports(point,own):
 found=[]
 for j in cells.get(tuple(math.floor(v/step) for v in point),[]):
  if j==own:continue
  b=beams[j];q=point-b['origin'];coordinates=list(b['inverse']@q)
  if all(-.001<=v<=length+.001 for v,length in zip(coordinates,b['lengths'])):found.append(b['name'])
 return found
rows=[];missing=[]
for ob in bpy.context.scene.objects:
 if not ob.name.startswith('R13_TOWER_X_'):continue
 ps=[ob.matrix_world@v.co for v in ob.data.vertices];n=len(ps)//2;rings=[ps[:n],ps[n:]];centers=[sum(ring,Vector())/n for ring in rings]
 for end,ring in enumerate(rings):
  axis=(centers[1-end]-centers[end]).normalized();found=set()
  for inset in [0,.01,.025,.05]:
   for p in ring+[centers[end]]:found.update(supports(p+axis*inset,-1))
  row=dict(name=ob.name,end=end,center=list(centers[end]),touching_frames=sorted(found));rows.append(row)
  if not found:missing.append(row)
revision='R'+re.search(r'_R(\d+)_',r['file'])[1]
q=dict(file=r['file'],end_sections=len(rows),findings=missing,checks=rows,construction_acceptance=False,limits=['Sample rod end section and first50mm of rod against affine frame solids.','No source dimensions or connection hardware inferred.'])
(B/'reports'/f'{revision}_pavilion_rod_solid_contacts.json').write_text(json.dumps(q,indent=2));print(len(rows),'rod ends',len(missing),'findings');print(json.dumps(missing,indent=2))
