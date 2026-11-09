import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R250_NOVOTEL_CATIBOLMELERI_ADAY_v001.blend'));o=bpy.data.objects['R176_NOVOTEL_HIGH'];camera=Vector((490,250,160));verts=[];faces=[];count=0
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);pending={f for f in bm.faces if f.material_index==1};groups=[]
while pending:
 seed=pending.pop();group={seed};stack=[seed]
 while stack:
  f=stack.pop()
  for e in f.edges:
   for q in e.link_faces:
    if q in pending and q.normal.dot(seed.normal)>.999:
     pending.remove(q);group.add(q);stack.append(q)
 groups.append(([o.matrix_world@v.co for v in {v for f in group for v in f.verts}],seed.normal.copy()))
for ps,normal in groups:
 if len(ps)!=4:continue
 center=sum(ps,Vector())/4;n=(o.matrix_world.to_3x3()@normal).normalized()
 if n.dot((camera-center).normalized())<.6:continue
 lo=min(v.z for v in ps);hi=max(v.z for v in ps)
 if hi-lo<1:continue
 xy=sorted(ps,key=lambda v:v.z)[:2];a,b=xy;u=(b-a).normalized();width=(b-a).length
 if width<.3:continue
 # Visible facade shows paired panes vertically; independent horizontal transom.
 a=a.copy();a.z=(lo+hi)/2-.0225;a+=n*.035;k=len(verts)
 for dep in [0,.055]:
  for x,z in [(0,0),(width,0),(width,.045),(0,.045)]:verts.append(tuple(a+u*x+Vector((0,0,z))+n*dep))
 faces.extend([tuple(k+i for i in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]);count+=1
assert count>0, 'No source-facing glazing identified'
me=bpy.data.meshes.new('R251_NOVOTEL_VISIBLE_TRANSOMS');me.from_pydata(verts,[],faces);me.update();me.materials.append(bpy.data.materials['R176_WINDOW_FRAME']);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
scene=R/'scenes/MUDAM_R251_NOVOTEL_CEPHE_BOLUNME_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;t=Vector((370,440,20));s.camera.location=t+Vector((120,-190,140));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=170;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R251_novotel_facade.png');bpy.ops.render.render(write_still=True)
for v in s.objects:v.select_set(v.name=='R251_NOVOTEL_VISIBLE_TRANSOMS')
glb=R/'exports/r152_clean/r251_transoms_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for v in bpy.context.scene.objects:
 if v.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(v.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(c['boundary']==0 and c['zero']==0 for c in checks)
(R/'reports/R251_NOVOTEL_VISIBLE_FACADE.json').write_text(json.dumps(dict(accepted=False,published=False,transoms=count,reopen=checks,source='R250 matched source oblique, visible facade paired vertical panes',limitations=['45mm profile height and55mm depth provisional','Existing bay positions not remeasured; source color variation and remaining facades unresolved']),indent=2));print('R251_READY',count,flush=True)
