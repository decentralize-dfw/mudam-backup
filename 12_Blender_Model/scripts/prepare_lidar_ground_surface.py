from pathlib import Path
import sys,json,hashlib
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'.local_source_cache/gis_runtime'))
import numpy as np,pyproj,shapely
from shapely.geometry import Polygon
from scipy.spatial import cKDTree
from scipy.interpolate import LinearNDInterpolator
src=B/'references/terrain_lidar2024/mudam_classified_points.npz';m=json.loads(src.with_name('points_manifest.json').read_text());assert hashlib.sha256(src.read_bytes()).hexdigest()==m['sha256'];p=np.load(src);v=p['xyz_luref'];cls=p['classification'];v=v[cls==2];T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);xyz=np.column_stack((x-293425,y-5499960,v[:,2]));old=json.loads((B/'.local_source_cache/r150_terrain_mesh.json').read_text());datum=old['datum_national_m'];bridge=Polygon(json.loads((B/'reports/R34_build_report.json').read_text())['union_boundary']);zones=[Polygon(json.loads((B/'config'/f).read_text())[key]) for f,key in [('site_moat.json','moat_polygon'),('pavilion_moat.json','polygon')]];region=shapely.union_all(zones).buffer(3);xyz=xyz[shapely.contains_xy(region,xyz[:,0],xyz[:,1])];mask=shapely.contains_xy(bridge.buffer(.8),xyz[:,0],xyz[:,1])&(xyz[:,2]>datum-1);excluded=int(mask.sum());xyz=xyz[~mask]
# At most one median source point per 0.25m XY cell: retain small slopes without duplicate returns.
keys=np.floor(xyz[:,:2]/.25).astype(int);_,ids=np.unique(keys,axis=0,return_inverse=True);sort=np.argsort(ids);groups=np.split(sort,np.flatnonzero(np.diff(ids[sort]))+1);samples=np.array([np.median(xyz[g],axis=0) for g in groups]);interp=LinearNDInterpolator(samples[:,:2],samples[:,2]);tree=cKDTree(samples[:,:2]);rows=[]
for row in old['surfaces']:
 xy=np.array(row['vertices'])[:,:2];z=interp(xy);distance,idx=tree.query(xy);missing=~np.isfinite(z);z[missing]=samples[idx[missing],2];row['vertices']=np.column_stack((xy,z-datum)).tolist();row['z_min']=float(z.min()-datum);row['z_max']=float(z.max()-datum);row['nearest_source_distance_m']=distance.tolist();rows.append(dict(name=row['name'],vertices=len(z),nearest_distance_quantiles=np.quantile(distance,[0,.5,.9,.99,1]).tolist(),outside_convex_hull=int(missing.sum()),under_bridge=int(shapely.contains_xy(bridge,xy[:,0],xy[:,1]).sum()),under_bridge_zmax=float((z-datum)[shapely.contains_xy(bridge,xy[:,0],xy[:,1])].max()) if shapely.contains_xy(bridge,xy[:,0],xy[:,1]).any() else None))
old.update(source=src.relative_to(B.parent).as_posix(),source_sha256=m['sha256'],terrain_method='Class2 points; bridge footprint +0.8m and z>datum-1m removed; .25m median cells; linear TIN interpolation',excluded_deck_points=excluded,interpolation_samples=len(samples),coverage=rows,construction_acceptance=False)
(B/'.local_source_cache/r150_terrain_filtered.json').write_text(json.dumps(old,indent=2)+'\n');(B/'reports/R150_point_terrain_coverage.json').write_text(json.dumps({k:v for k,v in old.items() if k!='surfaces'},indent=2)+'\n');np.savez_compressed(B/'.local_source_cache/r150_ground_tin_samples.npz',xyz=samples);print(json.dumps(dict(excluded=excluded,samples=len(samples),coverage=rows),indent=2))

# Derive wall bottom extensions against the newly triangulated candidate surface.
mesh_vertices=np.array([v for row in old['surfaces'] for v in row['vertices']]);surface=LinearNDInterpolator(mesh_vertices[:,:2],mesh_vertices[:,2]);surface_tree=cKDTree(mesh_vertices[:,:2]);extensions=[]
for wall in json.loads((B/'.local_source_cache/r150_existing_wall_meshes.json').read_text()):
 vertices=np.array(wall['vertices']);base=float(vertices[:,2].min());bottom=vertices[np.abs(vertices[:,2]-base)<1e-4];xy=[]
 for a in bottom:
  for b in bottom:
   length=np.linalg.norm(b[:2]-a[:2])
   if 0<length<90:
    xy.extend([(a*(1-t)+b*t)[:2] for t in np.linspace(0,1,max(2,int(length*2)+1))])
 xy=np.array(xy);z=surface(xy);dist,idx=surface_tree.query(xy);missing=~np.isfinite(z);z[missing]=mesh_vertices[idx[missing],2];new=min(base,float(z.min())-.25)
 if new<base-.001:extensions.append(dict(name=wall['name'],old_base=base,new_base=new,samples=len(z),terrain_min=float(z.min()),nearest_surface_max_distance=float(dist.max()),method='Only extend existing lowest vertices below adjacent candidate terrain; preserve heads/openings. .25m embed is inherited thickness, not surveyed foundation.'))
old['wall_base_extensions']=extensions
(B/'.local_source_cache/r150_terrain_filtered.json').write_text(json.dumps(old,indent=2)+'\n')
