"""Cut source photomesh on the registered museum footprint, preserving boundary UVs.
Candidate only: scene/terrain seam acceptance is a separate step.
"""
import sys,json,struct,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'.local_source_cache/act_context/local_glb';OUT=SRC.parent/'clipped_glb';OUT.mkdir(exist_ok=True)
if '--architecture' in sys.argv:OUT=SRC.parent/'clipped_glb_v002';OUT.mkdir(exist_ok=True)
if '--preserve-ground' in sys.argv:OUT=SRC.parent/'clipped_glb_v003';OUT.mkdir(exist_ok=True)
if '--lidar-ground' in sys.argv:OUT=SRC.parent/'clipped_glb_v004';OUT.mkdir(exist_ok=True)
if '--precise-mask' in sys.argv:OUT=SRC.parent/'clipped_glb_v005';OUT.mkdir(exist_ok=True)
if '--pavilion-base' in sys.argv:OUT=SRC.parent/'clipped_glb_v006';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'.local_source_cache/gis_runtime'))
import numpy as np
import shapely
from shapely.geometry import Polygon
from shapely.ops import triangulate
if '--lidar-ground' in sys.argv:
 from scipy.interpolate import LinearNDInterpolator
 from scipy.spatial import cKDTree
 ground_samples=np.load(ROOT/'.local_source_cache/r150_ground_tin_samples.npz')['xyz']
 ground_datum=json.loads((ROOT/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m']
 ground_interp=LinearNDInterpolator(ground_samples[:,:2],ground_samples[:,2]-ground_datum)
 ground_tree=cKDTree(ground_samples[:,:2])
mask=Polygon(json.loads((SRC.parent/'mudam_exclusion.json').read_text())['polygon'])
c=json.loads((ROOT/'config/foundation.json').read_text())['calibration'];p=json.loads((ROOT/'config/pavilion_room.json').read_text())['footprint'];M=c['pdf_to_utm_matrix'];k=c['canonical_to_pdf_scale'];ox,oy=c['canonical_to_pdf_offset']
p=[(M[0][0]*(k*x+ox)+M[0][1]*(k*y+oy)+M[0][2]-293425,M[1][0]*(k*x+ox)+M[1][1]*(k*y+oy)+M[1][2]-5499960) for x,y in p]
pavilion=Polygon(p).buffer(.25,join_style='mitre')
pavilion_base=-3.831193685531616 # Current R17 wall bottom, independently read from scene.
mask=shapely.union_all([mask,Polygon(p)])
if '--architecture' in sys.argv:mask=shapely.from_geojson((SRC.parent/'architecture_exclusion.geojson').read_text())
if '--precise-mask' in sys.argv:mask=shapely.from_geojson((SRC.parent/'architecture_precise_exclusion.geojson').read_text())
manifest=json.loads((SRC/'manifest.json').read_text());changes=[]
for row in manifest['tiles']:
 bounds=np.array(row['bounds_local']);lo=bounds.min(axis=0);hi=bounds.max(axis=0);mb=mask.bounds
 if hi[0]<mb[0] or lo[0]>mb[2] or hi[1]<mb[1] or lo[1]>mb[3]:continue
 raw=(SRC/row['file']).read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);binary=bytearray(raw[28+n:]);removed=0;split=0;before=0;after=0
 def array(key):
  a=j['accessors'][key];v=j['bufferViews'][a['bufferView']];width={'VEC3':3,'VEC2':2,'SCALAR':1}[a['type']];dtype='<f4' if a['componentType']==5126 else '<u4'
  return np.frombuffer(binary,dtype=dtype,count=a['count']*width,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,width).copy()
 def replace(key,a):
  while len(binary)%4:binary.append(0)
  view=len(j['bufferViews']);j['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':a.nbytes});binary.extend(a.tobytes());ac=j['accessors'][key];ac['bufferView']=view;ac['count']=len(a)
  if ac['type']=='VEC3':ac.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
 for prim in j['meshes'][0]['primitives']:
  vk=prim['attributes']['POSITION'];uk=prim['attributes']['TEXCOORD_0'];ik=prim['indices'];vs=array(vk);uv=array(uk);fs=array(ik).reshape(-1,3);before+=len(fs);xy=vs[:,[0,2]].astype('f8');xy[:,1]*=-1
  coords=xy[fs];polys=shapely.polygons(coords);hit=shapely.intersects(polys,mask);inside=shapely.covered_by(polys,mask)
  if '--preserve-ground' in sys.argv:
   # Keep source surfaces below the road datum with a ground-like slope.
   # This is a candidate classification, not an architectural measurement.
   edges=vs[fs];normal=np.cross(edges[:,1]-edges[:,0],edges[:,2]-edges[:,0]);length=np.linalg.norm(normal,axis=1)
   ground=(edges[:,:,1].max(axis=1)<-1.0)&(np.abs(normal[:,1])>0.6*length)&(length>1e-10)
   hit &= ~ground;inside &= ~ground
  if '--lidar-ground' in sys.argv:
   terrain=ground_interp(xy);distance,nearest=ground_tree.query(xy)
   terrain=np.where(np.isfinite(terrain),terrain,ground_samples[nearest,2]-ground_datum)
   ground=(np.abs(vs[:,1]-terrain)[fs].max(axis=1)<0.6)&(distance[fs].max(axis=1)<3.0)&(vs[fs,1].max(axis=1)<-0.5)
   if '--pavilion-base' in sys.argv:ground &= ~shapely.intersects(polys,pavilion)
   hit &= ~ground;inside &= ~ground
  keep=fs[~hit].tolist();nv=vs.tolist();nu=uv.tolist();removed+=int(inside.sum())
  for ix in np.flatnonzero(hit & ~inside):
   tri=coords[ix];cross=np.linalg.det(np.column_stack((tri[1]-tri[0],tri[2]-tri[0])))
   if abs(cross)<1e-10:
    if not mask.covers(shapely.Point(tri.mean(axis=0))):keep.append(fs[ix].tolist())
    else:removed+=1
    continue
   diff=polys[ix].difference(mask);parts=list(diff.geoms) if hasattr(diff,'geoms') else [diff]
   inv=np.linalg.inv(np.column_stack((tri[1]-tri[0],tri[2]-tri[0])));split+=1
   for part in parts:
    if part.geom_type!='Polygon' or part.area<1e-10:continue
    for t in triangulate(part):
     if not part.covers(t):continue
     points=np.array(t.exterior.coords)[:3];ids=[]
     for q in points:
      w=inv@(q-tri[0]);weights=np.array([1-w.sum(),*w]);xyz=weights@vs[fs[ix]];tex=weights@uv[fs[ix]];ids.append(len(nv));nv.append(xyz.tolist());nu.append(tex.tolist())
     if np.linalg.det(np.column_stack((points[1]-points[0],points[2]-points[0])))*cross<0:ids.reverse()
     keep.append(ids)
  if '--pavilion-base' in sys.argv:
   def add_lower_polygon(points,tex):
    # Sutherland-Hodgman clipping in XYZ/UV at the inherited wall bottom.
    output=[]
    values=[np.r_[q,t] for q,t in zip(points,tex)]
    for a,b in zip(values,values[1:]+values[:1]):
     ai=a[1]<=pavilion_base;bi=b[1]<=pavilion_base
     if ai:output.append(a)
     if ai!=bi:output.append(a+(b-a)*((pavilion_base-a[1])/(b[1]-a[1])))
    if len(output)<3:return
    ids=[]
    for v in output:ids.append(len(nv));nv.append(v[:3].tolist());nu.append(v[3:].tolist())
    for i in range(1,len(ids)-1):
     a,b,c=[np.array(nv[j]) for j in (ids[0],ids[i],ids[i+1])]
     if np.linalg.norm(np.cross(b-a,c-a))>1e-10:keep.append([ids[0],ids[i],ids[i+1]])
   for ix in np.flatnonzero(shapely.intersects(polys,pavilion)&shapely.intersects(polys,mask)):
    tri=coords[ix];cross=np.linalg.det(np.column_stack((tri[1]-tri[0],tri[2]-tri[0])))
    if vs[fs[ix],1].min()>pavilion_base:continue
    if abs(cross)<1e-10:
     point=shapely.Point(tri.mean(axis=0))
     if pavilion.covers(point) and mask.covers(point):add_lower_polygon(vs[fs[ix]],uv[fs[ix]])
     continue
    clipped=polys[ix].intersection(pavilion).intersection(mask)
    parts=list(clipped.geoms) if hasattr(clipped,'geoms') else [clipped]
    inv=np.linalg.inv(np.column_stack((tri[1]-tri[0],tri[2]-tri[0])))
    for part in parts:
     if part.geom_type!='Polygon' or part.area<1e-10:continue
     for t in triangulate(part):
      if not part.covers(t):continue
      points=np.array(t.exterior.coords)[:3]
      if np.linalg.det(np.column_stack((points[1]-points[0],points[2]-points[0])))*cross<0:points=points[::-1]
      w=(inv@(points-tri[0]).T).T;weights=np.column_stack((1-w.sum(axis=1),w))
      add_lower_polygon(weights@vs[fs[ix]],weights@uv[fs[ix]])
  after+=len(keep)
  if not keep:prim['_empty']=True;continue
  replace(vk,np.array(nv,dtype='<f4'));replace(uk,np.array(nu,dtype='<f4'));replace(ik,np.array(keep,dtype='<u4').reshape(-1,1))
 if not removed and not split:continue
 j['meshes'][0]['primitives']=[p for p in j['meshes'][0]['primitives'] if not p.pop('_empty',False)]
 while len(binary)%4:binary.append(0)
 j['buffers'][0]['byteLength']=len(binary);jb=json.dumps(j,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4)
 if j['meshes'][0]['primitives']:
  (OUT/row['file']).write_bytes(struct.pack('<4sII',b'glTF',2,28+len(jb)+len(binary))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(binary),b'BIN\0')+binary)
 changes.append({'file':row['file'],'before':before,'after':after,'removed_faces':removed,'boundary_faces_split':split,'empty':not j['meshes'][0]['primitives']})
 print(row['file'],before,after,flush=True)
result={'accepted':False,'clipped_directory':OUT.name,'mask':shapely.to_geojson(mask),'mask_area':mask.area,'changes':changes,'source_meshes_unchanged_on_disk':True,'cut_method':'Exact XY polygon difference; boundary elevation and UV barycentrically interpolated; no invented terrain cap','mask_basis':'Visible architecture projections plus 0.25m candidate blending clearance; no architectural dimension changed' if '--architecture' in sys.argv else 'OSM and pavilion registered footprint','remaining':'Visual and local seam checks, own-building integration'}
if '--precise-mask' in sys.argv:result['mask_basis']='Visible architecture projections with R34 actual concave bridge boundary plus 0.25m candidate clearance; OSM museum footprint retained'
if '--lidar-ground' in sys.argv:result['ground_preservation']={'method':'Retain original source triangles matching independent LiDAR ground at all three vertices','maximum_vertical_difference_m':0.6,'maximum_nearest_source_distance_m':3.0,'maximum_road_relative_height_m':-0.5,'datum':'Both sources tied independently to the same road anchor; conditional, not surveyed building elevation','classification_accepted':False}
if '--pavilion-base' in sys.argv:result['pavilion_base_preservation']={'cut_height':pavilion_base,'basis':'Inherited R17 wall minimum Z; preserve original ACT surfaces below this plane inside the pavilion mask. No terrain elevation invented; source lower base is retained as context.','uv':'Barycentric interpolation only','accepted':False}
(ROOT/'reports/ACT2020_museum_cut_candidate.json').write_text(json.dumps(result,indent=2))
