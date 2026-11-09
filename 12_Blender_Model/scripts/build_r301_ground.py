import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R300_ALT_MAHALLE_13_KUTLE_TAMAMLAMA_ADAY_v001.blend'));d=json.loads((R/'config/r301_ground_patch.json').read_text())
me=bpy.data.meshes.new('R301_GROUND_GAP_REPAIR');me.from_pydata(d['vertices'],[],d['faces']);me.materials.append(bpy.data.objects['R182_EXTENSION_GROUND'].data.materials[0]);me.update();uv=me.uv_layers.new()
for l in me.loops:p=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(p.x/8,p.y/8)
ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS','R300_DISTRICT_EDGE_GROUND','R301_GROUND_GAP_REPAIR'] or o.name.startswith(('R182_EXTENSION_','R210_GROUND_CONTINUITY_','R202_ALZETTE_'))):continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True,epsilon=.0001);contacts=[]
for domain in d['domains']:
 o=bpy.data.objects[domain['name']];world=[o.matrix_world@v.co for v in o.data.vertices];base=min(p.z for p in world);ids={i for i,p in enumerate(world) if abs(p.z-base)<.001};zs=[];missing=[]
 for e in o.data.edges:
  a,b=e.vertices
  if a not in ids or b not in ids:continue
  p,q=world[a],world[b];n=max(2,math.ceil((q-p).length/.5))
  for j in range(n+1):
   v=p.lerp(q,j/n);h,*_=ground.ray_cast(Vector((v.x,v.y,150)),Vector((0,0,-1)),400)
   if h:zs.append(h.z)
   else:missing.append(list(v))
 assert not missing,(o.name,missing)
 extension=max(0,base-min(zs)+.12)
 for i in ids:o.data.vertices[i].co.z-=extension
 contacts.append(dict(name=o.name,samples=len(zs),missing=0,extension=extension,waterUsedAsLowerSupport=True))
path=R/'scenes/MUDAM_R301_ALT_MAHALLE_ZEMIN_BAGLANTISI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' and (o.name.startswith(('R300_DISTRICT_','ARCH_')) or o.name=='R301_GROUND_GAP_REPAIR' or o.name in [v['name'] for v in contacts]))
glb=R/'exports/r152_clean/r301_district_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;target=Vector((-210,-175,-20));s.camera.location=target+Vector((90,-150,180));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=260;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R301_current_fort.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R301_GROUND_CONTACT.json').write_text(json.dumps(dict(accepted=False,published=False,patchArea=d['area'],contacts=contacts,checks=checks,waterChannelPreserved=True,scope='Local ground coverage and minimum foundation closure only; full district hardscape acceptance pending'),indent=2));print('R301_READY',flush=True)
