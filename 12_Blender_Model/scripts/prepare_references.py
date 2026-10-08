from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[2]
B=ROOT/'12_Blender_Model'
sys.path.insert(0,str(ROOT/'10_Olcekli_Plan_ve_Fotograf_Analizi/.deps'))
import pymupdf
from PIL import Image,ImageDraw,ImageFont
for p in ['config','scenes','renders/qa','reports','exports','references']:(B/p).mkdir(parents=True,exist_ok=True)
C=json.loads((ROOT/'10_Olcekli_Plan_ve_Fotograf_Analizi/kalibrasyon.json').read_text(encoding='utf-8'))
A=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset']
def world_pdf(p,dy=0):
 x,y=p[0],p[1]-dy
 return [A[0][0]*x+A[0][1]*y+A[0][2]-293425,A[1][0]*x+A[1][1]*y+A[1][2]-5499960]
def canonical(p,dy=0):return [(p[0]-off[0])/k,(p[1]-dy-off[1])/k]
def flatten(d):
 loops=[];cur=[]
 def addseg(pts):
  nonlocal cur
  if cur and math.dist(cur[-1],pts[0])>.01:loops.append(cur);cur=[]
  if not cur:cur.append(list(pts[0]))
  cur.extend([list(p) for p in pts[1:]])
 for item in d['items']:
  typ=item[0]
  if typ=='l':addseg([tuple(item[1]),tuple(item[2])])
  elif typ=='c':
   a,b,c,e=map(tuple,item[1:]);pts=[]
   for j in range(17):
    t=j/16;u=1-t;pts.append(tuple(u*u*u*a[q]+3*u*u*t*b[q]+3*u*t*t*c[q]+t*t*t*e[q] for q in range(2)))
   addseg(pts)
  elif typ=='re':
   r=item[1];addseg([(r.x0,r.y0),(r.x1,r.y0),(r.x1,r.y1),(r.x0,r.y1),(r.x0,r.y0)])
  elif typ=='qu':
   q=item[1];addseg([tuple(q.ul),tuple(q.ur),tuple(q.lr),tuple(q.ll),tuple(q.ul)])
 if cur:loops.append(cur)
 return [p[:-1] if math.dist(p[0],p[-1])<.01 else p for p in loops if len(p)>2]
doc=pymupdf.open(ROOT/'08_Belgeler/Mudam_Wim_Delvoye_2016_kat_semalari.pdf');drawings=doc[4].get_drawings()
selected={'walls_L00_A':(0,0),'walls_L00_B':(120,0),'walls_LP1':(103,251.865),'gallery_L00_E':(107,0),'gallery_L00_W':(116,0),'gallery_LP1_E':(32,251.865),'gallery_LP1_W':(27,251.865),'outline':(232,0)}
data={name:{'pdf_path_index':i,'source':'2016 PDF page5','loops_xy':[list(map(lambda p:world_pdf(p,dy),loop)) for loop in flatten(drawings[i])]} for name,(i,dy) in selected.items()}
(B/'config/vector_reference.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
for level,names,src in [('L00',['walls_L00_A','walls_L00_B'],'102'),('LP1',['walls_LP1'],'103')]:
 path=next((ROOT/'01_Kat_Planlari/Resmi_Kat_Semalari').glob(src+'*'));im=Image.open(path).convert('RGB');d=ImageDraw.Draw(im)
 for name in names:
  i,dy=selected[name]
  for loop in flatten(drawings[i]):
   pts=[canonical(p,dy) for p in loop];d.line(pts+[pts[0]],fill='#cf4127',width=2)
 d.rectangle((0,900,1108,960),fill='white');d.text((20,917),f'{level} / RED: 2016 vector wall outlines; underlying image: official visitor diagram',fill='black')
 im.save(B/'renders/qa'/f'{level}_vector_overlay.png')
config={'version':'v001','phase':'initial architectural shell; NOT detailed or survey verified','crs':'EPSG:32632','origin':[293425,5499960],'calibration':C,'provisional_z':{'LM1':-4.2,'L00':0,'LP1':4.5,'wall_top':9.0,'roof_base':9.0,'roof_shoulder':17.5,'roof_lantern':22.0,'roof_apex':23.0,'pavilion_wall':4.8,'pavilion_shoulder':7.8,'pavilion_lantern':10.8,'pavilion_apex':11.5},'provisional_thickness':{'slab':.3,'glass':.024,'frame':.085},'warning':'All numeric Z, slab and glass/profile thicknesses are explicit visual working assumptions, not measured Mudam values. Vector wall line widths are diagram graphics, not verified construction thicknesses.'}
(B/'config/model_config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
print('Reference paths:',{n:len(v['loops_xy']) for n,v in data.items()})
