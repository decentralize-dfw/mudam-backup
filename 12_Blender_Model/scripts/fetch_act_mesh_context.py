"""Fetch CC0 ACT 2020 full-detail photomesh leaves intersecting the Mudam context."""
import json, math, urllib.request, urllib.parse, concurrent.futures, hashlib, time
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.local_source_cache/gis_runtime'))
from pyproj import Transformer
BASE='https://acts3.geoportail.lu/3d-data/3d-tiles/mesh3D/mesh3D_2020_v2/Cesium/'
OUT=ROOT/'.local_source_cache/act_context'
OUT.mkdir(exist_ok=True)
t=Transformer.from_crs(32632,4326,always_xy=True)
corners=[t.transform(293425+x,5499960+y) for x in (-350,350) for y in (-350,450)]
B=[math.radians(min(p[0] for p in corners)),math.radians(min(p[1] for p in corners)),math.radians(max(p[0] for p in corners)),math.radians(max(p[1] for p in corners))]
def get(url):
 p=OUT/urllib.parse.urlparse(url).path.split('/Cesium/')[1]
 p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  for attempt in range(3):
   try:
    data=urllib.request.urlopen(url,timeout=60).read();p.write_bytes(data);break
   except Exception:
    if attempt==2:raise
    time.sleep(2)
 return p
def intersects(n):
 r=n.get('boundingVolume',{}).get('region')
 return not r or not(r[0]>B[2] or r[2]<B[0] or r[1]>B[3] or r[3]<B[1])
leaves=[]
def walk(n,url):
 if not intersects(n):return
 children=n.get('children',[])
 if children:
  for c in children:walk(c,url)
 else:
  uri=n.get('content',{}).get('uri')
  if not uri:return
  u=urllib.parse.urljoin(url,uri)
  if u.endswith('.json'):walk(json.loads(get(u).read_text())['root'],u)
  else:leaves.append({'url':u,'region':n['boundingVolume']['region'],'geometric_error':n.get('geometricError')})
url=BASE+'pyramid/tileset.json'
walk(json.loads(get(url).read_text())['root'],url)
print('Selected full detail leaves:',len(leaves),flush=True)
def fetch(row):
 p=get(row['url']);row.update(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest());return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 rows=[];failures=[]
 jobs={pool.submit(fetch,row):row for row in leaves}
 for job in concurrent.futures.as_completed(jobs):
  try:rows.append(job.result())
  except Exception as exc:
   failures.append({'url':jobs[job]['url'],'error':str(exc)});print('Retry later:',jobs[job]['url'],flush=True)
  if len(rows)%25==0:print('Downloaded',len(rows),flush=True)
manifest={'source':'https://data.public.lu/en/datasets/maquette-3d-du-grand-duche-de-luxembourg/','license':'CC0','capture_year':2020,'selection_local_xy':[-350,-350,350,450],'scene_origin_utm32':[293425,5499960],'leaves':rows,'selected_count':len(leaves),'failures':failures,'total_bytes':sum(r['bytes'] for r in rows),'accepted':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'leaves':len(rows),'bytes':manifest['total_bytes']}),flush=True)
