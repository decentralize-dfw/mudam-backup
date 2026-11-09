import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R249_ALT_MAHALLE_TEMEL_ADAY_v001.blend'));rows=json.loads((R/'config/r250_lowroof_architecture.json').read_text());plane=json.loads((R/'config/r206_novotel_roof_planes.json').read_text())[1]
def zbase(p):return plane['plane'][0]*(p.x-plane['origin'][0])+plane['plane'][1]*(p.y-plane['origin'][1])+plane['plane'][2]
for o in list(bpy.data.objects):
 if o.name.startswith('R209_ROOF_DIVISION_'):bpy.data.objects.remove(o,do_unlink=True)
mat=bpy.data.materials.new('R250_WARM_ROOF_GRAVEL');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.22,.185,.14,1);bs.inputs['Roughness'].default_value=.92
body=bpy.data.objects['R176_NOVOTEL_LOW'];body.data.materials.append(mat);mi=len(body.data.materials)-1
for f in body.data.polygons:
 if f.normal.z>.8:f.material_index=mi
made=[]
for r in rows:
 if r['samples']<10:continue
 pts=[Vector(p) for p in r['path']];dirs=[(b-a).normalized() for a,b in zip(pts,pts[1:])];norms=[Vector((-d.y,d.x)) for d in dirs];left=[];right=[]
 for i,p in enumerate(pts):
  if i==0:off=norms[0]*r['width']/2
  elif i==len(pts)-1:off=norms[-1]*r['width']/2
  else:
   n=(norms[i-1]+norms[i]).normalized();off=n*(r['width']/2/max(.3,n.dot(norms[i])))
  left.append(p+off);right.append(p-off)
 ring=left+right[::-1];n=len(ring);vs=[(p.x,p.y,zbase(p)) for p in ring]+[(p.x,p.y,r['top']) for p in ring];vv=[Vector((p.x,p.y,0)) for p in ring];fs=[]
 for tri in tessellate_polygon([vv]):
  ix=[v if isinstance(v,int) else min(range(n),key=lambda j:(vv[j]-v).length_squared) for v in tri];fs.extend([tuple(reversed(ix)),tuple(j+n for j in ix)])
 fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n));me=bpy.data.meshes.new('R250_ROOF_NETWORK_%02d'%r['id']);me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['R176_PALE_MINERAL']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert not any(e.is_boundary for e in bm.edges);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);made.append(o.name)
scene=R/'scenes/MUDAM_R250_NOVOTEL_CATIBOLMELERI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;t=Vector((370,440,20));s.camera.location=t+Vector((120,-190,140));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=170;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R250_lowroof_rebuilt.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name in made or o.name=='R176_NOVOTEL_LOW')
glb=R/'exports/r152_clean/r250_roof_network_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R250_ROOF_NETWORK.json').write_text(json.dumps(dict(accepted=False,published=False,created=made,reopen=checks,source='R250_lowroof_source_top.png; independent traced planar paths and scalar source elevations',limits=['Roof members have approximate0.45m widths','Path4 insufficient sample support omitted','Uniform cap heights simplify unresolved slopes','Source has incomplete east boundary coverage; fullbuilding not accepted']),indent=2));print('R250_READY',checks,flush=True)
