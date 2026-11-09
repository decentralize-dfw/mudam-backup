from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R242_KALE_ISTINAT_ZEMIN_BAGLANTI_ADAY_v001.blend'));cam=bpy.context.scene.camera;cam.location=(171,366,27);cam.rotation_euler=(Vector((126,414,6))-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();direction=cam.matrix_world.to_quaternion()@Vector((0,0,-1))
parts=json.loads((R/'config/r227_raised_planes.json').read_text())['parts'];records=[]
glass=bpy.data.materials['R221_BLUE_GREY_GLASS'];metal=bpy.data.materials['R221_DARK_FRAMES']
for part,rects in zip(parts,[[(447,270,497,312),(621,273,673,315)],[(974,279,1021,319),(1146,282,1187,321)]]):
 ident=part['id'];poly=part['polygon'];a=Vector((*poly[3],0));b=Vector((*poly[2],0));u=(b-a).normalized();n=Vector((u.y,-u.x,0));o=bpy.data.objects['R227_ERASMUS_REAR_'+str(ident)]
 def solid(name,x0,x1,y0,y1,z0,z1,mat=None):
  vs=[tuple(a+u*x+n*y+Vector((0,0,z))) for z in (z0,z1) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
  if mat:me.materials.append(mat)
  return ob
 def cut(c):
  bpy.context.view_layer.objects.active=o;m=o.modifiers.new('SOURCE_APERTURE','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
 bounds=[]
 for x in ([427,696] if ident==0 else [947,1208]):
  start=cam.matrix_world@Vector(((x/1400-.5)*65,(.5-290/1000)*65*1000/1400,0));hit=start+direction*(n.dot(a-start)/n.dot(direction));bounds.append(u.dot(hit-a))
 lo,hi=min(bounds),max(bounds);oldU=[u.dot(v.co-a) for v in o.data.vertices];oldlo=min(oldU);oldhi=max(oldU)
 for vert,uu in zip(o.data.vertices,oldU):
  if abs(uu-oldlo)<.1:vert.co+=u*(lo-oldlo)
  elif abs(uu-oldhi)<.1:vert.co+=u*(hi-oldhi)
  if vert.co.z>13.8:vert.co.z=part['plane'][0]*(vert.co.x-part['origin'][0])+part['plane'][1]*(vert.co.y-part['origin'][1])+part['plane'][2]
 o.data.update()
 windows=[]
 for rect in rects:
  pts=[]
  for x,y in [(rect[0],rect[1]),(rect[2],rect[1]),(rect[2],rect[3]),(rect[0],rect[3])]:
   start=cam.matrix_world@Vector(((x/1400-.5)*65,(.5-y/1000)*65*1000/1400,0));hit=start+direction*(n.dot(a-start)/n.dot(direction));pts.append((u.dot(hit-a),hit.z))
  windows.append(dict(u0=min(p[0] for p in pts),u1=max(p[0] for p in pts),z0=min(p[1] for p in pts),z1=max(p[1] for p in pts),pixels=rect))
 print('WINDOWS',ident,windows,'LENGTH',(b-a).length,flush=True)
 for i,w in enumerate(windows):
  x0,x1,z0,z1=[w[k] for k in ['u0','u1','z0','z1']]
  assert lo+.08<x0<x1<hi-.08,(ident,w)
  assert z1<min(part['cornerRoofs'])-.08,(ident,w)
  # A closed recessed aperture, glazing and independent frames; source does not resolve the room behind.
  cut(solid('CUT',x0,x1,-.32,.3,z0,z1));solid(f'R246_GLASS_{ident}_{i}',x0+.045,x1-.045,-.30,-.28,z0+.045,z1-.045,glass)
  for label,xx0,xx1,zz0,zz1 in [('L',x0,x0+.045,z0,z1),('R',x1-.045,x1,z0,z1),('B',x0,x1,z0,z0+.045),('T',x0,x1,z1-.045,z1),('M',(x0+x1)/2-.0225,(x0+x1)/2+.0225,z0,z1)]:solid(f'R246_FRAME_{ident}_{i}_{label}',xx0,xx1,-.31,-.22,zz0,zz1,metal)
 records.append(dict(part=ident,windows=windows,sourceFacadeBounds=[lo,hi],oldFacadeBounds=[oldlo,oldhi]))
p=R/'scenes/MUDAM_R246_ERASMUS_UST_CEPHE_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;c=s.camera;c.location=(171,366,27);c.rotation_euler=(Vector((126,414,6))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=65;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R246_erasmus_front.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith(('R246_','R227_ERASMUS_REAR_')))
glb=R/'exports/r152_clean/r246_upper_facades_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(not c['boundary'] and not c['zero'] for c in checks)
(R/'reports/R246_ERASMUS_UPPER_FACADES.json').write_text(json.dumps(dict(accepted=False,published=False,records=records,reopen=checks,limits=['Projected visible source rectangles; not surveyed dimensions','Recess .32m and frame .045m provisional; hidden interiors not modeled','Whole Erasmus still incomplete']),indent=2));print('R246_READY')

