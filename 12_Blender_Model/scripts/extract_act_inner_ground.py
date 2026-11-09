"""Keep exact source ground inside the streamed clipping polygon for hybrid export."""
import sys,json,struct,copy
from pathlib import Path
R=Path(__file__).resolve().parents[1];cache=R/'.local_source_cache/act_context'
sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
import shapely
from shapely.ops import triangulate
mask=shapely.from_geojson((cache/'architecture_precise_exclusion.geojson').read_text())
out=cache/'inner_ground_glb';out.mkdir(exist_ok=True);rows=[]
report=json.loads((R/'reports/ACT2020_museum_cut_v005.json').read_text())
for row in report['changes']:
 if row['empty']:continue
 raw=(cache/'clipped_glb_v005'/row['file']).read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);blob=raw[28+n:]
 output=bytearray();views=[];accessors=[];primitives=[]
 def view(data):
  output.extend(b'\0'*((-len(output))%4));i=len(views);views.append(dict(buffer=0,byteOffset=len(output),byteLength=len(data)));output.extend(data);return i
 def acc(a,typ,component):
  i=len(accessors);d=dict(bufferView=view(a.tobytes()),componentType=component,count=len(a),type=typ)
  if typ=='VEC3':d.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
  accessors.append(d);return i
 def array(key):
  a=doc['accessors'][key];v=doc['bufferViews'][a['bufferView']];w={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']]
  return np.frombuffer(blob,dtype='<f4' if a['componentType']==5126 else '<u4',count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w)
 for p in doc['meshes'][0]['primitives']:
  vs=array(p['attributes']['POSITION']);uv=array(p['attributes']['TEXCOORD_0']);fs=array(p['indices']).reshape(-1,3);xy=vs[:,[0,2]].astype(float);xy[:,1]*=-1
  polys=shapely.polygons(xy[fs]);nv=[];nu=[];nf=[]
  for ix in np.flatnonzero(shapely.intersects(polys,mask)):
   tri=xy[fs[ix]];cross=np.linalg.det(np.column_stack((tri[1]-tri[0],tri[2]-tri[0])))
   if abs(cross)<1e-10:continue
   clipped=polys[ix].intersection(mask);parts=list(clipped.geoms) if hasattr(clipped,'geoms') else [clipped];inv=np.linalg.inv(np.column_stack((tri[1]-tri[0],tri[2]-tri[0])))
   for part in parts:
    if part.geom_type!='Polygon' or part.area<1e-10:continue
    for t in triangulate(part):
     if not part.covers(t):continue
     points=np.array(t.exterior.coords)[:3]
     if np.linalg.det(np.column_stack((points[1]-points[0],points[2]-points[0])))*cross<0:points=points[::-1]
     w=(inv@(points-tri[0]).T).T;weights=np.column_stack((1-w.sum(axis=1),w));base=len(nv);nv.extend(weights@vs[fs[ix]]);nu.extend(weights@uv[fs[ix]]);nf.append([base,base+1,base+2])
  if nf:
   p=copy.deepcopy(p);p['attributes']={'POSITION':acc(np.array(nv,dtype='<f4'),'VEC3',5126),'TEXCOORD_0':acc(np.array(nu,dtype='<f4'),'VEC2',5126)};p['indices']=acc(np.array(nf,dtype='<u4').reshape(-1,1),'SCALAR',5125);primitives.append(p)
 if not primitives:continue
 for im in doc.get('images',[]):
  v=doc['bufferViews'][im['bufferView']];im['bufferView']=view(blob[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])
 doc['meshes'][0]['primitives']=primitives;doc['bufferViews']=views;doc['accessors']=accessors;output.extend(b'\0'*((-len(output))%4));doc['buffers']=[dict(byteLength=len(output))]
 jb=json.dumps(doc,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4)
 result=struct.pack('<4sII',b'glTF',2,28+len(jb)+len(output))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(output),b'BIN\0')+output
 (out/row['file']).write_bytes(result);rows.append(dict(file=row['file'],bytes=len(result),triangles=sum(accessors[p['indices']]['count']//3 for p in primitives)))
(R/'reports/ACT2020_inner_ground_export.json').write_text(json.dumps(dict(source='v005 clipped source ground; exact intersection with streamed clipping polygon',tiles=rows,accepted=False),indent=2));print('INNER_GROUND',len(rows),sum(r['triangles'] for r in rows),flush=True)
