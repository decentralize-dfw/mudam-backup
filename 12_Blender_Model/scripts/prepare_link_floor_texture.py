"""R67 procedural diagonal stone joints; not a measured slab schedule."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parents[1];N=2048;period=3.6;module=.9;rng=np.random.default_rng(67067);yy,xx=np.mgrid[0:N,0:N].astype(float);x=xx/N*4;y=yy/N*4;ix=x.astype(int);iy=y.astype(int);fx=x%1;fy=y%1
# Square cells divided along alternating diagonals: an editable triangular candidate.
flip=(ix+iy)%2;d=np.where(flip==0,fx-fy,fx+fy-1);side=(d>0).astype(int);tones=rng.uniform(-.022,.022,(4,4,2));variation=tones[iy%4,ix%4,side];grain=np.zeros((N,N))
for f in [3,7,13,29]:grain+=np.sin((xx/N*f+yy/N*f*.37)*np.pi*2+rng.uniform(0,np.pi*2))/f
base=np.array([.79,.774,.729])+variation[...,None]+grain[...,None]*.01+rng.normal(0,.001,(N,N,1))
distance=np.minimum(np.minimum(fx,1-fx),np.minimum(fy,1-fy))*module;distance=np.minimum(distance,abs(d)*module/np.sqrt(2));joint=np.clip((.0012/2-distance)/(period/N)+.5,0,1);base*=1-joint[...,None]*.16;height=-joint*.0003+grain*.0000003;gy,gx=np.gradient(height,period/N);normal=np.stack([-gx,-gy,np.ones_like(gx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1)[...,None];files=[]
for suffix,data in [('basecolor',base),('normal',normal*.5+.5)]:
 p=B/'textures'/f'R67_diagonal_floor_candidate_{suffix}.png';Image.fromarray(np.uint8(np.clip(data,0,1)*255)).save(p);files.append(dict(path=p.relative_to(B.parent).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(B/'reports/R67_texture_receipt.json').write_text(json.dumps(dict(files=files,resolution=[N,N],repeat_m=[period,period],candidate_cell_m=module,joint_candidate_m=.0012,source_ids=['067'],scanned=False,construction_acceptance=False,limits=['067 supports pale stone and diagonal triangular joints.','Alternating square diagonals,900mm cells,1.2mm joints,colour and orientation are appearance candidates; exact source layout not traced.','No geometric displacement or measured product claim.']),indent=2),encoding='utf8')
