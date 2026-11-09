from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
R=Path(__file__).resolve().parents[1];out=R/'textures/r297';out.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(297);N=1024
def field(size):
 im=Image.fromarray(np.uint8(rng.random((size,size))*255));return np.asarray(im.resize((N,N),Image.Resampling.BICUBIC),dtype=float)/255
large=field(12);medium=field(90);fine=field(N);yy,xx=np.mgrid[0:N,0:N];x=xx/N*1200;y=yy/N*1200
# Authored mineral roof material, no photographs or scan texture pixels.
# Broad gravel/weathering zones are visual interpretations, not surveyed patches.
rust=np.zeros((N,N))
for cx,cy,sx,sy in [(820,300,75,80),(930,430,65,70),(600,240,95,100),(540,400,70,90),(370,690,65,120),(470,820,110,45),(760,400,80,75)]:
 rust+=np.exp(-((x-cx)/sx)**2-((y-cy)/sy)**2)
rust=np.clip(rust*(.4+large*.9),0,1)*.45
base=np.array([149,145,133])[None,None,:]+((large-.5)*12+(medium-.5)*15+(fine-.5)*17)[:,:,None]
base=base*(1-rust[:,:,None])+np.array([128,108,91])[None,None,:]*rust[:,:,None]
Image.fromarray(np.uint8(np.clip(base,0,255))).save(out/'mineral_base.png')
height=(medium-.5)*.5+(fine-.5)*.25;dy,dx=np.gradient(height);normal=np.stack([-dx*.3,dy*.3,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
Image.fromarray(np.uint8((normal*.5+.5)*255)).save(out/'mineral_normal.png')
Image.fromarray(np.uint8(np.clip(222+(medium-.5)*24,0,255))).save(out/'mineral_roughness.png')
print('R297 procedural material generated without source pixels')
