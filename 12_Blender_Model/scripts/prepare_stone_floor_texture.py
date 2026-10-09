"""Deterministic model appearance maps; no source photograph is edited."""
from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
B=Path(__file__).resolve().parents[1];P=json.loads((B/'config/stone_floor_finish.json').read_text());N=2048;rng=np.random.default_rng(43);y,x=np.mgrid[0:N,0:N].astype(float);x/=N;y/=N;tiles=4;variation=rng.uniform(-.025,.025,(tiles,tiles));grain=np.zeros((N,N))
for frequency in [3,7,13,29,47]:
 phase=rng.uniform(0,6.283);grain+=np.sin((x*frequency+y*(frequency*.37)+.13*np.sin(y*18))*6.283+phase)/frequency
grain*=.012;ix=(x*tiles).astype(int)%tiles;iy=(y*tiles).astype(int)%tiles;base=np.clip(np.array([.79,.774,.729])+variation[iy,ix,None]+grain[:,:,None]+rng.normal(0,.0008,(N,N,1)),0,1)
distance=np.minimum(np.minimum(x*tiles%1,1-x*tiles%1),np.minimum(y*tiles%1,1-y*tiles%1))*P['tile_m'];joint=np.clip((P['joint_m']/2-distance)/(P['repeat_m']/N)+.5,0,1);base=base*(1-joint[:,:,None]*.18);height=-joint*.0004+grain*.00003;gy,gx=np.gradient(height,P['repeat_m']/N);normal=np.stack([-gx,-gy,np.ones_like(gx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1)[:,:,None]
paths=[]
for label,data in [('basecolor',base),('normal',normal*.5+.5)]:
 p=B/'textures'/f'R43_stone_floor_candidate_{label}.png';Image.fromarray(np.uint8(np.clip(data,0,1)*255)).save(p);paths.append(dict(path=p.relative_to(B.parent).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=[N,N]))
(B/'reports/R43_texture_receipt.json').write_text(json.dumps(dict(repeat_m=P['repeat_m'],tile_candidate_m=P['tile_m'],maps=paths,scanned=False,colour_calibrated=False),indent=2),encoding='utf8')
