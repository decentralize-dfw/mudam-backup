import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R267_ERASMUS_DORT_UST_BAGLANTI_ADAY_v001.blend'));s=bpy.context.scene;t=Vector((150,440,8));s.camera.location=t+Vector((.6542447*60,-.7562829*60,24));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=200;s.render.resolution_x=3400;s.render.resolution_y=1000;bpy.context.view_layer.update();rot=s.camera.matrix_world.to_3x3();right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));dire=rot@Vector((0,0,-1));camera=s.camera.location.copy();planes=json.loads((R/'config/r263_front_planes.json').read_text());glass=bpy.data.materials['R221_BLUE_GREY_GLASS'];metal=bpy.data.materials['R221_DARK_FRAMES'];stone=bpy.data.materials['R222_PALE_MINERAL'];roof=bpy.data.materials['R262_MINERAL_LOWER_ROOF']
traces=[('R268_SEED_FRONT_8',(39,211),[(45,58),(69,82),(93,106),(117,130),(141,154),(165,178),(189,202)])];records=[]

r=next(x for x in json.loads((R/'config/r219_front_planes.json').read_text())['parts'] if x['id']==8);poly=r['polygon'];base=.4;v=[(x,y,base) for x,y in poly]+[(x,y,z) for (x,y),z in zip(poly,r['cornerRoofs'])];me=bpy.data.meshes.new('R268_SEED_FRONT_8');me.from_pydata(v,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('R268_SEED_FRONT_8',me);bpy.context.collection.objects.link(ob)
face=max(me.polygons,key=lambda f:f.normal.dot(Vector((.6542447,-.7562829,0))));planes.append(dict(name=ob.name,normal=list(face.normal),points=[list(me.vertices[i].co) for i in face.vertices]))
for index,(name,bounds,windows) in enumerate(traces):
 old=bpy.data.objects[name];row=next(p for p in planes if p['name']==name);origin=Vector(row['points'][0]);origin.z=0;normal=Vector(row['normal']);u=Vector((.7562829,.6542447,0));u=(u-normal*u.dot(normal)).normalized();vs=[old.matrix_world@v.co for v in old.data.vertices];base=min(p.z for p in vs);toppts=sorted(vs,key=lambda p:p.z,reverse=True)[:4]
 import numpy as np
 aa=np.array([[p.x,p.y,1] for p in toppts]);zz=np.array([p.z for p in toppts]);co=np.linalg.lstsq(aa,zz,rcond=None)[0]
 def roofz(p):return float(co[0]*p.x+co[1]*p.y+co[2])
 def point(px,py):
  p=camera+right*((px/2048-.5)*200)+up*((.5-py/(1000*2048/3400))*200*1000/3400);return p+dire*((origin-p).dot(normal)/dire.dot(normal))
 lo=(point(bounds[0],420)-origin).dot(u);hi=(point(bounds[1],420)-origin).dot(u)
 if lo>hi:lo,hi=hi,lo
 def box(n,x0,x1,y0,y1,z0,z1,ma):
  v=[origin+u*x+normal*y+Vector((0,0,z)) for z in [z0,z1] for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];me=bpy.data.meshes.new(n);me.from_pydata([tuple(p) for p in v],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(ma);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return o
 top=max(p.z for p in toppts);shell=box(f'R268_FRONT_SHELL_{index}',lo,hi,-7,0,base,top,stone)
 for v in shell.data.vertices:
  if abs(v.co.z-top)<.001:v.co.z=roofz(v.co)
 shell.data.materials.append(roof)
 for p in shell.data.polygons:
  if p.normal.z>.9:p.material_index=1
 def cut(c):
  bpy.context.view_layer.objects.active=shell;m=shell.modifiers.new('Real opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
 minroof=min(roofz(origin+u*x+normal*y) for x in [lo,hi] for y in [-7,0]);cut(box('CUT',lo+.35,hi-.35,-6.65,-.35,base+.2,minroof-.25,stone));obs=[]
 for j,(x0,x1) in enumerate(windows):
  a=point(x0,391);b=point(x1,443);l=(a-origin).dot(u);r=(b-origin).dot(u);l,r=min(l,r),max(l,r);z0,z1=min(a.z,b.z),max(a.z,b.z);z0=max(z0,base+.25);z1=min(z1,minroof-.25);assert lo<l<r<hi and z0<z1
  cut(box('CUT',l,r,-.65,.3,z0,z1,stone));box(f'R268_GLASS_{index}_{j}',l+.06,r-.06,-.22,-.16,z0+.06,z1-.06,glass)
  for label,l0,l1,b0,b1 in [('L',l,l+.06,z0,z1),('R',r-.06,r,z0,z1),('B',l,r,z0,z0+.06),('T',l,r,z1-.06,z1),('M',(l+r)/2-.025,(l+r)/2+.025,z0,z1)]:box(f'R268_FRAME_{index}_{j}_{label}',l0,l1,-.27,-.12,b0,b1,metal)
  mid=point((x0+x1)/2,414).z
  if z0<mid<z1:box(f'R268_TRANSOM_{index}_{j}',l,r,-.27,-.12,mid-.035,mid+.035,metal)
  obs.append(dict(pixel=[x0,x1,391,443],u=[l,r],z=[z0,z1]))
 bpy.data.objects.remove(old,do_unlink=True);records.append(dict(replaced=name,newWidth=hi-lo,openings=obs));print('FACADE_DONE',name,flush=True)
path=R/'scenes/MUDAM_R268_ERASMUS_EKSIK_ON_KUTLE_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.resolution_x=2048;s.render.resolution_y=602;s.cycles.samples=16;s.render.filepath=str(R/'renders/qa/R268_erasmus_front_authored.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R268_'))
glb=R/'exports/r152_clean/r268_missing_front_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R268_THREE_FACADES.json').write_text(json.dumps(dict(accepted=False,published=False,records=records,checks=checks,limits=['Manual source projection, not surveyed','Roof plane extrapolation over widened fronts needs comparison','R219 id8 plane has p90 residual0.212m and88.3percent within0.2m; remains unaccepted, explicit source uncertainty. Missing whole volume reconstructed for visual review instead of leaving gap']),indent=2));print('R268_CHECKS',len(checks),sum(c['boundary'] for c in checks),sum(c['zero'] for c in checks),flush=True)
