from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R178_STATION_v001.blend'));d=json.loads((R/'config/r177_road_union.json').read_text());xy=[(-120,370),(30,370),(30,550),(-120,550)];edges=list(zip(xy,xy[1:]+xy[:1]));o=bpy.data.objects['R161_ROAD_CONNECTIONS'];old=o.data;old.calc_loop_triangles();uv=old.uv_layers.active;verts=[];faces=[];tex=[];cut=0
def split(poly,a,b):
 def dist(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 ins=[];outs=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=dist(p),dist(q);(ins if dp>=0 else outs).append(p)
  if dp*dq<0:
   t=dp/(dp-dq);v=[u+(w-u)*t for u,w in zip(p,q)];ins.append(v);outs.append(v)
 return ins,outs
for tri in old.loop_triangles:
 poly=[]
 for vi,li in zip(tri.vertices,tri.loops):p=o.matrix_world@old.vertices[vi].co;poly.append([*p,*uv.data[li].uv])
 if max(p[0] for p in poly)<-120 or min(p[0] for p in poly)>30 or max(p[1] for p in poly)<370 or min(p[1] for p in poly)>550:parts=[poly]
 else:
  parts=[];remaining=poly
  for a,b in edges:
   if len(remaining)<3:break
   remaining,out=split(remaining,a,b)
   if len(out)>=3:parts.append(out)
  if len(remaining)>=3:cut+=1
 for part in parts:
  k=len(verts);verts.extend(p[:3] for p in part);tex.extend(p[3:] for p in part);faces.extend((k,k+j,k+j+1) for j in range(1,len(part)-1))
me=bpy.data.meshes.new('R177_TRIMMED_INHERITED_ROAD');me.from_pydata(verts,[],faces);me.update()
for m in old.materials:me.materials.append(m)
uvnew=me.uv_layers.new(name=uv.name)
for l in me.loops:uvnew.data[l.index].uv=tex[l.vertex_index]
o.data=me
for previous in list(bpy.data.objects):
 if previous.name.startswith('R177_ROAD_'):bpy.data.objects.remove(previous,do_unlink=True)
vs=[];fs=[]
for obj in bpy.context.scene.objects:
 if obj.type=='MESH' and obj.name in ['R154_FAR_GROUND','R154_FAR_ROADS']:
  obj.data.calc_loop_triangles();k=len(vs);vs.extend(obj.matrix_world@v.co for v in obj.data.vertices);fs.extend([k+j for j in t.vertices] for t in obj.data.loop_triangles)
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def material(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.9;return m
asphalt=bpy.data.materials.get('R154_ROAD_PBR') or material('R177_ASPHALT',(.07,.07,.075));paving=material('R177_PAVED_WALK',(.36,.34,.3));mark=material('R177_PAINT',(.83,.83,.78));report=[]
def refine(tri):
 a,b,c=tri
 lens=[sum((p[i]-q[i])**2 for i in range(2)) for p,q in [(a,b),(b,c),(c,a)]]
 if max(lens)<=2.25:return [tri]
 k=lens.index(max(lens));p,q,r=[(a,b,c),(b,c,a),(c,a,b)][k];m=[(p[i]+q[i])/2 for i in range(2)]
 return refine([p,m,r])+refine([m,q,r])
for row in d['surfaces']+[dict(id='MARKINGS',kind='markings',triangles=d['markings'])]:
 vs=[];fs=[];miss=0
 for tri in [t for source_tri in row['triangles'] for t in refine(source_tri)]:
  ps=[]
  for x,y in tri:
   h,*_=ground.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),350)
   if h:ps.append((x,y,h.z+(.075 if row['kind']=='markings' else .055)))
  if len(ps)<3:miss+=1;continue
  k=len(vs);vs.extend(ps);fs.append((k,k+1,k+2))
 mesh=bpy.data.meshes.new('R177_ROAD_'+row['id']);mesh.from_pydata(vs,[],fs);mesh.update();obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(mark if row['kind']=='markings' else paving if row['kind'] in ['path','footway','pedestrian'] else asphalt);layer=mesh.uv_layers.new()
 for l in mesh.loops:p=mesh.vertices[l.vertex_index].co;layer.data[l.index].uv=(p.x/6,p.y/6)
 report.append({'id':row['id'],'triangles':len(fs),'ground_misses':miss})
(R/'reports/R177_ROADS_v003.json').write_text(json.dumps({'accepted':False,'trimmed_inherited_triangles':cut,'reconstruction':report,'limits':d['limits']},indent=2))
s=bpy.context.scene;s.camera.location=(-45,450,220);s.camera.rotation_euler=(0,0,0);s.camera.data.ortho_scale=200;s.render.resolution_x=1200;s.render.resolution_y=1200;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R177_TASAN_YOL_YENIDEN_v003.blend'),compress=True)
s.render.filepath=str(R/'renders/qa/R177_road_top_v003.png');bpy.ops.render.render(write_still=True);print('R177_DONE',cut)

