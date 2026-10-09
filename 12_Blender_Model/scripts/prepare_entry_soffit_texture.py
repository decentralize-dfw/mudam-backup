"""Procedural linear mineral grain candidate, not a photograph or source scan."""
from pathlib import Path
import numpy as np
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[1];W,H=1536,1152;SX,SY=3.2,2.4
x=np.arange(W,dtype=np.float32)[None,:]*SX/W;y=np.arange(H,dtype=np.float32)[:,None]*SY/H
rng=np.random.default_rng(5309);grain=np.zeros((H,W),dtype=np.float32)
for fx,fy,amp in [(1,2,.7),(3,13,.35),(2,41,.5),(5,103,.3),(3,199,.18)]:grain+=amp*np.sin(2*np.pi*(fx*x/SX+fy*y/SY)+rng.uniform(0,2*np.pi))
board=np.floor(y/.16).astype(int);tones=rng.uniform(-7,7,15)[np.clip(board,0,14)];joint=np.minimum(y%.16,.16-y%.16);depth=np.clip((.0015-joint)/.0015,0,1)
base=np.broadcast_to(np.array([196,191,177],dtype=np.float32),(H,W,3)).copy();base+=(grain*2.2+tones-depth*8)[...,None]
height=grain*.000025-depth*.00015;dx=(np.roll(height,-1,1)-np.roll(height,1,1))/(2*SX/W);dy=(np.roll(height,-1,0)-np.roll(height,1,0))/(2*SY/H);normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
files=[]
for suffix,data in [('basecolor',base),('normal',(normal*.5+.5)*255)]:
 p=B/'textures'/f'R60_soffit_linear_grain_candidate_{suffix}.png';Image.fromarray(np.clip(data,0,255).astype(np.uint8)).save(p);files.append(dict(path=p.relative_to(B.parent).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(B/'reports/R60_texture_receipt.json').write_text(json.dumps(dict(files=files,repeat_m=[SX,SY],board_width_candidate_m=.16,source_ids=['008','011','012','013'],seed=5309,status='procedural_linear_mineral_appearance_candidate',limits=['Photographs support linear grain on the recess underside, but concrete mix, formwork species, board width, colour and roughness are not identified.','No source image altered or used as a texture scan; no geometry displacement.']),indent=2),encoding='utf8')
