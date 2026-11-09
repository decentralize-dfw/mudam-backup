import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R322_BATI_MUZE_TERAS_KOT_ADAY_v004.blend'))
allowed={p['name'] for p in json.loads((R/'.local_source_cache/r152/building_objects.json').read_text()) if p.get('level')!='SITE'}
vs=[];fs=[];names=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or o.name not in allowed:continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
 fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles);names.extend([o.name]*len(o.data.loop_triangles))
b=BVHTree.FromPolygons(vs,fs,all_triangles=True)
pixels=[(849,859),(790,805),(796,652),(748,605),(670,548),(600,540),(495,522)]
pts=[Vector((-120+x*220/1400,95-y*220/1400)) for x,y in pixels];rows=[]
for si,(a,c) in enumerate(zip(pts,pts[1:])):
 d=(c-a).normalized();normal=Vector((d.y,-d.x,0))
 for i in range(math.ceil((c-a).length)+1):
  p=a.lerp(c,i/math.ceil((c-a).length));hits=[]
  for z in [-3.4,-2,0.2]:
   for sign in [-1,1]:
    start=Vector((p.x,p.y,z))+normal*sign*5;direction=-normal*sign
    h,n,idx,dist=b.ray_cast(start,direction,10)
    if h:hits.append(dict(z=z,point=list(h),object=names[idx],normal=list(n),distanceFromBoundary=(h.to_2d()-p).length))
  rows.append(dict(segment=si,xy=list(p),hits=hits))
(R/'reports/R323_MUSEUM_BOUNDARY_CONTACTS.json').write_text(json.dumps(rows,indent=2))
print('CONTACT_SURVEY',len(rows),sum(bool(p['hits']) for p in rows))
