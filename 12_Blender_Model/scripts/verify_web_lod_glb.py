"""Independent GLB, accessor, image and retained triangle-count checks."""
import json,struct,sys,io,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
DT={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};W={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def read(p):
 raw=Path(p).read_bytes();assert struct.unpack_from('<4sII',raw)==(b'glTF',2,len(raw));n,kind=struct.unpack_from('<I4s',raw,12);assert kind==b'JSON';d=json.loads(raw[20:20+n]);size,kind=struct.unpack_from('<I4s',raw,20+n);assert kind==b'BIN\0' and size==len(raw)-28-n;return d,raw[28+n:]
def verify(p):
 d,b=read(p);stats=json.loads(Path(str(p)+'.json').read_text());source,sb=read(stats['source']);arrays=[]
 for a in d['accessors']:
  v=d['bufferViews'][a['bufferView']];dt=np.dtype(DT[a['componentType']]);w=W[a['type']];stride=v.get('byteStride',w*dt.itemsize);offset=a.get('byteOffset',0);assert offset+max(0,a['count']-1)*stride+w*dt.itemsize<=v['byteLength'];arr=np.ndarray((a['count'],w),dt,buffer=b,offset=v.get('byteOffset',0)+offset,strides=(stride,dt.itemsize));assert np.isfinite(arr).all();arrays.append(arr)
 triangles=0
 for mesh in d['meshes']:
  for primitive in mesh['primitives']:
   positions=arrays[primitive['attributes']['POSITION']];ids=arrays[primitive['indices']];assert ids.max()<len(positions) and ids.size%3==0;triangles+=ids.size//3
   for a in primitive['attributes'].values():assert len(arrays[a])==len(positions)
 assert triangles==stats['triangles']
 images=[]
 for i,im in enumerate(d['images']):
  v=d['bufferViews'][im['bufferView']];payload=b[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];sv=source['bufferViews'][source['images'][i]['bufferView']];original=sb[sv.get('byteOffset',0):sv.get('byteOffset',0)+sv['byteLength']];assert payload==original
  image=Image.open(io.BytesIO(payload));image.verify();images.append(dict(bytes=len(payload),size=list(Image.open(io.BytesIO(payload)).size)))
 assert len(images)==len(source['images'])
 report=dict(file=str(p),triangles=triangles,draw_primitives=sum(len(m['primitives']) for m in d['meshes']),images=images,geometry_accessors_finite=True,indices_in_bounds=True,image_payloads_identical_to_unbatched=True,failures=[])
 Path(str(p)+'.verification.json').write_text(json.dumps(report,indent=2));print('GLB_VERIFIED',Path(p).name,triangles,len(images),flush=True)
if __name__=='__main__':verify(sys.argv[1])
