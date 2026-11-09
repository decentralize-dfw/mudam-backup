"""Reopen both scenes; unchanged architecture and sampled LOD surface deviation."""
from pathlib import Path
import bpy,json,hashlib,array
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];r=json.loads((R/'reports/R151_WEB_LOD_build.json').read_text());changed={x['name'] for x in r['changes']}
def digest(o):
 h=hashlib.sha256()
 for items,field,n,c in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
  values=array.array(c,[0])*(len(items)*n);items.foreach_get(field,values);h.update(values.tobytes())
 h.update(str([list(v) for v in o.matrix_world]).encode());return h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=r['source']);before={};samples={};source_counts={}
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get():continue
 if o.name not in changed:before[o.name]=digest(o);continue
 o.data.calc_loop_triangles();tris=o.data.loop_triangles;step=max(1,len(tris)//96);points=[]
 for t in list(tris)[::step]:points.append(list(o.matrix_world@(sum((o.data.vertices[i].co for i in t.vertices),Vector())/3)))
 samples[o.name]=points
bpy.ops.wm.open_mainfile(filepath=r['file']);fail=[];errors=[]
for name,h in before.items():
 o=bpy.context.scene.objects.get(name)
 if o is None or digest(o)!=h:fail.append(dict(name=name,error='architecture geometry changed outside declared LOD scope'))
for name,points in samples.items():
 o=bpy.context.scene.objects[name];v=[o.matrix_world@p.co for p in o.data.vertices];tree=BVHTree.FromPolygons(v,[list(p.vertices) for p in o.data.polygons]);ds=[]
 for p in points:
  near=tree.find_nearest(Vector(p));ds.append(float(near[3]) if near[0] is not None else 1e9)
 distance=min((p.x*p.x+p.y*p.y)**.5 for p in v);limit=.5 if distance<90 else (1 if distance<220 else 2)
 if not name.startswith('R151_ACT_'):limit=.05
 errors.append(dict(name=name,samples=len(ds),max_m=max(ds),mean_m=sum(ds)/len(ds),limit_m=limit))
 if max(ds)>limit:fail.append(errors[-1])
missing=[im.name for im in bpy.data.images if im.users and im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
if missing:fail.append(dict(missing_images=missing))
report=dict(file=r['file'],reopened=True,unchanged_architecture_meshes=len(before),sampled_surface_points=sum(x['samples'] for x in errors),surface_deviation=errors,failures=fail,scope='Face-centre surface samples, not a full Hausdorff bound. Context intentionally simplified; source placement uncertainties unchanged.')
(R/'reports/R151_WEB_LOD_verification.json').write_text(json.dumps(report,indent=2));print('LOD_CHECK',len(before),report['sampled_surface_points'],'FAILURES',len(fail),flush=True)
