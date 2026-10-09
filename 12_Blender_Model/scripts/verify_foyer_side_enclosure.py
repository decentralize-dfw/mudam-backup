"""R81 reopened solids, fixed boundary closure and unchanged auditorium circulation."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R81_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];s,dx,dy=C['basement_registration']['source_to_canonical'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];trees={};up=Vector((0,0,1))
def point(p,z=0):
 x,y=p;x=x*s+dx;y=y*s+dy;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for name in r['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();solids.append(dict(name=name,nonmanifold_edges=bad,volume_m3=vol));trees[name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(f.vertices) for f in ob.data.polygons])
 if bad or vol<=0:fail.append(solids[-1])
boundaries=[]
for side,path in r['native_paths'].items():
 for i,(a,b) in enumerate(zip(path,path[1:])):
  va,vb=point(a),point(b);normal=(vb-va).normalized().cross(up)
  for t in [.05,.25,.5,.75,.95]:
   for z in [r['lower_z']+.1,r['lower_z']+1.2,r['soffit_z']-.1]:
    p=va.lerp(vb,t)+up*z;hit=trees[f'R81_{side}_RETURN_{i:02d}'].ray_cast(p-normal*.3,normal,.6)[0] is not None;boundaries.append(hit)
    if not hit:fail.append(dict(side=side,segment=i,t=t,z=z))
portals=[]
for x in [470,474,478,566,570,574]:
 p=point([x,409],r['lower_z']+1.2);d=(point([x,423])-point([x,409])).normalized();length=(point([x,423])-point([x,409])).length;hits=[n for n,t in trees.items() if t.ray_cast(p,d,length)[0] is not None];portals.append(dict(native_x=x,new_obstructions=hits))
 if hits:fail.append(portals[-1])
q=dict(file=r['file'],solids=solids,boundary_samples=len(boundaries),preserved_entrances=portals,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R81_verification.json').write_text(json.dumps(q,indent=2),encoding='utf8');print('R81',len(solids),'solids',len(boundaries),'boundary samples',len(fail),'failures');assert not fail,fail
