"""Independent ray audit of source-traced configuration lines against current wall meshes.
This checks model/configuration coverage, not survey accuracy or source interpretation.
"""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(B/'scripts'));from release_utils import verified_current_scene
r=verified_current_scene();bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));inventory=json.loads((B/'reports/DUVAR_ENVANTERI.json').read_text());assert inventory['scene']==r['file'];C=json.loads((B/'config/foundation.json').read_text())['calibration'];up=Vector((0,0,1));UP=4.859074784676;LOW=-5.326293513972;deps=bpy.context.evaluated_depsgraph_get();trees={};samples=[];routes=[];fail=[]
for row in inventory['objects']:
 o=bpy.data.objects[row['name']].evaluated_get(deps);me=o.to_mesh();trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);o.to_mesh_clear()
def point(p,z=0,lower=False):
 x,y=p
 if lower:s,dx,dy=C['basement_registration']['source_to_canonical'];x=s*x+dx;y=s*y+dy
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def hits(a,b):
 d=(b-a).normalized();length=(b-a).length;return [name for name,t in trees.items() if t.ray_cast(a,d,length)[0] is not None]
def segment(region,key,a,b,z,lower=False,exclude=None):
 a,b=point(a,z,lower),point(b,z,lower);n=(b-a).normalized().cross(up)
 for i in range(1,20):
  f=i/20
  if exclude and exclude(f):continue
  p=a.lerp(b,f);found=hits(p-n*.45,p+n*.45);q=dict(region=region,segment=key,fraction=f,z=z,hits=found,passed=bool(found));samples.append(q)
  if not found:fail.append(q)
P=json.loads((B/'config/ground_service_rooms.json').read_text());window4=next(w for w in json.loads((B/'reports/R52_build_report.json').read_text())['windows'] if w['bay']==4)
for key,(a,b) in P['walls'].items():
 for z in [.4,1.65,3.9]:
  aperture=None
  if key=='GALLERY_E_S' and .15<z<3.38:
   lo,hi=sorted((p[0]-a[0])/(b[0]-a[0]) for p in window4['back_canonical']);aperture=lambda f:lo-.002<f<hi+.002
  segment('GROUND_SERVICES',key,a,b,z,exclude=aperture)
for key,(a,b) in P['routes'].items():
 found=hits(point(a,1.65),point(b,1.65));q=dict(region='GROUND_SERVICES',route=key,hits=found,passed=not found);routes.append(q)
 if found:fail.append(q)
P=json.loads((B/'config/upper_gallery_room.json').read_text())
for side,poly in P['source_polygons_canonical'].items():
 for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  spec=next((s for s in P['portals'] if s['side']==side and s['edge']==i),None);interval=None
  if spec:
   va,vb=Vector(a),Vector(b);ax=(vb-va).normalized();interval=sorted((Vector(p)-va).dot(ax)/(vb-va).length for p in spec['ends'])
  for z in [UP+1.2,UP+3.6,12.8]:segment('UPPER_GALLERY_'+side,str(i),a,b,z,exclude=(lambda f:interval[0]-.005<f<interval[1]+.005) if interval and z<UP+spec['head'] else None)
P=json.loads((B/'config/reading_room.json').read_text());poly=P['room_inner_polygon']
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
 spec=next((s for s in P['portals'] if s['edge']==i),None);interval=None
 if spec:axis=spec['coordinate_axis'];interval=sorted((v-a[axis])/(b[axis]-a[axis]) for v in spec['source_range'])
 segment('READING',str(i),a,b,UP+1.2,exclude=(lambda f:interval[0]-.005<f<interval[1]+.005) if interval else None)
P=json.loads((B/'config/pavilion_room.json').read_text());poly=P['footprint']
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
 for z in [-2.5,1.2,4.2]:
  if i==3 and z>-.2:continue
  if i==7 and P['west_window_sill_z']<z<P['west_window_head_z']:continue
  segment('PAVILION',str(i),a,b,z)
P=json.loads((B/'config/lower_gallery_rooms.json').read_text())
for side,poly in P['rooms'].items():
 for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  if side=='E' and i==1:b=[420,393]
  if side=='W' and i==len(poly)-1:continue
  segment('LOWER_GALLERY_'+side,str(i),a,b,LOW+1.2,True)
for key,(a,b) in P['routes'].items():
 found=hits(point(a,LOW+1.65,True),point(b,LOW+1.65,True));q=dict(region='LOWER_GALLERIES',route=key,hits=found,passed=not found);routes.append(q)
 if found:fail.append(q)
P=json.loads((B/'config/auditorium_room.json').read_text());L,RX=P['room_x'];front=P['front_y'];rear=P['rear_y']
for key,a,b in [('L',[L,front],[L,rear]),('R',[RX,front],[RX,rear]),('BACK',[L,rear],[RX,rear])]:
 for z in [LOW+1.2,LOW+3.5]:segment('AUDITORIUM',key,a,b,z,True)
for key,x0,x1,d0,d1 in [('L',L,486,469,480),('R',558,RX,565,576)]:
 for z in [LOW+1.2,LOW+3.5]:segment('AUDITORIUM','FRONT_'+key,[x0,front],[x1,front],z,True,exclude=(lambda f:d0<x0+(x1-x0)*f<d1) if z<LOW+2.25 else None)
 found=hits(point([(d0+d1)/2,front-3],LOW+1.5,True),point([(d0+d1)/2,front+3],LOW+1.5,True));q=dict(region='AUDITORIUM',route=key,hits=found,passed=not found);routes.append(q)
 if found:fail.append(q)
path=[(486,front),(486,414),(488,414),(504,398),(540,398),(554,414),(558,414),(558,front)]
for i,(a,b) in enumerate(zip(path,path[1:])):segment('AUDITORIUM','STAGE_'+str(i),a,b,LOW+1.2,True)
result=dict(file=r['file'],coverage_samples=samples,source_route_checks=routes,failures=fail,opening_exceptions=['R52 bay4 source-backed window: .15m sill / 3.38m head; not a missing wall.'],scope='Configuration-to-mesh coverage; source measurements, unlocated technical partitions and unlisted regions are not certified.');(B/'reports/DUVAR_KAYNAK_TARAMASI.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('WALL SOURCE COVERAGE',len(samples),'samples',len(routes),'routes',len(fail),'findings');print(json.dumps(fail[:30],indent=2))
