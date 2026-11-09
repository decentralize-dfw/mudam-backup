"""Clean near-site geometry from downloaded ground points, OSM and ACT reference.
The photographic mesh supplies reference heights only; no source triangles or images
are copied into the reconstructed terrain, roads, fort or historic walls.
"""
from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np,shapely,pyproj
from shapely.geometry import Polygon,LineString,Point,box
from scipy.spatial import cKDTree
from scipy.interpolate import LinearNDInterpolator
from scipy.ndimage import gaussian_filter1d
C=R/'.local_source_cache/r152';C.mkdir(exist_ok=True)
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text())
for w in ways:w['local']=(np.asarray(w['xy'])-[293425,5499960]).tolist()
fort=next(w for w in ways if w['id']=='26424184');fp=Polygon(fort['local']).buffer(0)
constraints=json.loads((C/'site_constraints.json').read_text());floors=[(Polygon(f['xy']),f['z']) for f in constraints['floors']];footprint=shapely.union_all([p for p,z in floors]);bridge=Polygon(json.loads((R/'reports/R34_build_report.json').read_text())['union_boundary'])
src=np.load(R/'references/terrain_lidar2024/mudam_classified_points.npz');v=src['xyz_luref'][src['classification']==2]
T=pyproj.Transformer.from_crs(2169,32632,always_xy=True);x,y=T.transform(v[:,0],v[:,1]);datum=json.loads((R/'.local_source_cache/r150_terrain_filtered.json').read_text())['datum_national_m'];p=np.column_stack((x-293425,y-5499960,v[:,2]-datum))
bad=shapely.contains_xy(footprint.union(fp),p[:,0],p[:,1]) | (shapely.contains_xy(bridge.buffer(.8),p[:,0],p[:,1])&(p[:,2]>-1))
p=p[~bad];_,ids=np.unique(np.floor(p[:,:2]/.5).astype(int),axis=0,return_index=True);p=p[ids];tree=cKDTree(p[:,:2]);interp=LinearNDInterpolator(p[:,:2],p[:,2])
def height(xy):
 xy=np.atleast_2d(xy);z=interp(xy);dist,ids=tree.query(xy);return np.where(np.isfinite(z),z,p[ids,2])
act=np.load(C/'site_reference_points.npz')['xyz'];at=cKDTree(act[:,:2])
def surface_height(xy,k=30,q=.75):
 d,ids=at.query(np.atleast_2d(xy),k=k);return np.quantile(act[ids,2],q,axis=1)

domain=box(-89,-98,98,108);meshes=[]
def triangulated(name,pol,mat,spacing=1.5,zfun=height):
 pol=shapely.make_valid(pol.intersection(domain))
 if pol.is_empty:return
 vs=[];fs=[];lookup={}
 def vi(q):
  key=tuple(np.round(q,6))
  if key not in lookup:lookup[key]=len(vs);vs.append(key)
  return lookup[key]
 x0,y0,x1,y1=pol.bounds
 for x in np.arange(math.floor(x0/spacing)*spacing,x1,spacing):
  for y in np.arange(math.floor(y0/spacing)*spacing,y1,spacing):
   part=pol.intersection(box(x,y,x+spacing,y+spacing))
   if part.is_empty or part.area<1e-8:continue
   for t in shapely.constrained_delaunay_triangles(part).geoms:
    if t.area<1e-8:continue
    q=np.array(t.exterior.coords)[:3]
    if np.linalg.det(np.column_stack((q[1]-q[0],q[2]-q[0])))<0:q=q[::-1]
    fs.append([vi(c) for c in q])
 if not fs:return
 xy=np.array(vs);z=zfun(xy);meshes.append(dict(name=name,material=mat,vertices=np.column_stack((xy,z)).tolist(),faces=fs))

# Drape separate path strips, using tagged widths where supplied. The widths
# without tags are explicitly recorded presentation candidates.
roads=[];widths=[]
for w in ways:
 tags=w['tags'];h=tags.get('highway');xy=np.asarray(w['local'])
 if not h or h in ('steps','proposed','construction') or tags.get('bridge')=='yes' or len(xy)<2:continue
 line=LineString(xy)
 if not line.intersects(domain) or line.length<1:continue
 try:width=float(tags['width'].replace('m','').strip());assumed=False
 except (KeyError,ValueError):width=3 if h in ('path','footway','pedestrian','cycleway','track') else 5.5;assumed=True
 pol=line.buffer(width/2,cap_style='flat',join_style='round').intersection(domain).difference(footprint.buffer(.05)).difference(fp).difference(bridge.buffer(.05))
 if pol.area<.5:continue
 occupied=shapely.union_all(roads) if roads else Polygon();roads.append(pol);pol=pol.difference(occupied);widths.append(dict(osm=w['id'],width=width,assumed=assumed))
 road=tags.get('surface','');mat='gravel' if road in ('gravel','fine_gravel','ground','compacted') or h in ('path','track') else 'paving'
 triangulated('R152_PATH_'+w['id'],pol,mat,1.5,lambda xy:height(xy)+.025)
# Broad paved approaches are visible in the ACT orthographic reference; road
# center lines alone would incorrectly leave these forecourts as grass.
for pi,pixels in enumerate([[(383,344),(590,316),(603,401),(562,420),(479,502),(428,492),(400,415)],[(779,167),(906,178),(915,319),(801,324),(799,250)],[(904,413),(1014,429),(1028,568),(978,598),(959,524),(905,513)]]):
 pixels=np.asarray(pixels);xy=np.column_stack(((pixels[:,0]-700)*260/1400,-10-(pixels[:,1]-700)*260/1400));pol=Polygon(xy).difference(footprint.buffer(.05)).difference(fp).difference(bridge.buffer(.05)).difference(shapely.union_all(roads));roads.append(pol);triangulated('R152_FORECOURT_%d'%pi,pol,'paving',1.5,lambda xy:height(xy)+.025)
paths=shapely.union_all(roads)
# Keep genuine sunken moats. Under-floor terrain is capped below the lowest
# existing floor; no flat plate across bridges or basement openings.
def ground(xy):
 z=height(xy)
 for pol,cap in floors:
  sel=shapely.intersects_xy(pol.buffer(2.2),xy[:,0],xy[:,1]);z[sel]=np.minimum(z[sel],cap)
 return z
triangulated('R152_CLASS2_TERRAIN',domain.difference(paths).difference(fp), 'grass',1.5,ground)

# Historic wall centerlines stay on the mapped traces. Top profiles are sampled
# locally from ACT, smoothed, and bounded above adjacent classified ground.
wallinfo=[]
for w in ways:
 tags=w['tags'];xy=np.asarray(w['local'])
 if tags.get('barrier') not in ('city_wall','retaining_wall') or len(xy)<2 or w['id']=='51946353':continue
 line=LineString(xy)
 if not domain.buffer(-2).contains(line) or line.intersects(footprint.buffer(-.5)):continue
 width=.9;coords=[]
 for a,b in zip(xy[:-1],xy[1:]):coords.extend(a+(b-a)*t for t in np.linspace(0,1,max(2,int(np.linalg.norm(b-a)/1)+1))[:-1])
 coords=np.vstack((coords,xy[-1]));n=np.gradient(coords,axis=0);n=np.column_stack((-n[:,1],n[:,0]));n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-8)
 left=coords+n*width/2;right=coords-n*width/2;glo=height(left+n*.4);gro=height(right-n*.4);bottom=np.minimum(glo,gro)-.25;raw=surface_height(coords,k=35,q=.45)
 # Retaining walls terminate at the upper terrain edge. Tree canopies above
 # that edge are not wall heights. Ruin profiles use a robust lower surface
 # sample and suppress isolated canopy spikes along the mapped wall.
 upper=np.maximum(glo,gro)
 if tags.get('barrier')=='retaining_wall':top=gaussian_filter1d(upper,.8)+.12
 else:
  profile=gaussian_filter1d(raw,1.5);extra=np.maximum(0,profile-upper);ceiling=float(np.quantile(extra,.35))+.35;top=upper+np.minimum(extra,ceiling);top=np.maximum(top,upper+.15)
 vs=[];faces=[]
 for a,b,z0,z1 in zip(left,right,bottom,top):vs.extend([[*a,z0],[*b,z0],[*b,z1],[*a,z1]])
 for i in range(len(coords)-1):
  k=i*4
  for j in range(4):faces.append([k+j,k+(j+1)%4,k+4+(j+1)%4,k+4+j])
 faces.extend([[3,2,1,0],[4*(len(coords)-1)+j for j in range(4)]])
 meshes.append(dict(name='R152_HISTORIC_WALL_'+w['id'],material='stone',vertices=vs,faces=faces));wallinfo.append(dict(osm=w['id'],width_candidate_m=width,points=len(coords),raw_range=[float(raw.min()),float(raw.max())]))

# Fort Thüngen: mapped perimeter, clean walls and roof; three independent
# circular towers read from ACT orthographic view, with source-derived heights.
roofxy=np.asarray(fp.exterior.coords)[:-1];zbase=height(roofxy)-.25;ztop=np.full(len(roofxy),2.9);n=len(roofxy)
vs=np.vstack((np.column_stack((roofxy,zbase)),np.column_stack((roofxy,ztop)))).tolist();fs=[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
meshes.append(dict(name='R152_FORT_THUNGEN_WALLS',material='stone',vertices=vs,faces=fs))
triangulated('R152_FORT_TURF_ROOF',fp,'grass',1.5,lambda xy:np.full(len(xy),2.9))
# The modern inset metal roof is traced separately from the source top view.
def ortho(px):
 px=np.asarray(px);return np.column_stack(((px[:,0]-700)*260/1400,-10-(px[:,1]-700)*260/1400))
metal=Polygon(ortho([(352,913),(356,884),(428,841),(488,790),(499,739),(529,721),(578,741),(578,782),(568,805),(545,805),(530,796),(495,815),(447,856),(398,896),(373,920)]))
triangulated('R152_FORT_INSET_METAL_ROOF',metal,'zinc',1.5,lambda xy:np.full(len(xy),3.02))
towers=[]
for name,xy,r in [('WEST',[-71.5,-47.6],4.5),('CENTRE',[-61.6,-53.15],2.8),('SOUTH',[-57.4,-63.1],4.5)]:
 rim=np.array(xy)+np.column_stack((np.cos(np.arange(64)*2*np.pi/64),np.sin(np.arange(64)*2*np.pi/64)))*r;base=float(np.quantile(height(rim),.1))-.25;roof=float(np.median(surface_height(rim*.6+np.array(xy)*.4,k=18,q=.9)))-.2;towers.append(dict(name=name,center=xy,radius=r,base=base,roof=roof))
# Internal masonry traces visible in the downloaded ACT orthographic reference.
# These short partitions are absent from the OSM perimeter lines.
ruins=[[(430,279),(544,226),(592,310)],[(443,288),(547,239),(578,309)],[(453,269),(464,287)],[(477,258),(488,275)],[(500,247),(511,264)],[(526,237),(538,256)],[(549,259),(568,250)],[(558,277),(578,269)],[(567,295),(588,286)],[(450,307),(471,285),(497,296)],[(981,733),(1080,773),(1060,838),(1011,900)],[(982,751),(1059,781),(1045,829),(1002,880)],[(998,756),(991,776)],[(1018,764),(1010,789)],[(1040,773),(1031,799)],[(1054,798),(1031,790)],[(1048,821),(1023,810)],[(1038,841),(1016,832)],[(1025,861),(1006,851)]]
for ri,trace in enumerate(ruins):
 coords=ortho(trace);normal=np.gradient(coords,axis=0);normal=np.column_stack((-normal[:,1],normal[:,0]));normal/=np.linalg.norm(normal,axis=1)[:,None];left=coords+normal*.35;right=coords-normal*.35;bottom=np.minimum(height(left),height(right))-.2;top=surface_height(coords,k=24,q=.85);top=np.maximum(top,bottom+.25);vs=[];fs=[]
 for a,b,z0,z1 in zip(left,right,bottom,top):vs.extend([[*a,z0],[*b,z0],[*b,z1],[*a,z1]])
 for i in range(len(coords)-1):
  k=i*4
  for j in range(4):fs.append([k+j,k+(j+1)%4,k+4+(j+1)%4,k+4+j])
 fs.extend([[3,2,1,0],[4*(len(coords)-1)+j for j in range(4)]])
 meshes.append(dict(name='R152_RUIN_PARTITION_%02d'%ri,material='stone',vertices=vs,faces=fs))
# The narrow fort entrance bridge is visible between the western approach and
# the central tower. Trace the deck independently from the sunken ground.
ab=ortho([(283,973),(356,930)]);direction=ab[1]-ab[0];normal=np.array([-direction[1],direction[0]])/np.linalg.norm(direction);deck=Polygon([ab[0]+normal*1.25,ab[1]+normal*1.25,ab[1]-normal*1.25,ab[0]-normal*1.25]);deckz=np.array([surface_height([ab[0]],k=20,q=.75)[0],surface_height([ab[0]+direction*.8],k=20,q=.9)[0]])
def bridgeheight(xy):
 t=np.clip((xy-ab[0])@direction/(direction@direction),0,1);return deckz[0]+t*(deckz[1]-deckz[0])
triangulated('R152_FORT_ENTRANCE_BRIDGE',deck,'paving',.8,bridgeheight)
edge=np.array(deck.exterior.coords)[:-1];dz=bridgeheight(edge);meshes.append(dict(name='R152_FORT_BRIDGE_EDGE',material='stone',vertices=np.vstack((np.column_stack((edge,dz-.25)),np.column_stack((edge,dz)))).tolist(),faces=[[i,(i+1)%4,(i+1)%4+4,i+4]for i in range(4)]+[[3,2,1,0]]))
# Independent vegetation returns identify canopy peaks, not invented tree rows.
from scipy.ndimage import maximum_filter,gaussian_filter
veg=src['xyz_luref'][src['classification']==5];vx,vy=T.transform(veg[:,0],veg[:,1]);veg=np.column_stack((vx-293425,vy-5499960,veg[:,2]-datum));can=np.full((208,190),-100.,dtype=float);ix=np.floor(veg[:,0]+90).astype(int);iy=np.floor(veg[:,1]+99).astype(int);valid=(ix>=0)&(ix<190)&(iy>=0)&(iy<208);np.maximum.at(can,(iy[valid],ix[valid]),veg[valid,2]);can[can<-90]=0;sm=gaussian_filter(can,1);peak=(sm==maximum_filter(sm,size=7))&(sm>0);yy,xx=np.where(peak);trees=[]
for x,y in zip(xx-89.5,yy-98.5):
 q=Point(x,y)
 if not domain.contains(q) or footprint.buffer(3).contains(q) or fp.buffer(2).contains(q) or paths.buffer(1).contains(q) or bridge.contains(q):continue
 z=float(height([[x,y]])[0]);h=float(sm[int(round(y+98.5)),int(round(x+89.5))]-z)
 if h<5 or h>26:continue
 trees.append(dict(x=float(x),y=float(y),z=z,height=h,radius=min(5.5,max(2,h*.23))))
result=dict(meshes=meshes,towers=towers,trees=trees,wall_profiles=wallinfo,path_widths=widths,datum=datum,source_ground_points=len(p),ground_coverage=[list(domain.bounds)],scope='Near-site reconstruction; no photographic source mesh used',limits=['Ground uses classified LiDAR 2024, locally interpolated across excluded decks and buildings.','Absolute vertical tie remains the inherited road anchor candidate.','Wall thicknesses and untagged path widths are presentation estimates, not surveyed dimensions.','Historic wall top profiles from 2020 ACT photogrammetry need local visual review.','Fort roof simplified from downloaded reference; facade openings not yet reconstructed.','Canopy peaks indicate approximate trees, not an individual-tree survey.'])
(C/'clean_site.json').write_text(json.dumps(result));np.savez_compressed(C/'ground_samples.npz',xyz=p)
print('R152_SITE_PREPARED',len(meshes),sum(len(m['faces']) for m in meshes),len(wallinfo),len(widths),towers,flush=True)

