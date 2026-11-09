import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R256_IKI_KULE_MIMARI_ADAY_v001.blend'));glass=bpy.data.materials['R255_TOWER_BLUE_GLASS'];metal=bpy.data.materials['R255_TOWER_SILVER'];dark=bpy.data.materials['R255_SPANDREL'];V={};F={};M={}
def prism(n,q,d,mat):
 # q is one planar quadrilateral, thickness vector d.
 V[n]=[tuple(p) for p in q]+[tuple(p+d) for p in q];F[n]=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];M[n]=mat
for o in list(bpy.context.scene.objects):
 if o.name.startswith(('R256_B_SLOPED','R256_B_ROOF_UPSTAND','R256_B_ROOF_BAR','R256_B_COPING')):bpy.data.objects.remove(o,do_unlink=True)
ps=json.loads((R/'config/r256_tower_roof_planes.json').read_text());ring=[Vector(p) for p in [(246,382),(269,400),(241,435),(223,421)]];a,b,c,d=ring;ab=d.lerp(a,.5);bc=b.lerp(c,.5);halves=[([a,b,bc,ab],ps[3]['plane']),([ab,bc,c,d],ps[0]['plane'])]
for k,(poly,co) in enumerate(halves):
 q=[Vector((p.x,p.y,co[0]*p.x+co[1]*p.y+co[2])) for p in poly]
 prism('R257_CONTINUOUS_PITCHED_ROOF_'+str(k),q,Vector((0,0,.12)),glass)
 for j,(p,r) in enumerate(zip(q,q[1:]+q[:1])):
  u=Vector((r.x-p.x,r.y-p.y,0)).normalized();normal=Vector((-u.y,u.x,0))*.1;count=max(1,round((r-p).length/1.5))
  for h in range(count):
   x=p.lerp(r,h/count);y=p.lerp(r,(h+1)/count)
   # Upper glazing closes from existing top floor to the continuous roof edge.
   prism(f'R257_UPPER_FACADE_{k}_{j}_{h}',[Vector((x.x,x.y,88.1)),Vector((y.x,y.y,88.1)),y,x],normal,glass)
   if min(x.z,y.z)>88.4:
    prism(f'R257_UPPER_MULLION_{k}_{j}_{h}',[Vector((x.x-.04*u.x,x.y-.04*u.y,88.1)),Vector((x.x+.04*u.x,x.y+.04*u.y,88.1)),x+u*.04,x-u*.04],normal*2,metal)
 for direction,count in [(0,27),(1,18)]:
  for j in range(count+1):
   t=j/count;x=q[0].lerp(q[1] if direction==0 else q[3],t);y=q[3].lerp(q[2],t) if direction==0 else q[1].lerp(q[2],t);u=(y-x).normalized();v=u.cross(Vector((0,0,1))).normalized()*.04
   prism(f'R257_ROOF_FRAME_{k}_{direction}_{j}',[x-v,y-v,y+v,x+v],Vector((0,0,.08)),metal)
for n,v in V.items():
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],F[n]);me.materials.append(M[n]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o)
# Extend only sub-grade foundations; roof and facade levels remain fixed.
for prefix,old,new in [('R255_A_',6.1,5.0),('R256_B_',6.0,.35)]:
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and o.name in [prefix+'BASE',prefix+'FLOOR']:
   for v in o.data.vertices:
    if v.co.z<old+.31:v.co.z+=new-old
p=R/'scenes/MUDAM_R257_KULE_CATI_CEPHE_BIRLESIM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.camera.location=(390,180,65);s.camera.rotation_euler=(Vector((240,370,48))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=145;s.render.resolution_x=1600;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R257_towers_integrated.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith(('R255_','R256_','R257_')))
glb=R/'exports/r152_clean/r257_towers_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R257_TOWER_JOIN.json').write_text(json.dumps(dict(accepted=False,published=False,checks=checks,limits=['Roof service recesses still need reconstruction; full roof outline simplification not accepted','Upper facade subdivisions provisional','Five terrain misses on tower A remain unresolved','Terrain at tower B varies excessively; subgrade foundation extended but hardscape unresolved']),indent=2));print('R257_CHECKS',len(checks),sum(c['boundary'] for c in checks),sum(c['zero'] for c in checks),flush=True)
