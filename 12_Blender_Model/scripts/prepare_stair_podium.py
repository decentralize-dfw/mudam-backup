"""Extract three observed podium nosings from PDF2016, without treating ink as thickness."""
from pathlib import Path
import sys,json,hashlib,math
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(R/'10_Olcekli_Plan_ve_Fotograf_Analizi/.deps'))
import pymupdf
from PIL import Image,ImageDraw,ImageFont
F=json.loads((B/'config/foundation.json').read_text());C=F['calibration'];k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];source=R/'08_Belgeler/Mudam_Wim_Delvoye_2016_kat_semalari.pdf';doc=pymupdf.open(source);draw=doc[4].get_drawings()
def canonical(p):return [(p.x-ox)/k,(p.y-oy)/k]
contours=[]
for index,count in [(138,4),(137,4),(136,3)]:
 pts=[]
 for item in draw[index]['items'][:count]:
  typ=item[0]
  if typ=='l':seg=[canonical(item[1]),canonical(item[2])]
  elif typ=='c':
   a,b,c,d=map(canonical,item[1:]);seg=[]
   for j in range(41):
    t=j/40;u=1-t;seg.append([u*u*u*a[v]+3*u*u*t*b[v]+3*u*t*t*c[v]+t*t*t*d[v] for v in range(2)])
  else:raise RuntimeError(typ)
  if not pts:pts.append(seg[0])
  pts.extend(seg[1:])
 # 136 starts at its right nose and ends at wall: add the straight end of
 # its observed long front edge from the same path, not an invented tread width.
 if index==136:pts.insert(0,canonical(draw[index]['items'][-1][1]))
 # Shared curved stair-wall boundary is present in the same source path 0.
 a,b,c,d=map(canonical,draw[0]['items'][116][1:]);wall=[]
 for j in range(1001):
  t=j/1000;u=1-t;wall.append([u*u*u*a[v]+3*u*u*t*b[v]+3*u*t*t*c[v]+t*t*t*d[v] for v in range(2)])
 j0=min(range(len(wall)),key=lambda j:math.dist(wall[j],pts[-1]));j1=min(range(len(wall)),key=lambda j:math.dist(wall[j],pts[0]))
 closure=wall[j0:j1+1:4]+[wall[j1]]
 footprint=[]
 for point in pts+closure:
  if not footprint or math.dist(footprint[-1],point)>1e-7:footprint.append(point)
 if math.dist(footprint[0],footprint[-1])<1e-7:footprint.pop()
 contours.append(dict(source_path_index=index,visible_nosing_polyline=pts,closure='Shared PDF2016 curved wall boundary: drawing 0 item 116. Nosing endpoints meet the printed wall band; physical finish junction unresolved.',wall_boundary_source=[0,116],footprint_canonical=footprint))
cfg=dict(id='GH_UP_PODIUM',status='partial_stair_study',sources=['PDF2016_page5','102','103','021','022','023','026'],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),observed_podium_risers=3,draft_riser_m=.16,draft_podium_top_z=.48,riser_basis='Three risers observed in 021/022; 0.16 m is a replaceable proportion hypothesis, not measured.',contours=contours,
 direction=dict(bottom_canonical=[501,478],podium_canonical=[491,489],upper_landing_canonical=[539,551],connection=['L00','LP1'],basis='022: three broad curved steps at lower end. 102/PDF2016 map those steps at the bulbous end. Narrow flight proceeds toward bridge at canonical y~555.'),
 unresolved=['Full flight riser count cannot be taken from visitor diagram line count.','Riser, nosing, stone thickness, curved wall and podium closure require measured/photogrammetric refinement.','No staircase collision/export approval.'])
(B/'config/stair_podium.json').write_text(json.dumps(cfg,indent=2),encoding='utf8')
im=Image.open(next((R/'01_Kat_Planlari').rglob('102_*'))).convert('RGB');dr=ImageDraw.Draw(im)
colors=['#e36c36','#c09820','#138392']
for i,item in enumerate(contours):
 pts=[tuple(p) for p in item['visible_nosing_polyline']];dr.line(pts,fill=colors[i],width=2)
dr.line((491,489,539,551),fill='#cf124b',width=2);dr.polygon([(539,551),(530,547),(536,541)],fill='#cf124b')
im.crop((450,440,565,570)).resize((920,1040)).save(B/'references/P09_podium_plan_check.png')
stair_path=B/'config/stair_systems.json';old=json.loads(stair_path.read_text(encoding='utf8'))
for system in old['systems']:
 if system['id']=='STAIR_GH_UP_0_TO_PLUS1':
  system['direction_correction']=cfg['direction'];system['geometry_status']='Three observed podium steps extracted; old P05 path direction reversed and superseded. Full flight riser count and detailed levels unresolved.'
stair_path.write_text(json.dumps(old,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print('Three podium contours extracted; GH_UP direction corrected.')
