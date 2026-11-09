import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R266_ERASMUS_UC_ARKA_BAGLANTI_ADAY_v001.blend'));s=bpy.context.scene;t=Vector((150,440,8));s.camera.location=t+Vector((.6542447*60,-.7562829*60,24));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=200;s.render.resolution_x=3400;s.render.resolution_y=1000;bpy.context.view_layer.update();rot=s.camera.matrix_world.to_3x3();right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));dire=rot@Vector((0,0,-1));cam=s.camera.location.copy();rows=json.loads((R/'config/r267_raised_rear_planes.json').read_text())['parts'];stone=bpy.data.materials['R222_PALE_MINERAL'];glass=bpy.data.materials['R221_BLUE_GREY_GLASS'];metal=bpy.data.materials['R221_DARK_FRAMES'];records=[]
for o in s.objects:
 if o.type=='MESH' and o.name.startswith(('R216_ERASMUS_WING','R217_ERASMUS_WING')):
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001);bm.to_mesh(o.data);bm.free()
traces=[[(43,66),(137,158)],[(289,312),(385,406)],[(1028,1051),(1121,1144)],[(1270,1293),(1366,1388)]]
for i,row in enumerate(rows[:4]):
 assert row['supported'] and row['samples']>=150;poly=[Vector((*p,0)) for p in row['polygon']];a=poly[3];u=(poly[2]-a).normalized();n=Vector((u.y,-u.x,0));length=(poly[2]-a).length;depth=abs((poly[0]-a).dot(n));base=.4;roof=min(row['cornerRoofs']);origin=Vector((*row['origin'],0));co=row['plane']
 def point(x,y):
  p=cam+right*((x/2048-.5)*200)+up*((.5-y/(1000*2048/3400))*200*1000/3400);return p+dire*((a-p).dot(n)/dire.dot(n))
 bounds=[(39,165),(282,413),(1021,1152),(1263,1397)][i]
 left=(point(bounds[0],230)-a).dot(u);rightEdge=(point(bounds[1],230)-a).dot(u);a=a+u*left;length=rightEdge-left
 def box(name,l,r,y0,y1,z0,z1,ma):
  v=[tuple(a+u*x+n*y+Vector((0,0,z))) for z in [z0,z1] for x,y in [(l,y0),(r,y0),(r,y1),(l,y1)]];me=bpy.data.meshes.new(name);me.from_pydata(v,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(ma);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
 shell=box(f'R267_REAR_CONNECTOR_{i}',0,length,-depth,0,base,roof,stone)
 for v in shell.data.vertices:
  if abs(v.co.z-roof)<.001:v.co.z=co[0]*(v.co.x-origin.x)+co[1]*(v.co.y-origin.y)+co[2]
 def cut(c):
  bpy.context.view_layer.objects.active=shell;m=shell.modifiers.new('Source opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
 cut(box('CUT',.35,length-.35,-depth+.35,-.35,base+.2,roof-.25,stone));obs=[]
 for j,(x0,x1) in enumerate(traces[i]):
  p,q=point(x0,221),point(x1,239);l,r=sorted([(p-a).dot(u),(q-a).dot(u)]);z0,z1=sorted([p.z,q.z]);assert 0<l<r<length and base<z0<z1<roof
  cut(box('CUT',l,r,-.7,.3,z0,z1,stone));box(f'R267_GLASS_{i}_{j}',l+.05,r-.05,-.25,-.18,z0+.05,z1-.05,glass)
  for label,l0,l1,b0,b1 in [('L',l,l+.06,z0,z1),('R',r-.06,r,z0,z1),('B',l,r,z0,z0+.06),('T',l,r,z1-.06,z1),('M',(l+r)/2-.025,(l+r)/2+.025,z0,z1)]:box(f'R267_FRAME_{i}_{j}_{label}',l0,l1,-.28,-.12,b0,b1,metal)
  for py in []:
   z=point((x0+x1)/2,py).z;box(f'R267_TRANSOM_{i}_{j}_{py}',l,r,-.28,-.12,z-.035,z+.035,metal)
  obs.append(dict(pixel=[x0,x1,221,239],u=[l,r],z=[z0,z1]))
 records.append(dict(id=i,roofPlane=row,openings=obs));print('REAR_DONE',i,flush=True)
path=R/'scenes/MUDAM_R267_ERASMUS_DORT_UST_BAGLANTI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.resolution_x=2048;s.render.resolution_y=602;s.cycles.samples=16;s.render.filepath=str(R/'renders/qa/R267_erasmus_front_authored.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith(('R265_','R267_','R216_ERASMUS_WING','R217_ERASMUS_WING')))
glb=R/'exports/r152_clean/r267_raised_rear_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R267_REAR_CONNECTORS.json').write_text(json.dumps(dict(accepted=False,published=False,records=records,checks=checks,limits=['Foundation lower extent provisional','Source window projection and independent roof planes; no source triangles','Fifth raised volume rejected: only9source samples; cannot extrapolate entire roof','Courtyards and side connections remain to be constructed']),indent=2));print('R267_CHECKS',len(checks),sum(c['boundary'] for c in checks),sum(c['zero'] for c in checks),flush=True)
