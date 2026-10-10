"""Metric route atlas generated from archived paths; procedural appearance only."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parents[1];R=B.parent;P=json.loads((B/'config/park_landings.json').read_text());assert hashlib.sha256((R/P['osm_file']).read_bytes()).hexdigest()==P['osm_sha256'];assert hashlib.sha256((R/P['ways_file']).read_bytes()).hexdigest()==P['ways_sha256'];ways=json.loads((R/P['ways_file']).read_text());xml={w.attrib['id']:w for w in ET.parse(R/P['osm_file']).getroot().findall('way')}
routes=[dict(id='83345393',points=P['path_centerline'],surface='paving_stones')]
for id in ['49910981','50643005']:
 w=next(w for w in ways if w['id']==id);routes.append(dict(id=id,points=[(x-293425,y-5499960) for x,y in w['xy']],surface=w['tags']['surface']))
N=4096;x0,y0,x1,y1=-20.,-20.,90.,100.;X,Y=np.meshgrid(np.linspace(x0,x1,N,dtype=np.float32),np.linspace(y1,y0,N,dtype=np.float32));classes=np.zeros((N,N),dtype=np.uint8);U=np.zeros_like(X);V=np.zeros_like(X);best=np.full_like(X,1e8)
for route in routes:
 tags={t.attrib['k']:t.attrib['v'] for t in xml[route['id']].findall('tag')};assert tags['surface']==route['surface'];route['source_tags']=tags
 for a,b in zip(route['points'],route['points'][1:]):
  ax,ay=a;dx,dy=np.array(b)-a;length=float(np.hypot(dx,dy));ux,uy=dx/length,dy/length;along=(X-ax)*ux+(Y-ay)*uy;across=-(X-ax)*uy+(Y-ay)*ux;mask=(along>=0)&(along<=length)&(abs(across)<=P['path_width_m']/2);kind=2 if route['surface']=='sett' else 1;mask&=(abs(across)<best)|(kind>classes);classes[mask]=kind;U[mask]=along[mask];V[mask]=across[mask];best[mask]=abs(across[mask])
rng=np.random.default_rng(133);noise=rng.normal(0,.006,(N,N)).astype(np.float32);linear=np.empty((N,N,3),dtype=np.float32);linear[:]=(.32,.33,.31);height=np.zeros((N,N),dtype=np.float32)
for kind,sx,sy,colour,joint in [(1,.6,.3,(.36,.37,.345),.006),(2,.16,.12,(.15,.16,.145),.007)]:
 mask=classes==kind;row=np.floor(V/sy);xx=np.mod(U+np.mod(row,2)*sx/2,sx);yy=np.mod(V,sy);edge=np.minimum(np.minimum(xx,sx-xx),np.minimum(yy,sy-yy));grout=edge<joint/2;block=np.sin(np.floor(U/sx)*12.9898+row*78.233)*43758.5453;tone=(block-np.floor(block)-.5)*.035+noise
 for c in range(3):linear[:,:,c][mask]=np.clip(colour[c]+tone[mask]-grout[mask]*.055,.02,.8)
 height[mask]=np.where(grout[mask],-.0015,noise[mask]*.002)
srgb=np.where(linear<=.0031308,linear*12.92,1.055*np.power(linear,1/2.4)-.055);gy,gx=np.gradient(height,(y1-y0)/(N-1),(x1-x0)/(N-1));normal=np.stack([-gx,gy,np.ones_like(gx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
paths=[]
for suffix,a in [('basecolor',np.uint8(np.clip(srgb,0,1)*255)),('normal',np.uint8((normal*.5+.5)*255))]:
 p=B/'textures'/f'R133_park_routes_{suffix}.png';Image.fromarray(a).save(p);paths.append(dict(path=p.relative_to(R).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(B/'reports/R133_texture_receipt.json').write_text(json.dumps(dict(routes=routes,bounds=[x0,y0,x1,y1],resolution=[N,N],width_m=P['path_width_m'],textures=paths,osm_sha256=P['osm_sha256'],ways_sha256=P['ways_sha256'],limits=['OSM supports route axes and surface class only. Width inherited4m candidate.','600x300mm paving and160x120mm setts, stagger, colour, joints and relief are replaceable visual candidates; no measured paving schedule.','Atlas changes no terrain geometry or planted boundary.']),indent=2)+'\n')
