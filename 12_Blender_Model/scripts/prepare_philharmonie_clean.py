"""Trace the architectural plan and registered ACT reference; no photo mesh in output."""
from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree
from scipy.interpolate import CubicSpline
from shapely.geometry import Polygon,Point
from shapely import contains_xy

# Coordinates below are in the 1632px wide displayed architect's N3 plan.
outline=np.array([(97,630),(240,544),(400,461),(550,401),(700,361),(840,344),(980,359),(1110,397),(1230,458),(1340,546),(1420,652),(1496,830),(1400,946),(1270,1049),(1110,1119),(930,1168),(760,1177),(620,1155),(515,1110),(432,1040),(354,934),(281,818),(200,691),(138,684)],float)
poly=Polygon(outline)
im=np.asarray(Image.open(R/'references/philharmonie/architect_plan_n3.webp').convert('L').resize((1632,1522)))
lab,n=ndimage.label(im<90);obj=ndimage.find_objects(lab);cols=[]
for i,s in enumerate(obj,1):
 if s is None:continue
 h=s[0].stop-s[0].start;w=s[1].stop-s[1].start
 if not(2<=h<=7 and 2<=w<=7 and .5<h/w<2):continue
 yy,xx=np.where(lab[s]==i);area=len(xx)
 if area<4 or area>36:continue
 p=np.array([s[1].start+xx.mean(),s[0].start+yy.mean()])
 if poly.contains(Point(p)) and poly.exterior.distance(Point(p))<60:cols.append(p)

# Plan north/south pointed ends tied to the 150m ACT orthographic reference.
pa=np.array([97.,630.]);pb=np.array([1496.,830.])
qa=np.array([215.535714,229.142857]);qb=np.array([148.678571,121.25])
v=pb-pa;v[1]*=-1;w=qb-qa
scale=np.linalg.norm(w)/np.linalg.norm(v);a=math.atan2(w[1],w[0])-math.atan2(v[1],v[0]);rot=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def world(p):
 p=np.asarray(p)-pa;p=p*np.array([1,-1]);return p@rot.T*scale+qa
def smooth(points,n=256):
 p=np.asarray(points);p=np.vstack((p,p[0]));t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];return CubicSpline(t,p,bc_type='periodic')(np.linspace(0,t[-1],n,endpoint=False))

# Roof / skylight traces in the registered source top view (1400px = 150m).
def act(p):
 p=np.asarray(p);return np.column_stack((185+(p[:,0]-700)*150/1400,170-(p[:,1]-700)*150/1400))
roof=act(smooth([(985,148),(1021,300),(1036,460),(1025,610),(992,750),(930,902),(834,1014),(725,1094),(590,1149),(460,1164),(361,1155),(320,986),(292,850),(286,710),(313,575),(376,448),(473,342),(600,272),(746,218),(866,181)]))
sky=act(smooth([(696,313),(779,335),(841,408),(872,492),(854,609),(813,726),(763,853),(688,989),(604,1050),(510,1050),(426,1002),(381,920),(373,824),(399,722),(451,610),(503,490),(567,377),(628,325)],192))
# Keep the roof tied to the same architectural outline as the columns.
# ACT facade reconstruction drifts locally; retain its trace for comparison.
act_roof=roof.copy()
roof=np.asarray(Polygon(world(smooth(outline,512))).buffer(.6).exterior.coords)[:-1]
core=sky.mean(0)+(sky-sky.mean(0))*.82
points=np.load(R/'.local_source_cache/r152/philharmonie_reference_points.npz')['xyz']
inside=contains_xy(Polygon(roof),points[:,0],points[:,1]);z=points[inside,2]
roof_z=float(np.median(z[(z>28)&(z<34)]));base=roof_z-20.5

# Curved side shells: sampled source heights, regularized on a new radial mesh.
petals=[]
for name,trace in [('chamber',[(1054,645),(1093,739),(1135,853),(1148,980),(1120,1091),(1057,1161),(954,1186),(840,1178),(745,1149),(692,1115),(817,1040),(927,928),(999,784)]),('discovery',[(523,271),(443,309),(361,365),(299,432),(271,504),(280,568),(319,551),(377,448),(474,342)])]:
 border=act(smooth(trace,128));pol=Polygon(border);p=points[contains_xy(pol,points[:,0],points[:,1])];p=p[(p[:,2]>base-.5)&(p[:,2]<roof_z-1)];tree=cKDTree(p[:,:2]);center=border.mean(0);verts=[[*center,float(np.median(p[tree.query(center,k=min(24,len(p)))[1],2]))]];faces=[]
 for ring in range(1,13):
  xy=center+(border-center)*(ring/12);dist,ids=tree.query(xy,k=min(24,len(p)));zz=np.median(p[ids,2],axis=1);zz=ndimage.gaussian_filter1d(zz,2,mode='wrap')
  verts.extend(np.column_stack((xy,zz)).tolist())
  for j in range(128):
   u=1+(ring-1)*128+j;vn=1+(ring-1)*128+(j+1)%128
   if ring==1:faces.append([0,u,vn])
   else:
    t=u-128;tn=vn-128;faces.extend([[t,u,vn],[t,vn,tn]])
 # A quadratic surface suppresses scan noise while preserving the source-derived curvature.
 v=np.asarray(verts);c=v[:,:2].mean(0);xy=(v[:,:2]-c)/50;A=np.column_stack((np.ones(len(v)),xy[:,0],xy[:,1],xy[:,0]**2,xy[:,0]*xy[:,1],xy[:,1]**2));coef=np.linalg.lstsq(A,v[:,2],rcond=None)[0];v[:,2]=A@coef;verts=v.tolist()
 petals.append(dict(name=name,vertices=verts,faces=faces,border=border.tolist()))
from shapely.ops import triangulate
def cap(poly):
 return [list(t.exterior.coords)[:3] for t in triangulate(poly) if poly.covers(t)]
roof_faces=cap(Polygon(roof,[sky[::-1]]))
sky_faces=cap(Polygon(sky,[core[::-1]]))
core_faces=cap(Polygon(core))
# Plaza footprint traced from the ACT orthographic image, including stair apron.
plaza=act([(955,72),(1030,116),(1075,510),(1210,1060),(991,1250),(355,1215),(228,775),(246,343),(576,137)])
plaza_triangles=cap(Polygon(plaza))
data=dict(plaza=plaza.tolist(),plaza_triangles=plaza_triangles,roof_triangles=roof_faces,skylight_triangles=sky_faces,core_triangles=core_faces,act_roof_trace=act_roof.tolist(),roof=roof.tolist(),skylight=sky.tolist(),core=core.tolist(),columns=world(cols).tolist(),base=base,roof_z=roof_z,petals=petals,plan_scale_m_per_pixel=scale,detected_columns=len(cols),sources=['ACT mesh3D 2020 registered source','https://www.2portzamparc.com/en/projects/luxembourg-philharmonie/','https://www.philharmonie.lu/en/architecture'],limits=['Context reconstruction, not measured as-built.','Plan registration uses two pointed roof ends; no survey accuracy claim.','Only isolated column marks detected from N3 plan; omitted/merged marks require review.','Curved roof heights regularized from source photogrammetry.'])
(R/'.local_source_cache/r152/philharmonie_clean.json').write_text(json.dumps(data,indent=2));print(json.dumps({k:data[k] for k in ['base','roof_z','plan_scale_m_per_pixel','detected_columns']}))
