"""Read only intersecting COPC chunks inside uncompressed ZIP members using HTTP ranges."""
from pathlib import Path
import sys,io,json,urllib.request,struct,hashlib,datetime
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'.local_source_cache/gis_runtime'))
import numpy as np
from laspy import CopcReader
from laspy.copc import Bounds
r=json.loads((B/'references/terrain_lidar2024/tile_archive_resource.json').read_text());idx=json.loads((B/'references/terrain_lidar2024/tile_archive_index.json').read_text());bounds=Bounds(np.array([77877.,75700.,200.]),np.array([78075.,75917.,400.]));downloaded=0

def get(start,n):
 global downloaded
 if n>4_000_000:
  from concurrent.futures import ThreadPoolExecutor
  jobs=[(start+i,min(4_000_000,n-i)) for i in range(0,n,4_000_000)]
  with ThreadPoolExecutor(max_workers=4) as pool:return b''.join(pool.map(lambda pair:get(*pair),jobs))
 cache=B/'.local_source_cache/lidar_ranges';cache.mkdir(exist_ok=True);p=cache/f'{start}_{n}.bin'
 if p.exists() and p.stat().st_size==n:return p.read_bytes()
 for attempt in range(3):
  try:
   req=urllib.request.Request(r['url'],headers={'Range':f'bytes={start}-{start+n-1}'})
   with urllib.request.urlopen(req,timeout=45) as f:
    assert f.status==206;data=f.read();assert len(data)==n
   p.write_bytes(data);downloaded+=len(data);assert downloaded<400_000_000;return data
  except Exception:
   if attempt==2:raise
class Member(io.RawIOBase):
 def __init__(self,item):
  h=get(item['offset'],30);assert h[:4]==b'PK\x03\x04';n,e=struct.unpack_from('<HH',h,26);assert struct.unpack_from('<H',h,8)[0]==0;self.base=item['offset']+30+n+e;self.size=item['size'];self.pos=0
 def readinto(self,buffer):
  data=self.read(len(buffer));buffer[:len(data)]=data;return len(data)
 def seek(self,offset,whence=0):self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset;return self.pos
 def tell(self):return self.pos
 def read(self,n=-1):
  if n<0:n=self.size-self.pos
  n=min(n,self.size-self.pos)
  if n<=0:return b''
  data=get(self.base+self.pos,n);self.pos+=n;return data
rows=[];parts=[]
for name in ['77500_76000.laz','78000_76000.laz']:
 item=next(i for i in idx if i['name']==name)
 with CopcReader(Member(item)) as reader:
  local_bounds=Bounds(np.maximum(bounds.mins,reader.header.mins),np.minimum(bounds.maxs,reader.header.maxs));print(dict(member=name,scales=reader.header.scales.tolist(),offsets=reader.header.offsets.tolist(),mins=local_bounds.mins.tolist(),maxs=local_bounds.maxs.tolist()),flush=True)
  points=reader.query(bounds=local_bounds);xyz=np.column_stack((np.asarray(points.x),np.asarray(points.y),np.asarray(points.z)));classes=np.asarray(points.classification);parts.append((xyz,classes));u,c=np.unique(classes,return_counts=True);rows.append(dict(member=name,points=len(points),classes=dict(zip(map(str,u.tolist()),c.tolist())),crs=str(reader.header.parse_crs())));print(rows[-1],flush=True)
assert all(len(x)>0 for x,c in parts),'Empty crop is not a valid source receipt'
xyz=np.concatenate([x for x,c in parts]);classes=np.concatenate([c for x,c in parts]);out=B/'references/terrain_lidar2024/mudam_classified_points.npz';np.savez_compressed(out,xyz_luref=xyz,classification=classes)
receipt=dict(url=r['url'],resource_id=r['id'],archive_size=r['filesize'],downloaded_range_bytes=downloaded,query_bounds_luref=[77877,75700,78075,75917],tiles=rows,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),license='cc-zero',classification_source='ACT dataset description: class2 ground, class13 bridge',full_archive_checksum_verified=False)
(out.parent/'points_manifest.json').write_text(json.dumps(receipt,indent=2)+'\n');print('DOWNLOAD_BYTES',downloaded,'POINTS',len(xyz),flush=True)
