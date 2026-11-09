from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R242_KALE_ISTINAT_ZEMIN_BAGLANTI_ADAY_v001.blend'))
d=json.loads((R/'config/r243_uphill_apron.json').read_text());outline=[Vector((p[0],p[1])) for p in d['points']];xmin=min(p.x for p in outline)-2;xmax=max(p.x for p in outline)+2;ymin=min(p.y for p in outline)-2;ymax=max(p.y for p in outline)+2
names=[o.name for o in bpy.context.scene.objects if o.type=='MESH' and (o.name in ('R154_FAR_GROUND','R241_RUIN_SURROUND') or o.name.startswith('R193_SOUTHWEST_COURT'))]
def inside(q):
 c=False
 for a,b in zip(outline,outline[1:]+outline[:1]):
  if (a.y>q.y)!=(b.y>q.y) and q.x<(b.x-a.x)*(q.y-a.y)/(b.y-a.y)+a.x:c=not c
 return c
def distance(q,a,b):
 v=b-a;t=max(0,min(1,(q-a).dot(v)/v.length_squared));return (q-a-v*t).length
changes=[]
for name in names:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));M=o.matrix_world;inv=M.inverted()
 for _ in range(3):
  edges=set()
  for f in bm.faces:
   pts=[M@v.co for v in f.verts]
   if max(p.x for p in pts)<xmin or min(p.x for p in pts)>xmax or max(p.y for p in pts)<ymin or min(p.y for p in pts)>ymax:continue
   edges.update(e for e in f.edges if (M@e.verts[0].co-M@e.verts[1].co).length>.75)
  if not edges:break
  bmesh.ops.subdivide_edges(bm,edges=list(edges),cuts=2,use_grid_fill=True);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 changed=0;shift=0
 for v in bm.verts:
  p=M@v.co;q=Vector((p.x,p.y))
  if not inside(q):continue
  x=(p.x-d['gradeOrigin'][0])/20;y=(p.y-d['gradeOrigin'][1])/20;z=sum(a*b for a,b in zip(d['gradeCoefficients'],[1,x,y,x*x,x*y,y*y]));w=min(1,min(distance(q,a,b) for a,b in zip(outline,outline[1:]+outline[:1]))/1.5);w=w*w*(3-2*w);new=p.z*(1-w)+z*w;shift=max(shift,abs(new-p.z));p.z=new;v.co=inv@p;changed+=1
 mat=bpy.data.materials['R234_DRY_FORT_EARTH'];o.data.materials.append(mat);mi=len(o.data.materials)-1
 for f in bm.faces:
  p=M@f.calc_center_median()
  if inside(Vector((p.x,p.y))):f.material_index=mi
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-10],context='FACES');bm.to_mesh(o.data);bm.free();o.data.update();changes.append(dict(name=name,vertices=changed,maxShift=shift))
p=R/'scenes/MUDAM_R245_KALE_UST_AVLU_SUREKLI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;t=Vector((-229.6,-192.1,-18));s.camera.location=t+Vector((35,-45,45));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=48;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R245_apron_candidate.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name in names)
glb=R/'exports/r152_clean/r245_apron_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[dict(name=o.name,finite=all(math.isfinite(c) for v in o.data.vertices for c in v.co),zero=sum(p.area<1e-10 for p in o.data.polygons)) for o in bpy.context.scene.objects if o.type=='MESH'];print('CHECKS',checks)
(R/'reports/R245_UPHILL_APRON.json').write_text(json.dumps(dict(accepted=False,published=False,changes=changes,reopen=checks,method='Deform/refine existing authored terrain continuously inside source-traced apron; no scan mesh transfer, no separate surface cuts',limits=['Material boundary approximated by refined faces','Shared object boundaries and source fidelity need review']),indent=2));assert all(c['finite'] and not c['zero'] for c in checks);print('R245_READY')
