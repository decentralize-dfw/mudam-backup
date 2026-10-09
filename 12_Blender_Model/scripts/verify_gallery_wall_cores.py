"""R73: closed cores, continuous caps, retained faces and open source passages."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R73_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];coverage=[];passages=[];trees={};up=Vector((0,0,1))
for d in r['definitions']:
 o=bpy.data.objects[d['name']];vs=[o.matrix_world@v.co for v in o.data.vertices];faces=[list(f.vertices) for f in o.data.polygons];t=BVHTree.FromPolygons(vs,faces);trees[o.name]=t;bm=bmesh.new();bm.from_mesh(o.data);q=dict(name=o.name,nonmanifold=sum(not e.is_manifold for e in bm.edges),volume=bm.calc_volume(signed=True),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(q)
 if q['nonmanifold'] or q['volume']<=0 or q['zero_faces']:fail.append(q)
 # Sample the entire convex connecting envelope, with both caps present.
 poly=[Vector((x,y,0)) for x,y in d['polygon_world']];c=sum(poly,Vector())/len(poly)
 for a,b in zip(poly,poly[1:]+poly[:1]):
  for i in range(1,10):
   for fraction in [.02,.25,.5,.75,.98]:
    p=c.lerp(a.lerp(b,i/10),fraction);bottom=t.ray_cast(p+up*(d['z0']-.1),up,d['z1']-d['z0']+.2);top=t.ray_cast(p+up*(d['z1']+.1),-up,.2);q=dict(wall=o.name,bottom_z=bottom[0].z if bottom[0] else None,passed=bottom[0] is not None and top[0] is not None);coverage.append(q)
    if not q['passed']:fail.append(q)
 for old in d['replaced']:
  if not bpy.data.objects[old].hide_render:fail.append(dict(superseded_visible=old))
# Independently preserve the original room-facing wall through its full length.
for d in r['definitions']:
 a,b=map(Vector,d['inner_front']);normal=(b-a).normalized().cross(up)
 for f in [.05,.2,.4,.6,.8,.95]:
  for z in [5.4,8.0,12.0]:
   p=a.lerp(b,f);p.z=z;h=trees[d['name']].ray_cast(p-normal*.03,normal,.06)
   q=dict(inner_boundary=d['name'],fraction=f,z=z,passed=h[0] is not None);coverage.append(q)
   if not q['passed']:fail.append(q)
# Regression against all four source upper gallery openings plus both clear
# portions of the Grand Hall east portal. New bodies must not enter routes.
p=json.loads((B/'reports/R23_build_report.json').read_text())
specs=[dict(id=x['id'],a=x['start'],b=x['end'],n=x['outward'],heights=[p['upper_z']+h for h in [.2,1.5,2.2]]) for x in p['portals']]
p=json.loads((B/'reports/R02_build_report.json').read_text());specs.append(dict(id='GH_EAST',a=p['portal_endpoints'][0],b=p['portal_endpoints'][1],n=p['normal'],heights=[.3,1.65,3.5,4.5,6.0,8.9]))
for s in specs:
 a,b,n=map(Vector,[s['a'],s['b'],s['n']])
 for f in [.1,.25,.5,.75,.9]:
  for z in s['heights']:
   pos=a.lerp(b,f);pos.z=z;hits=[name for name,t in trees.items() if t.ray_cast(pos-n*.64,n,1.28)[0] is not None];q=dict(portal=s['id'],fraction=f,z=z,hits=hits,passed=not hits);passages.append(q)
   if hits:fail.append(q)
result=dict(file=r['file'],solids=solids,cap_coverage=coverage,passage_regressions=passages,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R73_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R73',len(coverage),'cap samples',len(passages),'passage samples',len(fail),'failures');assert not fail,fail[:10]
