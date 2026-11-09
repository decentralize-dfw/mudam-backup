import bpy,bmesh,json,re,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R311_ECCL_ORMAN_CEPHE_ADAY_v002.blend'))
objects={}
for o in bpy.context.scene.objects:
 m=re.fullmatch(r'R(?:171|174|182_DISTRICT|300_DISTRICT)_(\d+)',o.name)
 if m:objects.setdefault(m[1],[]).append(o)
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text(encoding='utf8'));eligible=[]
for w in ways:
 if 'building' not in w['tags'] or w['tags'].get('location')=='underground':continue
 pts=[(x-293425,y-5499960) for x,y in w['xy']];cx=sum(p[0] for p in pts)/len(pts);cy=sum(p[1] for p in pts)/len(pts)
 if -600<cx<600 and -590<cy<-230:eligible.append((w,pts))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS','R300_DISTRICT_EDGE_GROUND','R301_GROUND_GAP_REPAIR'] or o.name.startswith(('R182_EXTENSION_','R210_GROUND_CONTINUITY_','R202_ALZETTE_'))):continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True,epsilon=.0001);records=[];rowids=['164179202','1337806219','1337806220','1337806221'];rowcount=sum(o.name.startswith('ARCH_') for o in bpy.context.scene.objects)
for w,pts in eligible:
 id=str(w['id']);obs=objects.get(id,[])
 if id in rowids:records.append(dict(id=id,representation='preserved_architectural_row',nodes=rowcount,groundCheck='separate row geometry verification required'));continue
 if len(obs)!=1:records.append(dict(id=id,error='missing_or_duplicate',objects=[o.name for o in obs]));continue
 o=obs[0];wp=[o.matrix_world@v.co for v in o.data.vertices];base=min(p.z for p in wp);missing=[];gaps=[];count=0
 for a,b in zip(pts,pts[1:]+pts[:1]):
  p,q=Vector(a),Vector(b);num=max(1,math.ceil((p-q).length/.5))
  for j in range(num):
   c=p.lerp(q,j/num);hit,*_=ground.ray_cast(Vector((c.x,c.y,150)),Vector((0,0,-1)),400);count+=1
   if hit:
    if base-hit.z>.03:gaps.append([c.x,c.y,base-hit.z])
   else:missing.append(list(c))
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);boundary=sum(e.is_boundary for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free()
 footprintMaxError=max(min(math.hypot(v.x-x,v.y-y) for v in wp) for x,y in pts)
 records.append(dict(id=id,object=o.name,samples=count,missing=missing,gaps=gaps,boundary=boundary,zero=zero,footprintVertexError=footprintMaxError))
rowSupport=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith(('ARCH_WALL_MASS_','ARCH_REAR_PROJECTION_WALL_')):continue
 world=[o.matrix_world@v.co for v in o.data.vertices];base=min(v.z for v in world);miss=0;gap=0;count=0
 for v in world:
  if abs(v.z-base)>.001:continue
  h,*_=ground.ray_cast(Vector((v.x,v.y,150)),Vector((0,0,-1)),400);count+=1
  if h:gap=max(gap,base-h.z)
  else:miss+=1
 rowSupport.append(dict(name=o.name,samples=count,missing=miss,maxGap=max(0,gap)))
(R/'reports/R313_DISTRICT_COVERAGE_CONTACT.json').write_text(json.dumps(dict(accepted=False,rectangle=[-600,600,-590,-230],eligible=len(eligible),records=records,rowSupport=rowSupport,limitations=['Rectangle coverage does not prove entire annotated region extent','Mapped footprint vertices compared directly; height assumptions unchanged','Detailed row requires separate contact verification']),indent=2));print('R313_READY',len(records),sum(bool(r.get('gaps') or r.get('missing') or r.get('error')) for r in records))

