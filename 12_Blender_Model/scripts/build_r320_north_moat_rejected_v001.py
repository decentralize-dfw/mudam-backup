import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R319_SUR_ZEMIN_TEMAS_ADAY_v001.blend'))
terrain=bpy.data.objects['R152_CLASS2_TERRAIN'];terrain.data.calc_loop_triangles();original=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in terrain.data.vertices],[list(t.vertices) for t in terrain.data.loop_triangles],all_triangles=True)
mat=terrain.data.materials[0];plane=json.loads((R/'reports/R317_NORTH_WALL_RECONSTRUCTION.json').read_text())['groundPlane'];aa,bb,cc=plane['coefficients']
poly=[(-9.2,60.89),(15.6,60.50),(15.6,53.67),(-9.2,54.61)];regions=[poly];records=[]
def clip(points,a,b,sign,inside):
 out=[]
 for j,P in enumerate(points):
  Q=points[(j+1)%len(points)];f=lambda X:sign*((b[0]-a[0])*(X[1]-a[1])-(b[1]-a[1])*(X[0]-a[0]));dp=f(P);dq=f(Q);ip=dp>=-1e-8 if inside else dp<=1e-8;iq=dq>=-1e-8 if inside else dq<=1e-8
  if ip:out.append(P)
  if ip!=iq:
   t=dp/(dp-dq);out.append(tuple(p+(q-p)*t for p,q in zip(P,Q)))
 return out
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or ob.name not in ['R152_CLASS2_TERRAIN']:continue
 me=ob.data;me.calc_loop_triangles();uvs=list(me.uv_layers);verts=[];faces=[];mis=[];attrs=[];changed=0
 for tr in me.loop_triangles:
  points=[]
  for li in tr.loops:
   q=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;points.append(tuple(q)+tuple(v for layer in uvs for v in layer.data[li].uv))
  chunks=[points]
  for region in regions:
   sign=1 if sum(region[i][0]*region[(i+1)%4][1]-region[(i+1)%4][0]*region[i][1] for i in range(4))>0 else -1;result=[]
   for chunk in chunks:
    if max(p[0] for p in chunk)<min(p[0] for p in region) or min(p[0] for p in chunk)>max(p[0] for p in region) or max(p[1] for p in chunk)<min(p[1] for p in region) or min(p[1] for p in chunk)>max(p[1] for p in region):result.append(chunk);continue
    remaining=chunk
    for i,a in enumerate(region):
     if len(remaining)<3:break
     b=region[(i+1)%4];outside=clip(remaining,a,b,sign,False)
     if len(outside)>2:result.append(outside)
     remaining=clip(remaining,a,b,sign,True)
    if len(remaining)>2:changed+=1
   chunks=result
  for chunk in chunks:
   for i in range(1,len(chunk)-1):
    tri=[chunk[0],chunk[i],chunk[i+1]]
    if (Vector(tri[1][:3])-Vector(tri[0][:3])).cross(Vector(tri[2][:3])-Vector(tri[0][:3])).length<1e-8:continue
    k=len(verts);verts.extend(tuple(ob.matrix_world.inverted()@Vector(p[:3])) for p in tri);attrs.extend(p[3:] for p in tri);faces.append((k,k+1,k+2));mis.append(tr.material_index)
 if changed:
  new=bpy.data.meshes.new(ob.name+'_COURT_CUT');new.from_pydata(verts,[],faces);new.update()
  for ma in me.materials:new.materials.append(ma)
  for i,ma in enumerate(mis):new.polygons[i].material_index=ma
  for j,layer in enumerate(uvs):
   dst=new.uv_layers.new(name=layer.name)
   for l in new.loops:dst.data[l.index].uv=attrs[l.vertex_index][j*2:j*2+2]
  ob.data=new;records.append(dict(name=ob.name,cutTriangles=changed))

def distance(p,u,v):
 p,u,v=Vector(p),Vector(u),Vector(v);d=v-u;t=max(0,min(1,(p-u).dot(d)/d.length_squared));return (p-u-t*d).length
def inside(p):
 return all((Vector(poly[(i+1)%4])-Vector(poly[i])).cross(Vector(p)-Vector(poly[i]))<=1e-7 for i in range(4))
points=set(poly)
# Exact surviving cut-edge vertices ensure the three exposed perimeter edges meet old terrain.
for v in terrain.data.vertices:
 q=terrain.matrix_world@v.co;p=(q.x,q.y)
 if inside(p) and min(distance(p,poly[i],poly[(i+1)%4]) for i in range(4))<1e-4:points.add((round(q.x,6),round(q.y,6)))
for ix in range(26):
 for iy in range(9):
  p=(-9.2+24.8*ix/25,53.67+7.22*iy/8)
  if inside(p):points.add(p)
points=list(points);verts2,edges,faces,*_=delaunay_2d_cdt([Vector(p) for p in points],[],[],0,1e-6)
vs=[]
for p in verts2:
 h=original.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),250)[0];assert h is not None
 # North edge is deliberately sharp and buried in the existing wall thickness.
 d=min(distance(p,poly[i],poly[(i+1)%4]) for i in [1,2,3]);w=min(1,d/1.3);w=w*w*(3-2*w);z=h.z+w*(aa*p.x+bb*p.y+cc-h.z);vs.append((p.x,p.y,z))
fs=[list(f) for f in faces if inside(sum((Vector(vs[i][:2]) for i in f),Vector((0,0)))/len(f))]
me=bpy.data.meshes.new('R320_NORTH_MOAT_WALL_FOOT_TERRACE');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(mat)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
u=me.uv_layers.new(name='UVMap');micro=me.uv_layers.new(name='MicroUV');me.uv_layers.active=u
for l in me.loops:
 q=me.vertices[l.vertex_index].co;u.data[l.index].uv=((q.x+500)/1150,(q.y+450)/1100);micro.data[l.index].uv=(q.x/2,q.y/2)
for f in me.polygons:f.use_smooth=True
ob['level_id']='SITE';ob['source']='Independent analytic ground plane fitted to20 stable source points; three perimeter transitions meet retained ground; north edge terminates inside wall';ob['status']='local candidate'
bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Buried ground thickness','SOLIDIFY');mod.thickness=.2;mod.offset=-1;bpy.ops.object.modifier_apply(modifier=mod.name)
out=R/'scenes/MUDAM_R320_KUZEY_SUR_HENDEK_BIRLESIM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));bpy.ops.object.select_all(action='DESELECT');bpy.data.objects['R320_NORTH_MOAT_WALL_FOOT_TERRACE'].select_set(True)
glb=R/'exports/r152_clean/r320_north_moat_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(0,46,5));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((0,61,-2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=45;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=650;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('R320_Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R320_north_moat.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-4);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R320_NORTH_MOAT_CONTACT.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,polygon=poly,groundPlane=plane,terrainCuts=records,glb=checks,limits=['Only central north moat reconstructed','Other ring sections and global likeness unaccepted','No surveyed hidden foundation claim']),indent=2));print('R320_READY',checks)
