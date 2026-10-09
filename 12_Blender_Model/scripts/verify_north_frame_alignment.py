from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R93_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));fail=[];verts=[];faces=[];solids=[]
for name in r['closed_objects']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges));bm.free();solids.append(row)
 if row['volume']<=0 or row['nonmanifold']:fail.append(row)
 start=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend(tuple(start+i for i in f.vertices) for f in o.data.polygons)
tree=BVHTree.FromPolygons(verts,faces);a=Vector(r['origin']);u=Vector(r['u']);n=Vector(r['normal']);count=0;missing=[]
for i in range(math.ceil(r['width']/.02)):
 for j in range(math.ceil(r['height']/.02)):
  x=min(r['width']-.001,(i+.5)*.02);z=min(r['height']-.001,(j+.5)*.02);p=a+u*x+Vector((0,0,z));count+=1
  if tree.ray_cast(p+n*.3,-n,.6)[0] is None:missing.append([x,z])
if missing:fail.append(dict(unclosed_samples=missing))
for name in r['changed_inherited_objects']:
 old=bpy.data.objects[name]
 if not old.hide_render or not old.hide_get():fail.append('legacy visible: '+name)
alignment=[]
for z in r['adjacent_levels'][0]:
 candidates=[o for o in bpy.data.objects if o.name.startswith('R93_NORTH_TRANSOM_')]
 def mid(o):
  zs=[(o.matrix_world@v.co).z for v in o.data.vertices];return (min(zs)+max(zs))/2
 err=min(abs(mid(o)-z) for o in candidates);alignment.append(dict(adjacent_z=z,error_m=err))
 if err>.0002:fail.append(dict(frame_alignment_error=err))
q=dict(file=r['file'],solids=solids,alignment=alignment,local_skin_samples=count,missing=missing,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R93_verification.json').write_text(json.dumps(q,indent=2));print('R93',count,'samples',len(fail),'failures');assert not fail
