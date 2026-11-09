import bpy,bmesh,json,math,numpy as np
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R276_AVLU_BITKI_CAKISMA_TEMIZLIGI_ADAY_v001.blend'))
def mat(n,c,r,m=0):
 a=bpy.data.materials.new(n);a.use_nodes=True;p=a.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=m;return a
metal=mat('R278_TOWER_SILVER',(.54,.61,.62),.32,.65);glass=mat('R278_TOWER_BLUE_GLASS',(.095,.24,.29),.23,.3);roof=mat('R278_TOWER_ROOF',(.22,.24,.24),.85);dark=mat('R278_SPANDREL',(.14,.23,.26),.5,.3)
V={};F={}
def box(name,a,b,z0,z1,depth,ma):
 a=Vector(a);b=Vector(b);n=Vector((-(b-a).y,(b-a).x)).normalized()*depth/2;p=[a-n,b-n,b+n,a+n];vs=[(q.x,q.y,z) for z in [z0,z1] for q in p];k=len(V.setdefault(name,[]));V[name]+=vs;F.setdefault(name,[]).extend(tuple(k+j for j in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);M[name]=ma
M={};ring=[Vector((150+x*.1875,300-y*.1875)) for x,y in [(606,902),(807,581),(876,621),(675,943)]]
# Source elevation horizontal bands, 1600px/110m orthographic, camera z55.
pixels=[1250,1204,1158,1112,1066,1020,974,928,882,836,790,744,698,652,606,560,514,468,422,376,330]
levels=[55+(800-y)*110/1600 for y in pixels];bottom=23.8;top=88.0
# Source-visible pale screen versus blue glass is classified per bay, not baked onto the facade.
scene=bpy.context.scene;scene.camera.location=(417.2,77.8,55);scene.camera.rotation_euler=(Vector((289.9,157.3,55))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=110;scene.render.resolution_x=1600;scene.render.resolution_y=1600;scene.render.resolution_percentage=100;bpy.context.view_layer.update()
img=bpy.data.images.load(str(R/'renders/qa/R278_east_tower_facade_source.png'));pix=np.array(img.pixels[:],dtype=np.float32).reshape(1600,1600,4);screen=mat('R280_PALE_WINDOW_SCREENS',(.56,.60,.58),.62,.12);screen_records=[]
glass.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.29,.42,.45,1)
# Observed ~15 panes on short facade, ~21 on long face; rear cadence provisional.
for edge,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
 u=(b-a).normalized();normal=Vector((u.y,-u.x));normal*=(-1 if normal.dot(sum(ring,Vector((0,0)))/4-(a+b)/2)>0 else 1);length=(b-a).length;n=[51,10,51,10][edge]
 box('R278_A_BASE',a,b,bottom,levels[0]-.2,.30,dark)
 for z in levels:box('R278_A_FLOOR_BANDS',a,b,z-.13,z+.13,.30,metal)
 limits=levels+[top]
 for lo,hi in zip(limits,limits[1:]):
  if hi-lo<.4:continue
  for j in range(n):
   p=a.lerp(b,j/n)+u*.045-normal*.10;q=a.lerp(b,(j+1)/n)-u*.045-normal*.10
   box('R278_A_RECESSED_GLAZING',p,q,lo+.13,hi-.13,.065,glass)
   if edge==2:
    center=(p+q)/2;uv=world_to_camera_view(scene,scene.camera,Vector((center.x,center.y,(lo+hi)/2)));xx=int(uv.x*1600);yy=int(uv.y*1600)
    if 8<xx<1592 and 8<yy<1592:
     rgb=np.median(pix[yy-7:yy+8,xx-5:xx+6,:3].reshape(-1,3),axis=0);ratio=float((rgb[1]+rgb[2])/max(.01,2*rgb[0]));covered=ratio<1.14
     screen_records.append(dict(column=j,z=(lo+hi)/2,sourcePixel=[xx,1600-yy],ratio=ratio,screen=bool(covered)))
     if covered:box('R280_FRONT_SCREENS',p+normal*.055,q+normal*.055,lo+.16,hi-.16,.025,screen)

 for j in range(n+1):
  p=a.lerp(b,j/n);box('R278_A_VERTICAL_MULLIONS',p-u*.045,p+u*.045,levels[0]-.13,top,.26,metal)
 box('R278_A_PARAPET',a,b,top-.15,top+.28,.30,metal)
# Closed flat roof/floor slabs.
def slab(name,z0,z1):
 k=0;V[name]=[(p.x,p.y,z) for z in [z0,z1] for p in ring];F[name]=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];M[name]=roof
slab('R278_A_ROOF',top-.22,top);slab('R278_A_FLOOR',bottom,bottom+.25)
for name,v in V.items():
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],F[name]);me.materials.append(M[name]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
o=bpy.data.objects['R166_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data)
def tower_zone(p):
 # Only inherited high-rise component inside eastern-complex envelope; podium retained.
 return 250<p.x<330 and 110<p.y<210 and p.z>23.5
remove=[v for v in bm.verts if tower_zone(o.matrix_world@v.co)];removed=len(remove);bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(o.data);bm.free()
p=R/'scenes/MUDAM_R280_DOGU_KULE_CEPHE_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.camera.location=(417.2,77.8,55);s.camera.rotation_euler=(Vector((289.9,157.3,55))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=110;s.render.resolution_x=1600;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R280_tower_facade_authored.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith(('R278_','R280_')))
glb=R/'exports/r152_clean/r255_tower_a_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert checks and all(not c['boundary'] and not c['zero'] for c in checks)
(R/'reports/R280_TOWER.json').write_text(json.dumps(dict(accepted=False,published=False,screenClassification=screen_records,removedReferenceVertices=removed,levels=levels,source='R277_east_source_top.png and R278_east_tower_facade_source.png; 21 observed floor lines, 51 long-facade modules',checks=checks,limits=['Rear facade cadence needs independent source elevation','Upper roof plant volume and facade shutter states not yet reconstructed','Base terrain contact not verified','Materials visual approximation; no scan texture','No region completion claim']),indent=2));print('R278_READY',flush=True)


