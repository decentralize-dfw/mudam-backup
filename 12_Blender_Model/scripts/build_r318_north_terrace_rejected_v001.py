from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R317_KUZEY_SUR_KOT_ADAY_v002.blend'))
plane=json.loads((R/'reports/R317_NORTH_WALL_RECONSTRUCTION.json').read_text())['groundPlane']
pixels=[(705,233),(863,235),(863,263),(705,257)]
poly=[(-120+x*220/1400,95-y*220/1400) for x,y in pixels]
regions=[poly];records=[]
def clip(points,a,b,sign,inside):
 out=[]
 for j,P in enumerate(points):
  Q=points[(j+1)%len(points)];f=lambda X:sign*((b[0]-a[0])*(X[1]-a[1])-(b[1]-a[1])*(X[0]-a[0]));dp=f(P);dq=f(Q);ip=dp>=-1e-8 if inside else dp<=1e-8;iq=dq>=-1e-8 if inside else dq<=1e-8
  if ip:out.append(P)
  if ip!=iq:
   t=dp/(dp-dq);out.append(tuple(p+(q-p)*t for p,q in zip(P,Q)))
 return out
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or ob.name not in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN','R182_EXTENSION_GROUND']:continue
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

a,b,c=plane['coefficients'];z=lambda x,y:a*x+b*y+c
vs=[(x,y,z(x,y)+dz) for dz in [-.25,0] for x,y in poly];fs=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
me=bpy.data.meshes.new('R318_NORTH_MOAT_GRASS_TERRACE');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.objects['R152_CLASS2_TERRAIN'].data.materials[0]);o['level_id']='SITE';o['source']='ACT orthographic outline with independent plane fitted to20 stable level observations';o['status']='local candidate, no complete moat acceptance'
u=me.uv_layers.new(name='UVMap');micro=me.uv_layers.new(name='MicroUV');me.uv_layers.active=u
for l in me.loops:
 q=me.vertices[l.vertex_index].co;u.data[l.index].uv=((q.x+500)/1150,(q.y+450)/1100);micro.data[l.index].uv=(q.x/2,q.y/2)
out=R/'scenes/MUDAM_R318_KUZEY_HENDEK_TERAS_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
bpy.ops.object.select_all(action='DESELECT');bpy.data.objects['R318_NORTH_MOAT_GRASS_TERRACE'].select_set(True)
glb=R/'exports/r152_clean/r318_north_terrace_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(0,46,5));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((0,61,-2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=45;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=650;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('R318_Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R318_north_terrace.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R318_NORTH_TERRACE.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,pixelOutline=pixels,worldOutline=poly,groundPlane=plane,terrainCuts=records,glb=checks,limits=['Outline manually traced at0.157m/pixel, not survey','Only grass terrace patch; remaining north moat paving and connections incomplete','Full museum ring incomplete']),indent=2));print('R318_READY',records,checks)


