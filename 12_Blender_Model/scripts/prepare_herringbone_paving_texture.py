"""R62 corrects the bond after close review of source013. Metric module remains a candidate."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
B=Path(__file__).resolve().parents[1];W=H=1536;period=3.2;unit=.05;L=4;cells=64;coverage=np.zeros((cells,cells),dtype=np.int16);colour=Image.new('RGB',(W,H),(39,42,43));height=Image.new('L',(W,H),90);d=ImageDraw.Draw(colour);dh=ImageDraw.Draw(height);count=0
# Lattice basis (L,L),(-1,1); one horizontal and one vertical rectangle per cell.
for i in range(-20,30):
 for j in range(-80,80):
  x=L*i-j;y=L*i+j
  for ax,ay,sx,sy,orient in [(x,y,L,1,0),(x+L,y,1,L,1)]:
   if ax>=cells or ay>=cells or ax+sx<=0 or ay+sy<=0:continue
   coverage[max(0,ay):min(cells,ay+sy),max(0,ax):min(cells,ax+sx)]+=1;count+=1
   seed=((ax%cells)*73856093+(ay%cells)*19349663+orient*83492791)%2**32;rr=np.random.default_rng(seed);tone=np.array([77,80,81])+rr.normal(0,7);g=.002;cut=.002;xx=ax*unit;yy=ay*unit;ww=sx*unit;hh=sy*unit;poly=[(xx+g+cut,yy+g),(xx+ww-g-cut,yy+g),(xx+ww-g,yy+g+cut),(xx+ww-g,yy+hh-g-cut),(xx+ww-g-cut,yy+hh-g),(xx+g+cut,yy+hh-g),(xx+g,yy+hh-g-cut),(xx+g,yy+g+cut)];px=[(round(a/period*W),round(b/period*H)) for a,b in poly];d.polygon(px,fill=tuple(np.clip(tone,0,255).astype(int)));dh.polygon(px,fill=int(rr.integers(155,166)))
assert np.all(coverage==1),np.unique(coverage,return_counts=True)
rng=np.random.default_rng(6213);base=np.array(colour,dtype=np.float32);grain=rng.normal(0,2.2,(H,W)).astype(np.float32);base+=grain[...,None];h=(np.array(height,dtype=np.float32)-90)/75*.0018+grain*.00003;dx=(np.roll(h,-1,1)-np.roll(h,1,1))/(2*period/W);dy=(np.roll(h,-1,0)-np.roll(h,1,0))/(2*period/H);normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);files=[]
for suffix,data in [('basecolor',base),('normal',(normal*.5+.5)*255)]:
 p=B/'textures'/f'R62_herringbone_candidate_{suffix}.png';Image.fromarray(np.clip(data,0,255).astype(np.uint8)).save(p);files.append(dict(path=p.relative_to(B.parent).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(B/'reports/R62_texture_receipt.json').write_text(json.dumps(dict(files=files,resolution=[W,H],repeat_m=[period,period],candidate_module_m=[.20,.05],source_ids=['013','014'],bond='herringbone',coverage_cells=int(coverage.size),coverage_min=int(coverage.min()),coverage_max=int(coverage.max()),limits=['013 foreground clearly shows elongated alternating-direction herringbone, replacing R59 staggered near-square candidate.','Module, joint, colour and relief remain unmeasured; no product or scanned texture claim.','Orientation relative to building is a visual candidate.']),indent=2),encoding='utf8')
