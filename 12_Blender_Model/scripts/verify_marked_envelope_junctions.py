from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R94_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));fail=[];verts=[];faces=[];solids=[]
for name in r['closed_objects']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges));bm.free();solids.append(row)
 if row['volume']<=0 or row['nonmanifold']:fail.append(row)
 start=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend(tuple(start+i for i in f.vertices) for f in o.data.polygons)
tree=BVHTree.FromPolygons(verts,faces);a=Vector(r['glazing_origin']);u=Vector(r['glazing_u']);n=Vector(r['glazing_normal']);count=0;missing=[]
for i in range(math.ceil(r['glazing_width']/.02)):
 for j in range(math.ceil(r['glazing_height']/.02)):
  x=min(r['glazing_width']-.001,(i+.5)*.02);z=min(r['glazing_height']-.001,(j+.5)*.02);p=a+u*x+Vector((0,0,z));count+=1
  if tree.ray_cast(p+n*.3,-n,.6)[0] is None:missing.append([x,z])
if missing:fail.append(dict(unclosed_samples=missing))
for name in [n for n in r['changed_inherited_objects'] if n!='R10_UPPER_DIAGONAL_WALL']:
 old=bpy.data.objects[name]
 if not old.hide_render or not old.hide_get():fail.append('legacy still visible: '+name)
wall=bpy.data.objects['R10_UPPER_DIAGONAL_WALL'];zs=[(wall.matrix_world@v.co).z for v in wall.data.vertices]
if abs(max(zs)-9.718577096381804)>.0001 or wall.hide_render:fail.append('stair-side wall does not terminate at R26 glass cover')
# Retain the actual upper-gallery stair portal enclosure behind the trimmed approach wall.
for name in ['R23_E_1_JAMB_A','R23_E_1_JAMB_B','R23_E_1_HEAD']:
 o=bpy.data.objects.get(name)
 if o is None or o.hide_render:fail.append('gallery portal boundary missing: '+name)
q=dict(file=r['file'],solids=solids,local_skin_samples=count,missing=missing,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R94_verification.json').write_text(json.dumps(q,indent=2));print('R94',count,'samples',len(fail),'failures');assert not fail
