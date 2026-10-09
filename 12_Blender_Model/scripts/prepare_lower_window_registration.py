"""Read-only conditional camera-ray study; do not fit invented survey dimensions."""
from pathlib import Path
import json,numpy as np
from camera_math import basis
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';cam=json.loads((B/'reports/P06_camera_fit_116.json').read_text());p=np.array(cam['candidates']['triangular_canopy']['camera']);C=json.loads((B/'config/foundation.json').read_text())['calibration'];s=C['meters_per_canonical_pixel'];F=json.loads((B/'config/gallery_reveals_revised.json').read_text());a,b=[np.array([(575-x)*s,(y-447)*s,0.]) for x,y in F['facade_endpoints']];axis=(b-a)/np.linalg.norm(b-a);inside=np.cross(axis,[0,0,1]);inside/=np.linalg.norm(inside)
if np.dot(inside,np.array([(575-400)*s,(500-447)*s,0])-(a+b)/2)<0:inside=-inside
pixels=[[761,941],[832,953],[908,969],[985,984],[1070,1002]];rows=[]
for z in [-.7,-1.,-1.3,-1.6]:
 windows=[]
 for px in pixels:
  ray=np.array([(px[0]-cam['size'][0]/2)/np.exp(p[6]),-(px[1]-cam['size'][1]/2)/np.exp(p[6]),1.])@basis(p);hit=p[:3]+ray*((z-p[2])/ray[2]);delta=hit-a;windows.append(dict(pixel=px,t_m=float(delta@axis),inside_depth_m=float(delta@inside),canonical=[float(575-hit[0]/s),float(hit[1]/s+447)]))
 rows.append(dict(head_z_candidate=z,windows=windows))
result=dict(status='diagnostic_not_accepted_geometry',camera='P06_camera_fit_116.json',pixel_identity='manual top centers, approximate source116; not independently triangulated',rows=rows,limits=['Head elevations are hypotheses, not measurements. Camera and facade registration carry prior uncertainty.','Do not align lower windows to upper bays; compare rays against historic wall and lower facade before modelling.'])
old=json.loads((B/'reports/R27_build_report.json').read_text());wa=np.array(old['origin']);wu=np.array(old['axis']);wn=np.array(old['inside']);wall=json.loads((B/'config/site_moat.json').read_text())['wall_paths'][0]['points'][:2]
def local(q):
 delta=np.array([*q,0.])-wa;return a+axis*(delta@wu)+inside*(delta@wn)
l0,l1=map(local,wall);wall_axis=(l1-l0)/np.linalg.norm(l1-l0);wall_in=np.cross(wall_axis,[0,0,1]);wall_in*=1 if wall_in@inside>0 else -1
wallrows=[]
for offset in [.45,.65,.85]:
 plane=l0+wall_in*offset;windows=[]
 for top,bottom in zip(pixels,[[763,958],[834,974],[909,990],[987,1008],[1072,1023]]):
  hits=[]
  for px in [top,bottom]:
   ray=np.array([(px[0]-cam['size'][0]/2)/np.exp(p[6]),-(px[1]-cam['size'][1]/2)/np.exp(p[6]),1.])@basis(p);hit=p[:3]+ray*((plane-p[:3])@wall_in/(ray@wall_in));hits.append(dict(z=float(hit[2]),t=float((hit-l0)@wall_axis),world=list(wa+wu*((hit-a)@axis)+wn*((hit-a)@inside)+np.array([0,0,hit[2]]))))
  windows.append(dict(top=top,bottom=bottom,hits=hits))
 wallrows.append(dict(inner_offset_from_osm_center_m=offset,windows=windows))
result['osm_glass_plane_study']=wallrows
(B/'reports/R54_lower_window_registration_study.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
print('OSM plane study',json.dumps(wallrows,indent=2))
