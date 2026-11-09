import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R311_ECCL_ORMAN_CEPHE_ADAY_v002.blend'))
a=Vector((178.3125,26.625));u=(Vector((332.4375,282.375))-a).normalized();n=Vector((-u.y,u.x));back=a-n*12;front=a-n*1.5;forest=Vector((187.5,24.125));created=[];contacts=[]
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS'] or o.name.startswith(('R182_EXTENSION_','R210_GROUND_CONTINUITY_'))):continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True,epsilon=.0001)
def prism(name,p,q,w,bot,top,mat):
 v=(q-p).normalized();normal=Vector((-v.y,v.x))*w/2;ring=[p-normal,q-normal,q+normal,p+normal];me=bpy.data.meshes.new(name);me.from_pydata([(v.x,v.y,z) for z in (bot,top) for v in ring],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(bpy.data.materials[mat]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);created.append(name)
for name,p,q in [('RETURN',front,back),('CORNER',back,forest)]:
 zs=[]
 for j in range(41):
  v=p.lerp(q,j/40);h,*_=ground.ray_cast(Vector((v.x,v.y,150)),Vector((0,0,-1)),400)
  if h:zs.append(h.z)
 assert len(zs)==41
 base=min(2.226974,min(zs)-.15);prism('R314_'+name+'_BASE',p,q,.30,base,7,'R308_ECCL_FLOOR');contacts.append(dict(name=name,samples=41,base=base,minGround=min(zs),maxGround=max(zs)))
 if name=='CORNER':
  prism('R314_CORNER_GLASS',p,q,.09,7,22.45,'R311_ECCL_GLASS')
  for z in [7,9.5,12,14.5,17,19.5,22.45]:prism('R314_TRANSOM_'+str(z),p,q,.20,z-.04,z+.04,'R308_ECCL_FRAME')
  for i in range(3):
   c=p.lerp(q,i/2);v=(q-p).normalized()*.035;prism('R314_MULLION_'+str(i),c-v,c+v,.20,7,22.48,'R308_ECCL_FRAME')
scene=R/'scenes/MUDAM_R314_ECCL_GUNEY_KOSE_OTURUM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;t=Vector((187,25,12));s.camera.location=t+Vector((55,-80,30));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=45;s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R314_south_corner.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name in created)
glb=R/'exports/r152_clean/r314_corner_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(c['boundary']==0 and c['zero']==0 for c in checks)
(R/'reports/R314_CORNER_CONTACT.json').write_text(json.dumps(dict(accepted=False,published=False,scene=str(scene),contacts=contacts,checks=checks,limits=['Architectural closure between existing independent facade endpoints only','Corner subdivisions and underground support depth provisional','Whole ECCL and first-six acceptance remain incomplete']),indent=2));print('R314_READY')
