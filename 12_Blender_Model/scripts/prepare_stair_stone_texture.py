"""Procedural grain-only stone maps, never a calibrated source-photo sample."""
from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
B=Path(__file__).resolve().parents[1];N=1024;size=2.;x=np.arange(N,dtype=np.float32)[None,:]/N;y=np.arange(N,dtype=np.float32)[:,None]/N;rng=np.random.default_rng(46024);cloud=np.zeros((N,N),np.float32)
for a,b,amp in [(1,2,1.1),(4,-3,.8),(11,8,.6),(33,19,.4),(97,-83,.3),(191,151,.16)]:cloud+=amp*np.sin(2*np.pi*(a*x+b*y)+rng.uniform(0,2*np.pi))
base=np.array([216,209,194])+cloud[...,None]*np.array([1.3,1.2,1.]);h=cloud*.00001;dx=(np.roll(h,-1,axis=1)-np.roll(h,1,axis=1))/(2*size/N);dy=(np.roll(h,-1,axis=0)-np.roll(h,1,axis=0))/(2*size/N);normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);files=[]
for suffix,a in [('basecolor',base),('normal',(normal*.5+.5)*255)]:
 p=B/'textures'/f'R46_stone_grain_candidate_{suffix}.png';Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save(p);files.append(dict(path=p.relative_to(B.parent).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(B/'reports/R46_texture_receipt.json').write_text(json.dumps(dict(seed=46024,repeat_m=size,resolution=[N,N],files=files,status='procedural_candidate_not_photographic_scan',limits='Colour, grain and roughness unmeasured; no new structural joints or displacement.'),indent=2),encoding='utf8')
