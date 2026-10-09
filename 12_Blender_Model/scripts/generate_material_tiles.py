"""Deterministic modelling textures, not scans or measured material samples.

Only visible material families and joint types are taken from references.
Every module dimension, grain pattern and colour is an editable approximation.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parents[1];out=B/'textures';out.mkdir(exist_ok=True)
W,H=2048,1536;SX,SY=3.2,2.4;rng=np.random.default_rng(3209)
x=np.arange(W,dtype=np.float32)[None,:]*SX/W;y=np.arange(H,dtype=np.float32)[:,None]*SY/H
def noise(seed,terms):
 r=np.random.default_rng(seed);v=np.zeros((H,W),dtype=np.float32)
 for a,b,amplitude in terms:v+=amplitude*np.sin(2*np.pi*(a*x/SX+b*y/SY)+r.uniform(0,2*np.pi))
 return v
def save(kind,base,heights):
 dx=(np.roll(heights,-1,axis=1)-np.roll(heights,1,axis=1))/(2*SX/W);dy=(np.roll(heights,-1,axis=0)-np.roll(heights,1,axis=0))/(2*SY/H)
 normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
 paths=[]
 for suffix,a in [('basecolor',base),('normal',(normal*.5+.5)*255)]:
  p=out/f'R32_{kind}_{suffix}.png';Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save(p);paths.append(dict(path=p.relative_to(B.parent).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 return paths
stone=np.zeros((H,W,3),dtype=np.float32);height=np.zeros((H,W),dtype=np.float32)
cloud=noise(6,[(1,2,1.2),(3,-1,.8),(9,5,.45),(21,17,.25),(71,-83,.14)])
patterns=[[.8,1,.6,.8],[.6,.8,.6,1.2],[1,.6,.8,.8],[.8,.8,1,.6],[.6,1.2,.6,.8],[1,.8,.8,.6]]
for row,widths in enumerate(patterns):
 y0=row*.4;y1=y0+.4;ym=(y>=y0)&(y<y1);cursor=0
 for width in widths:
  mask=ym&(x>=cursor)&(x<cursor+width);tone=rng.uniform(-5,5);color=np.array([216,209,194],dtype=np.float32)+tone
  stone[mask]=(color+cloud[...,None]*np.array([1,.92,.75]))[mask]
  joint=np.minimum(np.minimum(abs(x-cursor),abs(x-cursor-width)),np.minimum(abs(y-y0),abs(y-y1)))
  depth=np.clip((.0018-joint)/.0018,0,1);height[mask]=(-.0004*depth+.000015*cloud)[mask]
  stone[mask]*=(1-.10*depth[mask,None]);cursor+=width
stone_paths=save('limestone_candidate',stone,height)
wood=np.zeros((H,W,3),dtype=np.float32);height=np.zeros((H,W),dtype=np.float32)
cloud=noise(11,[(1,3,1),(3,7,.6),(5,37,.3),(13,91,.1)])
for row in range(16):
 y0=row*.15;y1=y0+.15;ym=(y>=y0)&(y<y1);widths=patterns[row%len(patterns)];cursor=0
 for width in widths:
  mask=ym&(x>=cursor)&(x<cursor+width);tone=rng.uniform(-8,8);phase=rng.uniform(0,2*np.pi)
  grain=np.sin((y-y0)/.15*2*np.pi*18+np.sin(2*np.pi*x/SX*3+phase)*.7+phase)*1.4
  color=np.array([146,111,75],dtype=np.float32)+tone*np.array([1,.8,.6]);wood[mask]=(color+(cloud+grain)[...,None]*np.array([1,.82,.62]))[mask]
  joint=np.minimum(np.minimum(abs(x-cursor),abs(x-cursor-width)),np.minimum(abs(y-y0),abs(y-y1)));depth=np.clip((.0011-joint)/.0011,0,1);height[mask]=(-.0003*depth+.000005*grain)[mask];wood[mask]*=(1-.25*depth[mask,None]);cursor+=width
wood_paths=save('wood_candidate',wood,height)
report=dict(texture_physical_repeat_m=[SX,SY],resolution=[W,H],stone_course_height_candidate_m=.4,stone_joint_candidate_m=.0018,wood_board_width_candidate_m=.15,wood_joint_candidate_m=.0011,seed=3209,files=stone_paths+wood_paths,source_ids=['003','004','017','056','061','062','069','070','077'],status='procedural_appearance_candidates_not_scans',limits=['No source photograph was edited, resampled into a texture or treated as a calibrated swatch.','Module widths, joint depth, grain, colour and roughness are unmeasured editable candidates.','Surface textures do not replace structural or panel-joint geometry.'],construction_acceptance=False)
(B/'reports/R32_texture_receipt.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('Generated four material candidate maps')
