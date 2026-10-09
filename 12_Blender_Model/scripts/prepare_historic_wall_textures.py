"""Deterministic coarse masonry/turf appearance studies, not scans."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
B=Path(__file__).resolve().parents[1];W,H=2048,1536;SX,SY=4.,3.;rng=np.random.default_rng(5509);x=np.arange(W,dtype=np.float32)[None,:]*SX/W;y=np.arange(H,dtype=np.float32)[:,None]*SY/H
def noise(seed,terms):
 rand=np.random.default_rng(seed);q=np.zeros((H,W),dtype=np.float32)
 for fx,fy,amp in terms:q+=amp*np.sin(2*np.pi*(fx*x/SX+fy*y/SY)+rand.uniform(0,2*np.pi))
 return q
colour=Image.new('RGB',(W,H),(102,99,85));height=Image.new('L',(W,H),95);dc=ImageDraw.Draw(colour);dh=ImageDraw.Draw(height)
courses=[0,.19,.43,.64,.88,1.04,1.32,1.55,1.79,2.02,2.27,2.48,2.73,3.]
palette=np.array([[142,137,117],[156,146,121],[124,123,109],[177,167,139]])
for row,(y0,y1) in enumerate(zip(courses,courses[1:])):
 widths=rng.uniform(.19,.65,12);widths*=SX/sum(widths);cursor=0
 for width in widths:
  gap=.006;cut=min(width*.12,.035);poly=[(cursor+gap+cut,y0+gap),(cursor+width-gap-cut,y0+gap),(cursor+width-gap,y0+gap+.025),(cursor+width-gap,y1-gap-.018),(cursor+width-gap-cut,y1-gap),(cursor+gap+cut,y1-gap),(cursor+gap,y1-gap-.025),(cursor+gap,y0+gap+.018)]
  pix=[(int(xx/SX*W),int(yy/SY*H)) for xx,yy in poly];tone=palette[rng.integers(0,len(palette))]+rng.uniform(-8,8);dc.polygon(pix,fill=tuple(np.clip(tone,0,255).astype(int)));dh.polygon(pix,fill=int(rng.integers(140,174)));cursor+=width
cloud=noise(55,[(1,2,3.),(2,-1,2.),(7,5,1.),(29,13,.8),(113,-73,.65),(281,193,.35)]);patina=np.maximum(noise(56,[(1,1,.45),(3,-2,.30),(7,3,.2)]),0)
base=np.array(colour,dtype=np.float32)+cloud[...,None];base*=1-patina[...,None]*.18;heights=(np.array(height,dtype=np.float32)-95)/79*.004+cloud*.00012
files=[]
def save(name,base,heights):
 dx=(np.roll(heights,-1,1)-np.roll(heights,1,1))/(2*SX/W);dy=(np.roll(heights,-1,0)-np.roll(heights,1,0))/(2*SY/H);normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 for suffix,data in [('basecolor',base),('normal',(normal*.5+.5)*255)]:
  p=B/'textures'/f'R55_{name}_candidate_{suffix}.png';Image.fromarray(np.clip(data,0,255).astype(np.uint8)).save(p);files.append(dict(path=p.relative_to(B.parent).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
save('historic_masonry',base,heights)
# Reject the v001 crossed sine pattern: its visible plaid is not vegetation.
coarse=noise(57,[(1,2,.45),(3,-1,.30),(7,5,.20),(19,-13,.12),(53,41,.1)])
fine=np.random.default_rng(5510).normal(0,2.5,(H,W)).astype(np.float32)
base=np.array([78,92,51])[None,None,:]+coarse[...,None]*np.array([1.1,1,.7])+fine[...,None];save('moat_turf',base,(coarse*.00003+fine*.00003))
(B/'reports/R55_texture_receipt.json').write_text(json.dumps(dict(files=files,repeat_m=[SX,SY],resolution=[W,H],seed=5509,source_ids=['004','063','065','086','116'],status='procedural_surface_candidates_not_historic_fabric_survey',limits=['Sources show rough coursed stone distinct from the modern pale cladding, darker surface patches and a vegetated moat.','Exact stones, decay patterns, plant species, course heights, mortar and colour are not reconstructed; these are visualization candidates.','No source image altered or texture scan made. Normal maps do not move geometry; turf is a surface approximation, not individual plants.']),indent=2),encoding='utf8')
