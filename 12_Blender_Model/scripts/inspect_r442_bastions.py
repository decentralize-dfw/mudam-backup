import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R439_KOPRU_BASI_ZEMIN_BAGLANTISI_ADAY_v001.blend'));o=bpy.data.objects['R154_FORT_MASONRY_BODY'];f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());out=[]
for t in f['towers']:
 if t['name']=='CENTRE':continue
 c=Vector((*t['center'],0));vs=[]
 for v in o.data.vertices:
  p=o.matrix_world@v.co;r=math.hypot(p.x-c.x,p.y-c.y);front=-(p.x-c.x)*f['direction'][0]-(p.y-c.y)*f['direction'][1]
  if 4<r<6.5 and front>0:vs.append(dict(index=v.index,point=list(p),radius=r))
 out.append(dict(name=t['name'],vertices=vs))
(R/'reports/R442_EXISTING_BASTION_VERTICES.json').write_text(json.dumps(out,indent=2));print([(r['name'],len(r['vertices']),sorted(set(round(v['point'][2],3) for v in r['vertices'])),[min(v['radius'] for v in r['vertices']),max(v['radius'] for v in r['vertices'])]) for r in out])
