"""Reconstruct canopy occupancy from downloaded ACT textures and surface heights."""
from pathlib import Path
import sys,json,struct,io
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely,pyproj,rasterio
from scipy.ndimage import gaussian_filter,binary_closing,maximum_filter,distance_transform_edt
from scipy.spatial import cKDTree
from shapely.geometry import Polygon,LineString,Point
from PIL import Image,ImageDraw,ImageFilter
D=R/'.local_source_cache/r158';D.mkdir(exist_ok=True)
S=R/'.local_source_cache/act_context/local_glb';manifest=json.loads((S/'manifest.json').read_text())
step=2.;origin=np.array([-500.,-450.]);shape=(550,575);top=np.full(shape,-999.,np.float32);green=np.zeros(shape,np.float32);hits=np.zeros(shape,np.uint32)
T=pyproj.Transformer.from_crs(32632,2169,always_xy=True)
yy,xx=np.indices(shape);X=origin[0]+(xx+.5)*step;Y=origin[1]+(yy+.5)*step
gx,gy=T.transform((X+293425).ravel(),(Y+5499960).ravel());datum=json.loads((R/'.local_source_cache/r152/clean_site.json').read_text())['datum']
with rasterio.open(R/'references/terrain_lidar2024/mudam_far_mnt_2024.tif') as ds: ground=np.array([a[0] for a in ds.sample(zip(gx,gy))]).reshape(shape)-datum
def acc(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);w={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']]
 return np.ndarray((a['count'],w),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',w*dt.itemsize),dt.itemsize))
for n,row in enumerate(manifest['tiles']):
 raw=(S/row['file']).read_bytes();jl=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+jl]);b=raw[28+jl:]
 for mesh in j['meshes']:
  for p in mesh['primitives']:
   v=acc(j,b,p['attributes']['POSITION']);xy=v[:,[0,2]].copy();xy[:,1]*=-1;ij=np.floor((xy-origin)/step).astype(int);ok=(ij[:,0]>=0)&(ij[:,0]<shape[1])&(ij[:,1]>=0)&(ij[:,1]<shape[0]);ids=np.where(ok)[0];ij=ij[ok];z=v[ok,1]
   uv=acc(j,b,p['attributes']['TEXCOORD_0'])[ok];m=j['materials'][p['material']];ti=m['pbrMetallicRoughness']['baseColorTexture']['index'];im=j['images'][j['textures'][ti]['source']];bv=j['bufferViews'][im['bufferView']];off=bv.get('byteOffset',0);pix=np.asarray(Image.open(io.BytesIO(b[off:off+bv['byteLength']])).convert('RGB'));u=np.clip((uv[:,0]*pix.shape[1]).astype(int),0,pix.shape[1]-1);vv=np.clip((uv[:,1]*pix.shape[0]).astype(int),0,pix.shape[0]-1);rgb=pix[vv,u].astype(float)
   vegetation=(rgb[:,1]>rgb[:,0]*1.035)&(rgb[:,1]>rgb[:,2]*1.07)&(z-ground[ij[:,1],ij[:,0]]>3)&(z-ground[ij[:,1],ij[:,0]]<38)
   np.maximum.at(top,(ij[:,1],ij[:,0]),z);np.add.at(hits,(ij[:,1],ij[:,0]),1);np.add.at(green,(ij[:,1],ij[:,0]),vegetation.astype(float))
 if n%150==0:print('ACT_CANOPY',n,flush=True)
height=top-ground;mask=(green/np.maximum(hits,1)>.28)&(height>3)&(height<38);mask=binary_closing(mask,iterations=1)
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text());exclude=[]
for w in ways:
 t=w['tags'];xy=np.array(w['xy'])-[293425,5499960]
 if len(xy)<2:continue
 if t.get('highway'):exclude.append(LineString(xy).buffer(1.5 if t['highway'] in ('path','footway','steps','track','cycleway') else 4))
 if len(xy)>3 and np.linalg.norm(xy[0]-xy[-1])<.1 and (t.get('building') or str(w['id']) in ('37847302','26424184')):exclude.append(shapely.make_valid(Polygon(xy)).buffer(2))
floors=json.loads((R/'.local_source_cache/r152/site_constraints.json').read_text())['floors'];exclude.extend(Polygon(f['xy']).buffer(2) for f in floors);excluded=shapely.union_all(exclude);mask&=~shapely.intersects_xy(excluded,X,Y)
# Candidate stems fill measured canopy support with overlapping crowns, never open lawns.
rng=np.random.default_rng(158);occupied=np.zeros(shape,bool);trees=[];smooth=gaussian_filter(np.where(mask,height,0),1);candidates=np.argwhere(mask);order=np.argsort(-smooth[mask]);
for idx in order:
 i,k=candidates[idx]
 if occupied[i,k]:continue
 h=float(np.clip(smooth[i,k],5,29));radius=float(np.clip(h*.25,2.5,6));spacing=max(3.5,radius*1.15);xy=[float(X[i,k]),float(Y[i,k])]
 trees.append(dict(xy=xy,height=h,radius=radius,z=float(ground[i,k]),near=bool(np.linalg.norm(xy)<180),source='ACT downloaded mesh: elevated green surface occupancy; inferred stem, not surveyed tree'))
 r=int(np.ceil(spacing/step));a=max(0,i-r);bb=min(shape[0],i+r+1);c=max(0,k-r);dd=min(shape[1],k+r+1);occupied[a:bb,c:dd]|=(X[a:bb,c:dd]-xy[0])**2+(Y[a:bb,c:dd]-xy[1])**2<spacing**2
np.savez_compressed(D/'act_canopy.npz',mask=mask,top=top,ground=ground,green=green,hits=hits)
(D/'trees.json').write_text(json.dumps({'trees':trees,'source_tiles':len(manifest['tiles']),'canopy_area_m2':int(mask.sum()*step*step),'method':'ACT elevated green texels, 2m raster; building/path exclusion; inferred overlapping crowns','not_exact_individual_tree_inventory':True}))
# Leafy twig texture: cutout geometry rather than solid blobs. Shared by all crown cards.
im=Image.new('RGBA',(512,512));draw=ImageDraw.Draw(im);rng=np.random.default_rng(159)
for branch in range(7):
 x0,y0=256,480;xt=int(rng.uniform(80,432));yt=int(rng.uniform(35,260));draw.line((x0,y0,xt,yt),fill=(70,67,37,255),width=3)
 for t in np.linspace(.22,1,8):
  cx=x0+(xt-x0)*t;cy=y0+(yt-y0)*t
  for side in (-1,1):
   angle=-1.57+side*rng.uniform(.6,1.4);le=rng.uniform(18,33);wi=le*.42;u=np.array([np.cos(angle),np.sin(angle)]);v=np.array([-u[1],u[0]]);c=np.array([cx,cy]);tip=c+u*le;middle=c+u*le*.52;color=(int(rng.uniform(42,76)),int(rng.uniform(76,119)),int(rng.uniform(24,47)),255);pts=[tuple(c),tuple(middle+v*wi),tuple(tip),tuple(middle-v*wi)];draw.polygon(pts,fill=color);draw.line([tuple(c),tuple(tip)],fill=(95,123,57,255),width=1)
im.save(R/'textures/R158_leafy_twig.png');print('R158_SOURCE_TREES',len(trees),'CANOPY_M2',int(mask.sum()*4),flush=True)
