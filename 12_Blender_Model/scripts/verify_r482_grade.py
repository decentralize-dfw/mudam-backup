import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
from collections import Counter
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R464_AVLU_CAMI_ZEMIN_KESISI_ADAY_v001.blend'))
D=json.loads((R/'reports/R482_COURT_PATH_DOMAINS.json').read_text());P=json.loads((R/'reports/R481_WEST_PATH_GRADE.json').read_text());G=json.loads((R/'reports/R479_NW_FOUR_GRADE_PLANES.json').read_text());assert P['valid']
vs=[];fs=[]
for name in ['R457_NORTH_LOADING_COURT','R458_WEST_SERVICE_PLAZA']:
 o=bpy.data.objects[name];o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([[i+k for i in t.vertices] for t in o.data.loop_triangles])
B=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def edgey(x):
 return 44.557142857+(x+59.971428571)*(.314285714/13.042857143) if x<=-46.928571429 else 44.871428571-(x+46.928571429)*(.314285714/13.828571429)
def court(x):
 h,*_=B.ray_cast(Vector((x,edgey(x)+.002,20)),Vector((0,0,-1)),50)
 assert h is not None,x
 return h.z
pc=P['coefficients']
def rawpath(x,y):return sum(a*b for a,b in zip(pc,[1,x,y,x*x,x*y,y*y]))
def pathgrade(x,y):
 w=max(0,min(1,(y-43.2)/1.01));return rawpath(x,y)*(1-w)+court(max(-58.22,min(-44.43,x)))*w
# Actual traced west verge, and north lawn boundary; bank widths are explicit model parameters.
west=np.array(sorted([(44.21,-58.22),(37,-57.31),(27.9,-56.855),(20.165,-57.415)]))
north=np.array(sorted([(-58.22,44.21),(-44.78,44.0),(-44.43,43.16)]))
def lawn(x,y):
 xe=float(np.interp(y,west[:,0],west[:,1]));yn=float(np.interp(x,north[:,0],north[:,1]));base=G['planes'][0];floor=base[0]+base[1]*(x+51)+base[2]*(y-35)
 w=max(0,1-max(0,x-xe)/3.5);n=max(0,1-max(0,yn-y)/2.5)
 westz=floor+(pathgrade(xe,y)-floor)*w;northz=floor+(court(max(-58.22,min(-44.43,x)))-floor)*n
 e=G['planes'][3];east=e[0]+e[1]*(x+51)+e[2]*(y-35)
 return max(floor,westz,northz,east)

contacts=[]
for y in np.linspace(20.165,44.21,80):
 x=float(np.interp(y,west[:,0],west[:,1]));contacts.append(abs(lawn(x,y)-pathgrade(x,y)));
 if contacts[-1]>.1: print("west",x,y,lawn(x,y),pathgrade(x,y))
for x in np.linspace(-58.22,-44.43,80):
 y=float(np.interp(x,north[:,0],north[:,1]));contacts.append(abs(lawn(x,y)-court(x)));
 if contacts[-1]>.1: print("north",x,y,lawn(x,y),court(x))
q=np.array(json.loads((R/'reports/R478_FULL_BANK_CONTROLS.json').read_text())['controls']);errors=np.array([lawn(x,y)-z for x,y,z in q]);out=dict(sharedBoundarySamples=len(contacts),maxAnalyticJoinGap=float(max(contacts)),finalGradeDiagnosticRms=float(np.sqrt(np.mean(errors*errors))),finalGradeDiagnosticMax=float(abs(errors).max()),independent=False,accepted=False);(R/'reports/R482_FINAL_GRADE_DIAGNOSTIC.json').write_text(json.dumps(out,indent=2));print(out)
