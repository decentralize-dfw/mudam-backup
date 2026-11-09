import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R439_KOPRU_BASI_ZEMIN_BAGLANTISI_ADAY_v001.blend'));raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());fits={x['tower']:x for x in json.loads((R/'reports/R445_CLASS1_BASTION_FITS.json').read_text())};body=bpy.data.objects['R154_FORT_MASONRY_BODY'];front=Vector((-raw['direction'][0],-raw['direction'][1]));records=[];cplane=json.loads((R/'reports/R399_FRONT_COURT_PLANES.json').read_text())['tower_forecourt']['plane']
# Only exterior arc columns; window/door-cut vertices on straight curtain are excluded.
for t in raw['towers']:
 if t['name']=='CENTRE':continue
 cx,cy=t['center'];fit=fits[t['name']]['fit'];foot=[Vector((x,y)) for x,y in raw['footprint'] if 5.2<math.hypot(x-cx,y-cy)<5.6];changes=[]
 for v in body.data.vertices:
  q=body.matrix_world@v.co;p=Vector((q.x,q.y));nearest=min(foot,key=lambda a:(a-p).length)
  if (nearest-p).length>1e-3:continue
  delta=p-Vector((cx,cy));rad=delta.length;angle=math.acos(max(-1,min(1,delta.normalized().dot(front))));w=max(0,min(1,(math.radians(120)-angle)/math.radians(45)));w=w*w*(3-2*w)
  if w==0:continue
  rr=fit[2]+fit[3]*q.z;target=Vector(fit[:2])+delta.normalized()*rr;old=list(q);q.x+=(target.x-q.x)*w;q.y+=(target.y-q.y)*w;v.co=body.matrix_world.inverted()@q;changes.append(dict(index=v.index,before=old,after=list(q),weight=w))
 records.append(dict(tower=t['name'],changes=changes,profile=fit))
body.data.update()
# Exterior structural corbel belt meets the revised battered body and existing upper tower.
ma=bpy.data.materials['R406_FORT_DRESSED_SANDSTONE'];names=[]
for t in raw['towers']:
 if t['name']=='CENTRE':continue
 cx,cy=t['center'];fit=fits[t['name']]['fit'];z=cplane[0]*cx+cplane[1]*cy+cplane[2]-.06;r=t['radius']-.18;N=96;phi=math.atan2(front.y,front.x);vs=[]
 for band in range(4):
  for i in range(N+1):
   a=phi-math.pi/2+i*math.pi/N;u=Vector((math.cos(a),math.sin(a)));lo=z-.38;low=Vector(fit[:2])+u*(fit[2]+fit[3]*lo);outer=Vector((cx,cy))+u*(r+.32);inner=Vector((cx,cy))+u*(r-.35)
   xy,zz=[(low,lo),(outer,z-.12),(outer,z+.02),(inner,z+.02)][band];vs.append((xy.x,xy.y,zz))
 fs=[]
 for k in range(3):
  for i in range(N):a=k*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
 for i in range(N):fs.append((i,3*(N+1)+i,3*(N+1)+i+1,i+1))
 fs.extend([(0,N+1,2*(N+1),3*(N+1)),(N,4*N+3,3*N+2,2*N+1)])
 name='R446_'+t['name']+'_CORBEL_BELT';me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(ma);o['level_id']='SITE';o['source']='Independent architectural transition from R445 robust lower profile to existing tower; not scan mesh. Profile maximum residuals still include unverified points.';names.append(name);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 old=bpy.data.objects['R424_'+t['name']+'_EXTERIOR_BASE_COPING'];old.hide_render=True;old.hide_viewport=True;old.hide_set(True)
# No change to court/earth cover yet: render identifies any mismatch before accepting altered silhouette.
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));boundary=sum(e.is_boundary for e in bm.edges);bm.to_mesh(body.data);bm.free();assert boundary==70
out=R/'scenes/MUDAM_R446_KALE_EGIMLI_BURC_GOVDESI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R446_BATTERED_BASTIONS.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changes=records,checks=checks,limits=['Architectural profile candidate supported by photograph taper; R445 full maximum-distance test failed, not survey acceptance.','Front arc only; rear contacts and earth cover require visual check before adoption.']),indent=2));print('R446_SAVED',flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-107,-92,6));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-63,-54,1.7))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=50;s.render.filepath=str(R/'renders/qa/R446_front_candidate.png');bpy.ops.render.render(write_still=True)
