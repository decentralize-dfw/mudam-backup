from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R191_KUZEY_AVLULAR_v001.blend'))
rows=json.loads((R/'config/r192_court_transitions.json').read_text());raw=json.loads((R/'.local_source_cache/r154/terrain.json').read_text());gv=[];gf=[]
for r in raw['meshes']:
 k=len(gv);gv.extend(r['vertices']);gf.extend([k+i for i in f] for f in r['faces'])
ground=BVHTree.FromPolygons(gv,gf,all_triangles=True);cuts=[]
for r in rows:
 for xy in r['cuts']:
  if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))<0:xy.reverse()
  cuts.append((xy,[min(p[0] for p in xy),max(p[0] for p in xy),min(p[1] for p in xy),max(p[1] for p in xy)]))
def split(poly,a,b):
 ins=[];out=[]
 def dist(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=dist(p),dist(q);(ins if dp>=0 else out).append(p)
  if dp*dq<0:
   t=dp/(dp-dq);v=[u+(w-u)*t for u,w in zip(p,q)];ins.append(v);out.append(v)
 return ins,out
changes=[]
for obj in list(bpy.context.scene.objects):
 if obj.type!='MESH' or obj.name not in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS']:continue
 old=obj.data;old.calc_loop_triangles();uv=old.uv_layers.active;verts=[];faces=[];tex=[];mats=[];cutcount=0
 for t in old.loop_triangles:
  poly=[]
  for vi,li in zip(t.vertices,t.loops):
   p=obj.matrix_world@old.vertices[vi].co;poly.append([*p,*(uv.data[li].uv if uv else (p.x/6,p.y/6))])
  bounds=[min(p[0] for p in poly),max(p[0] for p in poly),min(p[1] for p in poly),max(p[1] for p in poly)];parts=[poly]
  for xy,b in cuts:
   if bounds[1]<b[0] or bounds[0]>b[1] or bounds[3]<b[2] or bounds[2]>b[3]:continue
   result=[]
   for part in parts:
    remain=part
    for a,c in zip(xy,xy[1:]+xy[:1]):
     if len(remain)<3:break
     remain,out=split(remain,a,c)
     if len(out)>=3:result.append(out)
    if len(remain)>=3:cutcount+=1
   parts=result
  for p in parts:
   k=len(verts);verts.extend(v[:3] for v in p);tex.extend(v[3:] for v in p)
   for j in range(1,len(p)-1):faces.append((k,k+j,k+j+1));mats.append(t.material_index)
 me=bpy.data.meshes.new(obj.name+'_R192');me.from_pydata(verts,[],faces);me.update()
 for m in old.materials:me.materials.append(m)
 layer=me.uv_layers.new()
 for p,mi in zip(me.polygons,mats):
  p.material_index=mi;p.use_smooth=True
  for li in p.loop_indices:layer.data[li].uv=tex[me.loops[li].vertex_index]
 obj.data=me;changes.append(dict(name=obj.name,intersections=cutcount));print(obj.name,cutcount,flush=True)
grass=bpy.data.objects['R154_FAR_GROUND'].data.materials[0]
for row in rows:
 vs=[];fs=[];c=row['plane'];origin=row['origin']
 for tri in row['triangles']:
  k=len(vs)
  for x,y,w in tri:
   h=ground.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),300)[0]
   if h is None:raise RuntimeError('Missing transition datum')
   z=c[0]*(x-origin[0])+c[1]*(y-origin[1])+c[2];vs.append((x,y,z*(1-w)+h.z*w))
  fs.append((k,k+1,k+2))
 me=bpy.data.meshes.new('R192_GRADE_'+row['name']);me.from_pydata(vs,[],fs);me.update();me.materials.append(grass);uv=me.uv_layers.new()
 for l in me.loops:v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x/6,v.y/6)
 o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
# Use the verified closed background assets in the working scene as well.
for o in list(bpy.data.objects):
 if o.name.startswith(('R179_BACKGROUND_','R188_BACKGROUND_')):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(R/'exports/r152_clean/r188_background_REVIEW.glb'))
(R/'reports/R192_TRANSITIONS_v001.json').write_text(json.dumps(dict(accepted=False,terrain_changes=changes,limits=['Constructed2m grade blends, not measured retaining walls','Source courtyard fit support remains73.6/69.2percent; hidden edges require comparison','Full11regions remain incomplete']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R192_KUZEY_ZEMIN_BAGLANTILARI_v001.blend'),compress=True)
s=bpy.context.scene;s.render.filepath=str(R/'renders/qa/R192_ground_connections_v001.png');bpy.ops.render.render(write_still=True)
