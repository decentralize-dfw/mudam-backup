"""Photo-family paving candidate; no photo sampling or measured stone module claim."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
B=Path(__file__).resolve().parents[1];W=H=1536;period=3.2;rng=np.random.default_rng(5909);colour=Image.new('RGB',(W,H),(39,42,43));height=Image.new('L',(W,H),90);d=ImageDraw.Draw(colour);dh=ImageDraw.Draw(height)
for row in range(40):
 for col in range(-1,33):
  x=(col+(row%2)*.5)*.1;y=row*.08;gap=.0025;cut=.003;poly=[(x+gap+cut,y+gap),(x+.1-gap-cut,y+gap),(x+.1-gap,y+gap+cut),(x+.1-gap,y+.08-gap-cut),(x+.1-gap-cut,y+.08-gap),(x+gap+cut,y+.08-gap),(x+gap,y+.08-gap-cut),(x+gap,y+gap+cut)];px=[(int(a/period*W),int(b/period*H)) for a,b in poly];v=rng.normal(0,7);tone=np.array([77,80,81])+v;d.polygon(px,fill=tuple(np.clip(tone,0,255).astype(int)));dh.polygon(px,fill=int(rng.integers(155,166)))
base=np.array(colour,dtype=np.float32);grain=rng.normal(0,2.2,(H,W)).astype(np.float32);base+=grain[...,None];h=(np.array(height,dtype=np.float32)-90)/75*.0018+grain*.00003;dx=(np.roll(h,-1,1)-np.roll(h,1,1))/(2*period/W);dy=(np.roll(h,-1,0)-np.roll(h,1,0))/(2*period/H);normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True);files=[]
for suffix,data in [('basecolor',base),('normal',(normal*.5+.5)*255)]:
 p=B/'textures'/f'R59_paving_candidate_{suffix}.png';Image.fromarray(np.clip(data,0,255).astype(np.uint8)).save(p);files.append(dict(path=p.relative_to(B.parent).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(B/'reports/R59_texture_receipt.json').write_text(json.dumps(dict(files=files,resolution=[W,H],repeat_m=[period,period],candidate_module_m=[.1,.08],source_ids=['008','011','012','013'],limits=['Rectangular dark staggered paving family visible in photographs.','Module, joint width, tone and relief are unmeasured appearance parameters. No texture scan and no geometry displacement.']),indent=2),encoding='utf8')
