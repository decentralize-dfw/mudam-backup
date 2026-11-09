import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R252_OVAL_BAGIMSIZ_MIMARI_ADAY_v001.blend'));d=json.loads((R/'config/r252_oval_architecture.json').read_text());old=[Vector(p) for p in d['outer']];smooth=set(list(range(2,6))+list(range(8,14))+list(range(16,20))+list(range(22,27)));glazed=set(list(range(8,14))+list(range(16,20))+list(range(22,27)));ring=[];tags=[]
for i,p1 in enumerate(old):
 p0=old[(i-1)%len(old)];p2=old[(i+1)%len(old)];p3=old[(i+2)%len(old)];n=max(1,math.ceil((p2-p1).length/1.3))
 for j in range(n):
  t=j/n
  p=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t) if i in smooth else p1.lerp(p2,t)
  ring.append(p);tags.append(i)
area=sum(a.x*b.y-b.x*a.y for a,b in zip(ring,ring[1:]+ring[:1]));inner=[]
for i,p in enumerate(ring):
 a=(p-ring[i-1]).normalized();b=(ring[(i+1)%len(ring)]-p).normalized();na=Vector((-a.y,a.x))*(1 if area>0 else -1);nb=Vector((-b.y,b.x))*(1 if area>0 else -1);nn=(na+nb).normalized();inner.append(p+nn*.4/max(.35,nn.dot(nb)))
stone=bpy.data.materials['R252_PALE_LIMESTONE'];glass=bpy.data.materials['R252_ATRIUM_GLASS'];metal=bpy.data.materials['R252_LIGHT_FRAMES'];vs=[];fs=[];mi=[]
def solid(poly,z0,z1,mat):
 k=len(vs);vs.extend((p.x,p.y,z) for z in [z0,z1] for p in poly);ff=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];fs.extend(tuple(k+x for x in f) for f in ff);mi.extend([mat]*6)
windows=[(17.1,19.15),(20.15,22.15),(23.15,25.1),(26.1,27.95)];count=0
for i,a in enumerate(ring):
 j=(i+1)%len(ring);b=ring[j];ia,ib=inner[i],inner[j];poly=[a,b,ib,ia]
 if tags[i] not in glazed:solid(poly,8.5,29.85,0);continue
 lower=8.5
 for z0,z1 in windows:
  solid(poly,lower,z0,0);ga=a.lerp(ia,.28);gb=b.lerp(ib,.28);gai=a.lerp(ia,.45);gbi=b.lerp(ib,.45);solid([ga,gb,gbi,gai],z0,z1,1)
  u=(b-a).normalized();w=min(.055,(b-a).length/4);solid([a,a+u*w,ia+u*w,ia],z0,z1,2);lower=z1;count+=1
 solid(poly,lower,28.9,0)
# Replace blank exterior only; keep roof annulus and independent glazed atrium.
bpy.data.objects.remove(bpy.data.objects['R252_OVAL_MAIN_BODY'],do_unlink=True)
me=bpy.data.meshes.new('R253_OVAL_ARCHITECTURAL_FACADES');me.from_pydata(vs,[],fs);me.update()
for m in [stone,glass,metal]:me.materials.append(m)
for p,m in zip(me.polygons,mi):p.material_index=m
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
# An independently closed floor preserves the original footprint bottom. Courtyard sides are retained below glazing.
from mathutils.geometry import tessellate_polygon
poly=[Vector((*p,0)) for p in d['outer']];n=len(poly);v=[(p.x,p.y,z) for z in [8.5,8.8] for p in poly];f=[]
for tri in tessellate_polygon([poly]):
 ids=[q if isinstance(q,int) else min(range(n),key=lambda i:(poly[i]-q).length_squared) for q in tri];f.extend([tuple(reversed(ids)),tuple(i+n for i in ids)])
f.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n));me=bpy.data.meshes.new('R253_OVAL_FLOOR');me.from_pydata(v,[],f);me.materials.append(stone);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
scene=R/'scenes/MUDAM_R253_OVAL_KAVISLI_CEPHE_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;t=Vector((320,398,20));s.camera.location=t+Vector((80,-100,80));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=100;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R253_oval_facades.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R253_'))
glb=R/'exports/r152_clean/r253_oval_facades_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R253_OVAL_FACADES.json').write_text(json.dumps(dict(accepted=False,published=False,glazedSegments=count,sectionCount=len(ring),checks=checks,source='Isolated ACT front elevation R253, four observed glazing bands projected via orthographic scale',limits=['Unseen rear and lower facade not inferred','Band edge elevations approximate from image','Curve interpolation independent, source footprint not surveyed','Roof perimeter must be reconciled to smoothed outline before publication']),indent=2));print('R253_READY',count,checks,flush=True)
