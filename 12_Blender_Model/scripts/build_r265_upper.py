import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R264_ERASMUS_SON_ON_CEPHE_ADAY_v001.blend'));s=bpy.context.scene;t=Vector((150,440,8));s.camera.location=t+Vector((.6542447*60,-.7562829*60,24));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=200;s.render.resolution_x=3400;s.render.resolution_y=1000;bpy.context.view_layer.update();rot=s.camera.matrix_world.to_3x3();right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));dire=rot@Vector((0,0,-1));cam=s.camera.location.copy();glass=bpy.data.materials['R221_BLUE_GREY_GLASS'];metal=bpy.data.materials['R221_DARK_FRAMES'];rows=json.loads((R/'config/r265_upper_planes.json').read_text());traces={'R216_ERASMUS_WING_2':[(295,307),(318,330),(342,354),(366,378),(390,402)],'R217_ERASMUS_WING_8':[(44,56),(67,79),(91,103),(115,127),(139,150)],'R217_ERASMUS_WING_12':[(1035,1047),(1059,1071),(1083,1095),(1107,1119),(1131,1143)],'R217_ERASMUS_WING_13':[(1270,1282),(1294,1306),(1318,1330),(1342,1354),(1366,1378)],'R217_ERASMUS_WING_14':[(1518,1530),(1542,1554),(1566,1578),(1590,1602),(1614,1625)]};records=[]
for name,windows in traces.items():
 o=bpy.data.objects[name];row=next(r for r in rows if r['name']==name);a=Vector(row['points'][0]);a.z=0;n=Vector(row['normal']);u=Vector((.7562829,.6542447,0));u=(u-n*u.dot(n)).normalized()
 def point(x,y):
  p=cam+right*((x/2048-.5)*200)+up*((.5-y/(1000*2048/3400))*200*1000/3400);return p+dire*((a-p).dot(n)/dire.dot(n))
 def box(name,l,r,y0,y1,z0,z1,ma):
  vs=[tuple(a+u*x+n*y+Vector((0,0,z))) for z in [z0,z1] for x,y in [(l,y0),(r,y0),(r,y1),(l,y1)]];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(ma);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);return ob
 obs=[]
 for i,(px0,px1) in enumerate(windows):
  p=point(px0,335);q=point(px1,351);l,r=sorted([(p-a).dot(u),(q-a).dot(u)]);z0,z1=sorted([p.z,q.z]);c=box('CUT',l,r,-.7,.2,z0,z1,metal);bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Measured window recess','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
  box(f'R265_GLASS_{name}_{i}',l+.04,r-.04,-.24,-.19,z0+.04,z1-.04,glass)
  for label,x0,x1,b0,b1 in [('L',l,l+.05,z0,z1),('R',r-.05,r,z0,z1),('B',l,r,z0,z0+.05),('T',l,r,z1-.05,z1),('M',(l+r)/2-.025,(l+r)/2+.025,z0,z1)]:box(f'R265_FRAME_{name}_{i}_{label}',x0,x1,-.27,-.13,b0,b1,metal)
  obs.append(dict(pixel=[px0,px1,335,351],u=[l,r],z=[z0,z1]))
 records.append(dict(name=name,windows=obs));print('UPPER_DONE',name,flush=True)
path=R/'scenes/MUDAM_R265_ERASMUS_UST_ACIKLIKLAR_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.resolution_x=2048;s.render.resolution_y=602;s.cycles.samples=16;s.render.filepath=str(R/'renders/qa/R265_erasmus_front_authored.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R265_') or o.name in traces)
glb=R/'exports/r152_clean/r265_upper_windows_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R265_UPPER_WINDOWS.json').write_text(json.dumps(dict(accepted=False,published=False,records=records,checks=checks,limits=['Window recesses and separate glazing/frames; full interiors not reconstructed','Manual source image projection, not surveyed','Rear/courtyard construction still incomplete']),indent=2));print('R265_CHECKS',len(checks),sum(c['boundary'] for c in checks),sum(c['zero'] for c in checks),flush=True)
