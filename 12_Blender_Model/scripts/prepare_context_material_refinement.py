"""R129 procedural context materials: source-guided appearance, not a scan."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, json, hashlib
B=Path(__file__).resolve().parents[1]; W,H=2048,1536; SX,SY=4.,3.
rng=np.random.default_rng(129063)
def field(nx,ny):
 a=rng.random((ny,nx)).astype('float32'); a=np.tile(a,(3,3))
 return np.asarray(Image.fromarray(a).resize((3*W,3*H),Image.Resampling.BICUBIC),dtype=np.float32)[H:2*H,W:2*W]
fine=rng.normal(0,1,(H,W)).astype('float32'); cloud=field(8,6); mottled=field(60,45)
colour=Image.new('RGB',(W,H),(98,94,81)); relief=Image.new('L',(W,H),65)
dc,dh=ImageDraw.Draw(colour),ImageDraw.Draw(relief)
# Unequal courses and irregular stone edges. Edge wrap retains the original 4x3m UV scale.
ys=np.array([0,.19,.43,.64,.88,1.04,1.32,1.55,1.79,2.02,2.27,2.48,2.73,3.])
for row,(a,b) in enumerate(zip(ys,ys[1:])):
 widths=rng.uniform(.19,.65,12); widths*=SX/widths.sum(); offset=rng.uniform(0,SX); cursor=offset
 for width in widths:
  g=.007; x0,x1=cursor+g,cursor+width-g; y0,y1=a+g,b-g
  points=[]
  for t in np.linspace(0,1,6):points.append((x0+t*(x1-x0),y0+rng.uniform(-.005,.006)))
  for t in np.linspace(0,1,4)[1:]:points.append((x1+rng.uniform(-.006,.004),y0+t*(y1-y0)))
  for t in np.linspace(1,0,6)[1:]:points.append((x0+t*(x1-x0),y1+rng.uniform(-.005,.005)))
  for t in np.linspace(1,0,4)[1:]:points.append((x0+rng.uniform(-.004,.006),y0+t*(y1-y0)))
  tone=np.array([119,113,98])+rng.normal(0,6)+rng.normal(0,1.5,3)
  ht=int(rng.uniform(133,152))
  for shift in (-SX,0,SX):
   p=[(round((x+shift)/SX*W),round(y/SY*H)) for x,y in points];dc.polygon(p,fill=tuple(np.clip(tone,0,255).astype(int)));dh.polygon(p,fill=ht)
  cursor+=width
base=np.asarray(colour,dtype=np.float32).copy(); base+=(cloud[...,None]-.5)*20+(mottled[...,None]-.5)*17+fine[...,None]*1.7
height=np.asarray(relief.filter(ImageFilter.GaussianBlur(1.25)),dtype=np.float32)/255*.010+(mottled-.5)*.0014+fine*.00006
rough=.84+(cloud-.5)*.13+(mottled-.5)*.06
files=[]
def save(label,base,h,rough):
 dx=(np.roll(h,-1,1)-np.roll(h,1,1))/(2*SX/W);dy=(np.roll(h,-1,0)-np.roll(h,1,0))/(2*SY/H)
 n=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
 for suffix,data in [('basecolor',base),('normal',(n*.5+.5)*255),('roughness',rough*255)]:
  # Match opposite edge texels; repeat interpolation cannot produce a seam.
  data=data.copy(); edge=(data[:,0]+data[:,-1])/2;data[:,0]=edge;data[:,-1]=edge
  edge=(data[0]+data[-1])/2;data[0]=edge;data[-1]=edge
  p=B/'textures'/f'R129_{label}_{suffix}.png';Image.fromarray(np.clip(data,0,255).astype('uint8')).save(p)
  files.append(dict(path=p.relative_to(B.parent).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
save('historic_masonry',base,height,rough)
patch=field(9,7);mid=field(55,41);blade=field(650,230);dry=np.maximum(patch-.62,0)
base=np.array([78,94,48])[None,None,:]+(patch[...,None]-.5)*np.array([23,25,12])+(mid[...,None]-.5)*np.array([10,14,6])+(blade[...,None]-.5)*np.array([17,21,9])+dry[...,None]*np.array([45,20,18])
save('moat_turf',base,(blade-.5)*.0012+(mid-.5)*.0005,.94+(mid-.5)*.08)
(B/'reports/R129_texture_receipt.json').write_text(json.dumps(dict(files=files,source_ids=['063','065','116'],repeat_m=[SX,SY],resolution=[W,H],measured=False,limits='Procedural appearance only. No reconstructed individual stone, material product, vegetation species, surveyed colour or geometric relief.'),indent=2),encoding='utf8')
