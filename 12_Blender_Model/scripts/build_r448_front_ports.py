import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R446_KALE_EGIMLI_BURC_GOVDESI_ADAY_v001.blend'));rows=json.loads((R/'reports/R447_PHOTO_OPENING_POSITIONS.json').read_text());body=bpy.data.objects['R154_FORT_MASONRY_BODY'];stone=bpy.data.materials['R406_FORT_DRESSED_SANDSTONE'];dark=bpy.data.materials['R154_RECESSED_OPENINGS'];names=[]
def mesh(name,vs,fs,ma):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(ma);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o['level_id']='SITE';names.append(name);return o
for row in rows:
 assert row['hit'];p=Vector(row['point']);n=Vector(row['normal']).normalized();t=Vector((0,0,1)).cross(n).normalized();up=n.cross(t).normalized();w=row['width'];h=row['height'];label=row['label'];ring=[]
 if row['shape']=='circle':ring=[(w/2*math.cos(math.tau*i/40),h/2*math.sin(math.tau*i/40)) for i in range(40)]
 else:ring=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]
 def prism(name,shape,d0,d1,ma):
  N=len(shape);vs=[tuple(p+t*x+up*z+n*d) for d in [d0,d1] for x,z in shape];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];return mesh(name,vs,fs,ma)
 cutter=prism('R448_TEMP',ring,-.65,.35,dark);bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Photo documented port','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);names.remove(cutter.name);bpy.data.objects.remove(cutter,do_unlink=True)
 prism('R448_'+label+'_RECESS',ring,-.655,-.645,dark)
 if row['shape']=='circle':
  N=40;vs=[]
  for d,rad in [(-.035,w/2),(.035,w/2),(.035,w/2+.105),(-.035,w/2+.105)]:
   vs.extend(tuple(p+t*(rad*math.cos(math.tau*i/N))+up*(rad*math.sin(math.tau*i/N))+n*d) for i in range(N))
  fs=[(k*N+i,k*N+(i+1)%N,((k+1)%4)*N+(i+1)%N,((k+1)%4)*N+i) for k in range(4) for i in range(N)];mesh('R448_'+label+'_STONE_RING',vs,fs,stone)
  prism('R448_'+label+'_CROSSBAR',[(-w/2,-.018),(w/2,-.018),(w/2,.018),(-w/2,.018)],-.12,-.10,stone)
  prism('R448_'+label+'_VERTICALBAR',[(-.018,-h/2),(.018,-h/2),(.018,h/2),(-.018,h/2)],-.12,-.10,stone)
 else:
  prism('R448_'+label+'_LINTEL',[(-w/2-.11,h/2),(w/2+.11,h/2),(w/2+.11,h/2+.12),(-w/2-.11,h/2+.12)],-.03,.08,stone)
# Stabilize boolean n-gons for GLB; retain the inherited intentional eave boundary.
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-4);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-4);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bodyCheck=dict(boundary=sum(e.is_boundary for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.to_mesh(body.data);bm.free()
out=R/'scenes/MUDAM_R448_KALE_FOTOGRAF_MAZGAL_ACIKLIKLARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R448_FRONT_PORTS.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,sourcePositions=rows,checks=checks,bodyCheck=bodyCheck,limits=['Source photo camera residual8.58px; positions/widths are registered visual estimates, not survey.','Recess depth0.65m modeled estimate.','Bastion rear quarters and complete ring not yet validated.']),indent=2));print('R448_SAVED',bodyCheck,flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-107,-92,6));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-63,-54,1.7))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=50;s.render.filepath=str(R/'renders/qa/R448_front_candidate.png');bpy.ops.render.render(write_still=True)
