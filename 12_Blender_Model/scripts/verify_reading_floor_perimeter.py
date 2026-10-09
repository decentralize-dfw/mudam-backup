from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R107_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/reading_room.json').read_text());Q=json.loads((B/'config/reading_void.json').read_text());D=json.loads((B/'reports/R09_build_report.json').read_text());UP=D['floor_z'];up=Vector((0,0,1));results={};fail=[]
def pt(p,z=0):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def inside(p,poly):
 yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));deps=bpy.context.evaluated_depsgraph_get();ob=bpy.data.objects[r['object']].evaluated_get(deps);me=ob.to_mesh();vs=[ob.matrix_world@v.co for v in me.vertices];fs=[list(f.vertices) for f in me.polygons];tree=BVHTree.FromPolygons(vs,fs);bm=bmesh.new();bm.from_mesh(me);solid=dict(nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces),volume=bm.calc_volume(signed=True));bm.free();ob.to_mesh_clear();rows=[];poly=list(map(pt,P['room_inner_polygon']));center=sum(poly,Vector())/8
 for ei,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  axis=(b-a).normalized();normal=axis.cross(up)
  if normal.dot((a+b)/2-center)<0:normal=-normal
  n=math.ceil((b-a).length/.08)
  for i in range(n):
   p=a.lerp(b,(i+.5)/n)-normal*.015+up*(UP+.03);hit=tree.ray_cast(p,-up,.08);rows.append(dict(kind='perimeter',edge=ei,index=i,passed=hit[0] is not None))
 for x in range(542,612,2):
  for y in range(606,678,2):
   if not inside([x,y],P['room_inner_polygon']) or abs(x-Q['center_canonical'][0])+abs(y-Q['center_canonical'][1])<Q['floor_void_half_diagonal_canonical']+.3:continue
   rows.append(dict(kind='interior',x=x,y=y,passed=tree.ray_cast(pt([x,y],UP+.03),-up,.08)[0] is not None))
 for dx,dy in [(0,0),(8,0),(-8,0),(0,8),(0,-8)]:
  p=pt([Q['center_canonical'][0]+dx,Q['center_canonical'][1]+dy],UP+.03);rows.append(dict(kind='central_void',dx=dx,dy=dy,passed=tree.ray_cast(p,-up,.3)[0] is None))
 results[phase]=dict(checks=rows,solid=solid)
 if phase=='after':
  fail.extend(x for x in rows if not x['passed'])
  if solid['nonmanifold'] or solid['zero_faces'] or solid['volume']<=0:fail.append(solid)
# Existing portal definitions checked against the full current scene.
vs=[];fs=[];owners=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs);routes=[]
for portal in D['portals']:
 a,b=map(Vector,[portal['a'],portal['b']]);axis=(b-a).normalized();normal=(a+b)/2-center;normal=(normal-axis*normal.dot(axis)).normalized()
 for fraction in [.15,.5,.85]:
  p=a.lerp(b,fraction);p.z=UP+1.6;hit=t.ray_cast(p-normal*.65,normal,1.3);row=dict(portal=portal['id'],kind='passage',fraction=fraction,passed=hit[0] is None);routes.append(row)
  for offset in [-.65,0,.65]:
   q=p+normal*offset;q.z=UP+.03;floor=t.ray_cast(q,-up,.08);head=t.ray_cast(q,up,2.1);routes.append(dict(portal=portal['id'],kind='support_head',fraction=fraction,offset=offset,passed=floor[0] is not None and head[0] is None))
fail.extend(x for x in routes if not x['passed']);q=dict(file=r['file'],results=results,route_checks=routes,failures=fail,previously_missing=sum(not x['passed'] for x in results['before']['checks']),construction_acceptance=False)
(B/'reports/R107_verification.json').write_text(json.dumps(q,indent=2));print('R107',len(rows),'floor/void checks',len(routes),'route checks',q['previously_missing'],'old misses',len(fail),'failures');assert not fail,fail
