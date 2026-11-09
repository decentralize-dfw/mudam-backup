from pathlib import Path
import sys,json,struct,gzip,hashlib,copy
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely
from shapely.geometry import Polygon
from shapely.ops import triangulate
cache=R/'.local_source_cache/act_context';mask=shapely.from_geojson((cache/'architecture_precise_exclusion.geojson').read_text())
pav=json.loads((R/'reports/R151_pavilion_registration_candidate.json').read_text())['old'];pav=Polygon([(x+1.5801740961,y-.2937927484) for x,y in pav]).buffer(.25,join_style='mitre');mask=shapely.union_all([mask,pav]);(R/'reports/R151_WEB_CLEAN_mask.geojson').write_text(shapely.to_geojson(mask))
# Include the CURRENT exported building projection, not only the old registration mask.
br=(R/'exports/r151_web_v002/building.glb').read_bytes();bn=struct.unpack_from('<I',br,12)[0];bd=json.loads(br[20:20+bn]);bb=br[28+bn:]
def ba(k):
 a=bd['accessors'][k];v=bd['bufferViews'][a['bufferView']];w={'VEC3':3,'VEC2':2,'SCALAR':1,'VEC4':4}[a['type']];return np.frombuffer(bb,dtype='<f4' if a['componentType']==5126 else '<u4',count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w)
parts=[]
for bm in bd['meshes']:
 for bp in bm['primitives']:
  v=ba(bp['attributes']['POSITION']);f=ba(bp['indices']).reshape(-1,3);xy=v[:,[0,2]].astype(float);xy[:,1]*=-1;polys=shapely.polygons(xy[f]);polys=polys[shapely.area(polys)>.001]
  if len(polys):parts.append(shapely.union_all(polys,grid_size=.005))
actual=shapely.union_all(parts,grid_size=.005).buffer(.12,join_style='mitre');mask=shapely.union_all([mask,actual]);(R/'reports/R151_WEB_CLEAN_mask.geojson').write_text(shapely.to_geojson(mask));print('ACTUAL_MASK',mask.area,flush=True)

src=R/'exports/r151_web_v002/near_context.glb';raw=src.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);blob=raw[28+n:];out=bytearray();views=[];acs=[];rows=[]
def arr(k):
 a=d['accessors'][k];v=d['bufferViews'][a['bufferView']];w={'VEC3':3,'VEC2':2,'SCALAR':1,'VEC4':4}[a['type']];return np.frombuffer(blob,dtype='<f4' if a['componentType']==5126 else '<u4',count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w).copy()
def view(b):
 out.extend(b'\0'*(-len(out)%4));i=len(views);views.append(dict(buffer=0,byteOffset=len(out),byteLength=len(b)));out.extend(b);return i
def acc(a,typ,ct):
 q=dict(bufferView=view(a.tobytes()),componentType=ct,type=typ,count=len(a));i=len(acs)
 if typ=='VEC3':q.update(min=a.min(0).tolist(),max=a.max(0).tolist())
 acs.append(q);return i
new=[];remaining=0
for p in d['meshes'][0]['primitives']:
 vs=arr(p['attributes']['POSITION']);uv=arr(p['attributes']['TEXCOORD_0']);fs=arr(p['indices']).reshape(-1,3);xy=vs[:,[0,2]].astype(float);xy[:,1]*=-1;coords=xy[fs];polys=shapely.polygons(coords);masks=np.where(vs[fs,1].max(axis=1)>-1.0,mask.buffer(1.0,join_style='mitre'),mask);hit=shapely.intersects(polys,masks);inside=shapely.covered_by(polys,masks);nv=vs.tolist();nu=uv.tolist();keep=fs[~hit].tolist()
 for ix in np.flatnonzero(hit & ~inside):
  tri=coords[ix];cross=np.linalg.det(np.column_stack((tri[1]-tri[0],tri[2]-tri[0])))
  if abs(cross)<1e-10:continue
  diff=polys[ix].difference(masks[ix]);inv=np.linalg.inv(np.column_stack((tri[1]-tri[0],tri[2]-tri[0])))
  for part in (list(diff.geoms) if hasattr(diff,'geoms') else [diff]):
   if part.geom_type!='Polygon' or part.area<1e-9:continue
   for t in triangulate(part):
    if not part.covers(t):continue
    q=np.array(t.exterior.coords)[:3]
    if np.linalg.det(np.column_stack((q[1]-q[0],q[2]-q[0])))*cross<0:q=q[::-1]
    w=(inv@(q-tri[0]).T).T;weights=np.column_stack((1-w.sum(1),w));base=len(nv);nv.extend(weights@vs[fs[ix]]);nu.extend(weights@uv[fs[ix]]);keep.append([base,base+1,base+2])
 if keep:
  ids=np.array(keep,dtype='<u4');used,rev=np.unique(ids,return_inverse=True);v=np.array(nv,dtype='<f4')[used];u=np.array(nu,dtype='<f4')[used];ids=rev.astype('<u4').reshape(-1,3)
  # Independent area intersection with inset mask tolerates float32 boundary rounding only.
  checkxy=v[:,[0,2]].astype(float);checkxy[:,1]*=-1;over=shapely.intersection(shapely.polygons(checkxy[ids]),mask.buffer(-.002));remaining+=int((shapely.area(over)>1e-8).sum())
  new.append(dict(attributes={'POSITION':acc(v,'VEC3',5126),'TEXCOORD_0':acc(u,'VEC2',5126)},indices=acc(ids.reshape(-1,1),'SCALAR',5125),material=p['material'],mode=4))
 rows.append(dict(material=p['material'],before=len(fs),after=len(keep),affected=int(hit.sum())))
assert remaining==0,remaining
for im in d['images']:
 v=d['bufferViews'][im['bufferView']];im['bufferView']=view(blob[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])
d['meshes'][0]['primitives']=new;d['bufferViews']=views;d['accessors']=acs;out.extend(b'\0'*(-len(out)%4));d['buffers']=[dict(byteLength=len(out))];jb=json.dumps(d,separators=(',',':')).encode();jb+=b' '*(-len(jb)%4);b=struct.pack('<4sII',b'glTF',2,28+len(jb)+len(out))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(out),b'BIN\0')+out
folder=R/'exports/r151_web_clean';folder.mkdir(exist_ok=True);target=folder/'near_context.glb';target.write_bytes(b);gz=gzip.compress(b,compresslevel=9,mtime=0);Path(str(target)+'.gz').write_bytes(gz)
m=json.loads((R/'config/r151_web_lod.json').read_text());(R/'reports/R151_WEB_before_clean_manifest.json').write_text(json.dumps(m,indent=2))
for l in m['layers']:
 if l['key']=='near_context':l.update(url='../exports/r151_web_clean/near_context.glb.gz',bytes=len(b),gzip_bytes=len(gz),sha256=hashlib.sha256(b).hexdigest(),triangles=sum(x['after'] for x in rows))
m['revision']='R151 WEB CLEAN v001';(R/'config/r151_web_lod.json').write_text(json.dumps(m,indent=2));report=dict(affected_triangles=sum(x['affected'] for x in rows),removed_net=sum(x['before']-x['after'] for x in rows),remaining_inside_inset_mask=remaining,building_layer_unchanged=True,texture_bytes_unchanged=True,rows=rows);(R/'reports/R151_WEB_CLEAN.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='rows'})
