import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R259_KULE_SERVIS_GIRINTILERI_ADAY_v001.blend'));holes=[[Vector((211+x*.05,443-y*.05)) for x,y in p] for p in [[(415,452),(453,420),(670,674),(632,706)],[(640,736),(680,702),(855,959),(815,993)]]];metal=bpy.data.materials['R255_TOWER_SILVER'];dark=bpy.data.materials['R255_SPANDREL'];count=0
faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def mesh(n,v,ma):
 me=bpy.data.meshes.new(n);me.from_pydata([tuple(p) for p in v],[],faces);me.materials.append(ma);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o)
def cross(a,b):return a.x*b.y-a.y*b.x
def inside(p,poly):
 vals=[cross(b-a,p-a) for a,b in zip(poly,poly[1:]+poly[:1])];return all(v>=-1e-6 for v in vals) or all(v<=1e-6 for v in vals)
for o in list(bpy.context.scene.objects):
 if not o.name.startswith('R257_ROOF_FRAME'):continue
 vs=[v.co.copy() for v in o.data.vertices];a=sum((vs[i] for i in [0,3,4,7]),Vector())/4;b=sum((vs[i] for i in [1,2,5,6]),Vector())/4;aa=Vector((a.x,a.y));bb=Vector((b.x,b.y));d=bb-aa;ts=[0.,1.]
 for poly in holes:
  for p,q in zip(poly,poly[1:]+poly[:1]):
   e=q-p;den=cross(d,e)
   if abs(den)<1e-9:continue
   t=cross(p-aa,e)/den;u=cross(p-aa,d)/den
   if 0<t<1 and 0<=u<=1:ts.append(t)
 ts=sorted(set(round(t,9) for t in ts));spans=[(x,y) for x,y in zip(ts,ts[1:]) if y-x>1e-7 and not any(inside(aa.lerp(bb,(x+y)/2),p) for p in holes)]
 if spans==[(0.,1.)]:continue
 for x,y in spans:
  p=a.lerp(b,x);q=a.lerp(b,y);u=(q-p).normalized();v=u.cross(Vector((0,0,1))).normalized()*.04;w=u.cross(v).normalized()*.04;mesh('R261_CLIPPED_ROOF_FRAME_'+str(count),[r+i*v+j*w for r in [p,q] for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]],metal);count+=1
 bpy.data.objects.remove(o,do_unlink=True)
planes=json.loads((R/'config/r256_tower_roof_planes.json').read_text());m=Vector((234.5,401.5));n=Vector((255,417.5));line=n-m
for i,poly in enumerate(holes):
 for j,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  da=cross(line,a-m);db=cross(line,b-m);parts=[a,b]
  if da*db<0:parts.insert(1,a.lerp(b,da/(da-db)))
  for k,(x,y) in enumerate(zip(parts,parts[1:])):
   c=planes[3 if cross(line,(x+y)/2-m)<0 else 0]['plane'];z=lambda p:c[0]*p.x+c[1]*p.y+c[2];u=(y-x).normalized();v=Vector((-u.y,u.x))*.10;q=[Vector((x.x,x.y,88.3)),Vector((y.x,y.y,88.3)),Vector((y.x,y.y,z(y))),Vector((x.x,x.y,z(x)))];mesh(f'R261_SERVICE_REVEAL_{i}_{j}_{k}',q+[p+Vector((v.x,v.y,0)) for p in q],dark)
p=R/'scenes/MUDAM_R261_KULE_SERVIS_BOSLUKLARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.camera.location=(246,408,220);s.camera.rotation_euler=(0,0,0);s.camera.data.ortho_scale=70;s.render.resolution_x=1400;s.render.resolution_y=1400;s.cycles.samples=16;s.render.filepath=str(R/'renders/qa/R261_roof_top_authored.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith(('R255_','R256_','R257_','R258_','R261_')))
glb=R/'exports/r152_clean/r261_towers_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R261_SERVICE_RECESSES.json').write_text(json.dumps(dict(accepted=False,published=False,splitFrames=count,checks=checks,limits=['Whole source comparison still required','Roof equipment not modeled','Ground apron unresolved']),indent=2));print('R261_CHECKS',len(checks),sum(c['boundary'] for c in checks),sum(c['zero'] for c in checks),flush=True)
