from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_CATI_PENCERELERI_v077.blend'))
measure=json.loads((D/'front_mansard_measurements_v078.json').read_text());data=np.array([[r['point'][2],r['offset']] for r in measure]);good=data[:,0]>-65.5;A=np.c_[data[good,0]+65.5,np.ones(good.sum())];coef=np.linalg.lstsq(A,data[good,1],rcond=None)[0];res=abs(A@coef-data[good,1]);keep=res<.12;coef=np.linalg.lstsq(A[keep],data[good,1][keep],rcond=None)[0]
center=Vector((-78.6563873,-306.0042725,-69));right=Vector((.9779602885,.2087912709,0));n=Vector((.208791494,-.977960169,0));wall=bpy.data.objects['ARCH_WALL_MASS_2'];matwall=wall.data.materials[0];slate=bpy.data.materials['Authored slate - neutral unlit source color not copied'];frame=bpy.data.materials['Painted light window frames'];glass=bpy.data.materials['Glazing subdued blue grey']
# Lower wall meets measured foot of the steep roof band.
for v in wall.data.vertices:
 if v.co.z>-65.5:v.co.z=-65.5
wall.data.update()
def coord(x,y,offset=None):
 z=-69+(395.636-y)*36/2048;p=center+right*((x-1024)*36/2048);p.z=z;return p+n*(float(coef[0]*(z+65.5)+coef[1]) if offset is None else offset)
def mesh(name,v,f,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat);o['method']='Independent architectural geometry, source measurements only';return o
# Registered source-visible pale dormer fronts and their visible glazing.
panels=[(110,90,215,190),(330,90,490,190),(850,90,982,190),(1080,90,1250,190),(1290,90,1440,190),(1580,90,1700,190),(1790,90,1925,190)]
windows=[(125,112,199,160,2),(344,105,474,160,3),(862,111,970,160,3),(1120,117,1238,175,3),(1310,115,1418,175,3),(1600,108,1680,160,2),(1807,110,1910,165,3)]
# Roof band domain top is the actual authored main roof eave, bottom joins lowered front wall.
q=json.loads((D/'facade_planes_v062.json').read_text())['q'];roofedge=[Vector((*q[i],0)) for i in [2,3]]
for p in roofedge:
 hits=[]
 for o in bpy.context.scene.objects:
  if o.name.startswith('ARCH_MAIN_ROOF'):
   h,loc,no,ix=o.ray_cast(Vector((p.x,p.y,10)),Vector((0,0,-1)))
   if h:hits.append(loc.z)
 # Polygon boundary ray fallback: closest roof vertex XY is the source-traced eave endpoint.
 if not hits:
  candidates=[v.co for o in bpy.context.scene.objects if o.name.startswith('ARCH_MAIN_ROOF') for v in o.data.vertices];near=min(candidates,key=lambda v:(v.x-p.x)**2+(v.y-p.y)**2);hits=[near.z]
 p.z=max(hits)
xedge=[1024+(p-center).dot(right)*2048/36 for p in roofedge];xlo,xhi=min(xedge),max(xedge)
def upper(x):
 u=(x-xedge[0])/(xedge[1]-xedge[0]);return roofedge[0].lerp(roofedge[1],u)
def bandpoint(x,y):
 bottom=coord(x,195.0);top=upper(x);z=-69+(395.636-y)*36/2048;f=(z-bottom.z)/(top.z-bottom.z);return bottom.lerp(top,f)
xs=sorted(set([xlo,xhi]+[max(xlo,min(xhi,x)) for p in panels for x in [p[0],p[2]]]));ys=[90,190,195];vv=[];ff=[]
def quad(points):
 k=len(vv);vv.extend(points);ff.append((k,k+1,k+2,k+3))
# Build strips from main eave to foot with rectangular dormer cutouts; top may lie below nominal panel top.
for xl,xr in zip(xs,xs[1:]):
 mid=(xl+xr)/2;panel=next((p for p in panels if p[0]<mid<p[2]),None)
 if not panel:quad([upper(xl),upper(xr),bandpoint(xr,195),bandpoint(xl,195)])
 else:quad([bandpoint(xl,190),bandpoint(xr,190),bandpoint(xr,195),bandpoint(xl,195)])
mesh('ARCH_FRONT_MANSARD_BAND',vv,ff,slate)
for i,(panel,win) in enumerate(zip(panels,windows)):
 x0,y0,x1,y1=panel;l,top,r,bot,panes=win;off=.025
 # White dormer face has an actual opening, modeled as four solid face strips.
 v=[];f=[]
 for rect in [(x0,y0,x1,top),(x0,bot,x1,y1),(x0,top,l,bot),(r,top,x1,bot)]:
  a,b,c,d=rect;k=len(v);v.extend([coord(a,b,off),coord(c,b,off),coord(c,d,off),coord(a,d,off)]);f.append((k,k+1,k+2,k+3))
 mesh(f'ARCH_DORMER_FRONT_{i}',v,f,matwall)
 # Sloped cap and side cheeks return to parent roof eave without copying source surfaces.
 mesh(f'ARCH_DORMER_CAP_{i}',[coord(x0,y0,off),coord(x1,y0,off),upper(x1),upper(x0)],[(0,1,2,3)],slate)
 for x in [x0,x1]:mesh(f'ARCH_DORMER_CHEEK_{i}_{x}',[coord(x,y0,off),coord(x,y1,off),bandpoint(x,y1),upper(x)],[(0,1,2,3)],slate)
 mesh(f'ARCH_DORMER_GLASS_{i}',[coord(l,top,-.10),coord(r,top,-.10),coord(r,bot,-.10),coord(l,bot,-.10)],[(0,1,2,3)],glass)
 for j in range(panes+1):
  x=l+(r-l)*j/panes;mesh(f'ARCH_DORMER_MULLION_{i}_{j}',[coord(x-1.7,top,0),coord(x+1.7,top,0),coord(x+1.7,bot,0),coord(x-1.7,bot,0)],[(0,1,2,3)],frame)
 for y in [top,bot]:mesh(f'ARCH_DORMER_FRAME_{i}_{y}',[coord(l,y-1.7,0),coord(r,y-1.7,0),coord(r,y+1.7,0),coord(l,y+1.7,0)],[(0,1,2,3)],frame)
s=bpy.context.scene;s['acceptance']='WIP not accepted; front mansard and seven source-visible dormer groups authored. Rear/ends and hidden openings still incomplete.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_MANSARD_v078.blend'));s.render.filepath=str(R/'renders/qa/R169_architectural_mansard_v078.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_ARCHITECTURAL_MANSARD_v078.json').write_text(json.dumps(dict(accepted=False,source_measurements=len(measure),fit=coef.tolist(),fit_p90=float(np.quantile(abs(A@coef-data[good,1]),.9)),source_fronts=panels,source_windows=windows,assumptions=['Frame depth','Dormer cap return inferred between measured front and roof'],pending=['Cap planarity and source comparison','End and rear band','Chimneys and rear projections','Ground contact and export']),indent=2));print('MANSARD_SAVED')
