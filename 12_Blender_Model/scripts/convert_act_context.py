"""Lossless topology/texture conversion of ACT b3dm/glTF1 to local glTF2 tiles.

ECEF positions use CESIUM_RTC. The glTF1 Y_UP node and 3D Tiles Y-to-Z
conversion cancel. XY is projected into the existing scene UTM32 frame.
Height is conditionally tied to the existing approach-road model zero.
"""
import json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.local_source_cache/gis_runtime'))
import numpy as np
from pyproj import Transformer
SRC=ROOT/'.local_source_cache/act_context'
OUT=SRC/'local_glb';OUT.mkdir(exist_ok=True)
T=Transformer.from_crs(4978,32632,always_xy=True)
def read(p):
 b=Path(p).read_bytes();h=struct.unpack_from('<4s6I',b);g=b[28+sum(h[3:]):]
 assert g[:4]==b'glTF' and struct.unpack_from('<I',g,4)[0]==1
 size=struct.unpack_from('<I',g,12)[0];j=json.loads(g[20:20+size])
 identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
 yup=[1,0,0,0,0,0,-1,0,0,1,0,0,0,0,0,1]
 assert all(n.get('matrix',identity) in [identity,yup] for n in j['nodes'].values()),'Unexpected source node transform'
 return j,g[20+size:]
def array(j,b,key):
 a=j['accessors'][key];v=j['bufferViews'][a['bufferView']]
 dtype={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']]
 width={'VEC3':3,'VEC2':2,'SCALAR':1,'VEC4':4}[a['type']]
 step=np.dtype(dtype).itemsize
 return np.ndarray((a['count'],width),dtype=dtype,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(a.get('byteStride',step*width),step)).copy()
def positions(j,b,p):
 xyz=array(j,b,p['attributes']['POSITION']).astype('f8')+np.array(j['extensions']['CESIUM_RTC']['center'])
 x,y,z=T.transform(xyz[:,0],xyz[:,1],xyz[:,2]);return np.column_stack((x-293425,y-5499960,z))
if '--available' in sys.argv:
 import hashlib
 rows=[]
 for path in sorted(SRC.glob('Tile*/*.b3dm')):
  raw=path.read_bytes()
  if len(raw)<28 or struct.unpack_from('<I',raw,8)[0]!=len(raw):continue
  rows.append({'path':str(path),'sha256':hashlib.sha256(raw).hexdigest()})
 manifest={'source':'https://data.public.lu/en/datasets/maquette-3d-du-grand-duche-de-luxembourg/','leaves':rows}
else:
 manifest=json.loads((SRC/'manifest.json').read_text())
heights=[]
for row in manifest['leaves']:
 j,b=read(row['path'])
 for mesh in j['meshes'].values():
  for p in mesh['primitives']:
   xyz=positions(j,b,p);sel=(xyz[:,0]>=27)&(xyz[:,0]<=33)&(xyz[:,1]>=69)&(xyz[:,1]<=73)
   heights.extend(xyz[sel,2].tolist())
assert len(heights)>10,'No approach-road tie samples; wait for centre tiles to finish'
datum=float(np.median(heights));print('Road tie',len(heights),datum,np.percentile(heights,[0,10,90,100]),flush=True)
rows=[]
for i,row in enumerate(manifest['leaves']):
 j,b=read(row['path']);binary=bytearray();views=[];accessors=[];primitives=[];materials=[];images=[];textures=[];ntris=0;bounds=[]
 def blob(data):
  while len(binary)%4:binary.append(0)
  k=len(views);views.append({'buffer':0,'byteOffset':len(binary),'byteLength':len(data)});binary.extend(data);return k
 def acc(a,kind,ctype):
  k=len(accessors);v=blob(a.tobytes());d={'bufferView':v,'componentType':ctype,'count':len(a),'type':kind}
  if kind=='VEC3':d.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
  accessors.append(d);return k
 for mesh in j['meshes'].values():
  for p in mesh['primitives']:
   assert p.get('mode',4)==4
   xyz=positions(j,b,p);xyz[:,2]-=datum;bounds.extend([xyz.min(axis=0).tolist(),xyz.max(axis=0).tolist()])
   # glTF Y-up -> Blender Z-up: (x,z,-y)
   xyz=xyz[:,[0,2,1]];xyz[:,2]*=-1
   uv=array(j,b,p['attributes']['TEXCOORD_0']).astype('<f4')
   ids=array(j,b,p['indices']).astype('<u4').reshape(-1);ntris+=len(ids)//3
   pa=acc(xyz.astype('<f4'),'VEC3',5126);ua=acc(uv,'VEC2',5126);ia=acc(ids,'SCALAR',5125)
   mat=j['materials'][p['material']];tex=j['textures'][mat['values']['diffuse']];im=j['images'][tex['source']]['extensions']['KHR_binary_glTF'];v=j['bufferViews'][im['bufferView']];off=v.get('byteOffset',0);imidx=len(images)
   images.append({'bufferView':blob(b[off:off+v['byteLength']]),'mimeType':im['mimeType']});textures.append({'source':imidx})
   mi=len(materials);materials.append({'name':'ACT_2020_PHOTOTEXTURE','pbrMetallicRoughness':{'baseColorTexture':{'index':imidx},'metallicFactor':0,'roughnessFactor':1},'doubleSided':True,'extensions':{'KHR_materials_unlit':{}}})
   primitives.append({'attributes':{'POSITION':pa,'TEXCOORD_0':ua},'indices':ia,'material':mi,'mode':4})
 while len(binary)%4:binary.append(0)
 out={'asset':{'version':'2.0','generator':'ACT CC0 local context conversion'},'extensionsUsed':['KHR_materials_unlit'],'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0}],'meshes':[{'primitives':primitives}],'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':accessors,'materials':materials,'textures':textures,'images':images}
 jb=json.dumps(out,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4)
 glb=struct.pack('<4sII',b'glTF',2,28+len(jb)+len(binary))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(binary),b'BIN\0')+binary
 name=Path(row['path']).parent.name+'_'+Path(row['path']).stem+'.glb';(OUT/name).write_bytes(glb)
 rows.append({'file':name,'triangles':ntris,'bounds_local':bounds,'source_sha256':row['sha256']})
 if i%100==0:print('Converted',i+1,flush=True)
result={'accepted':False,'source':manifest['source'],'license':'CC0','datum_ellipsoid_candidate':datum,'road_sample_count':len(heights),'road_height_quantiles':np.percentile(heights,[0,10,50,90,100]).tolist(),'tiles':rows,'triangles':sum(r['triangles'] for r in rows),'notes':['Photogrammetry surface, not watertight architecture','No Google Earth detail parity claim before visual comparison','Z tie to approach road is conditional; no global building movement']}
(OUT/'manifest.json').write_text(json.dumps(result,indent=2));print('DONE',result['triangles'],flush=True)
