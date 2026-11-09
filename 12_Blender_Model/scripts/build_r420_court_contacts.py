import bpy,bmesh,json,math,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R419_GUNEY_KULE_AVLU_CEPHESI_ADAY_v001.blend'));raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());regions=[];records=[]
for t in raw['towers']:
 cx,cy=t['center'];r=t['radius'];regions.append([(cx+r*math.cos(i*math.tau/192),cy+r*math.sin(i*math.tau/192)) for i in range(192)])
src=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(a for a in src.body if isinstance(a,ast.FunctionDef) and a.name=='clip');loop=next(a for a in src.body if isinstance(a,ast.For) and isinstance(a.target,ast.Name) and a.target.id=='ob');exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));exec(compile(ast.unparse(loop).replace("['R152_CLASS2_TERRAIN']","['R154_FORT_ROUNDED_EARTH_ROOF']"),'<legacy disks>','exec'))
c=json.loads((R/'reports/R399_FRONT_COURT_PLANES.json').read_text())['tower_forecourt']['plane'];names=[]
# Fill the narrow 18 cm architectural body-to-existing roof-domain gap only.
# Plane is the measured low court, not inherited false z=2.9 roof.
for t in raw['towers']:
 if t['name']=='WEST':continue # inherited wide west foot still covers its junction
 cx,cy=t['center'];r=t['radius'];N=192;vs=[];fs=[]
 for rr,dz in [(r-.19,0),(r+.025,0),(r+.025,-.12),(r-.19,-.12)]:
  for i in range(N):a=i*math.tau/N;x=cx+rr*math.cos(a);y=cy+rr*math.sin(a);vs.append((x,y,c[0]*x+c[1]*y+c[2]-.012+dz))
 for k in range(4):
  for i in range(N):fs.append((k*N+i,k*N+(i+1)%N,((k+1)%4)*N+(i+1)%N,((k+1)%4)*N+i))
 name='R420_'+t['name']+'_LOW_COURT_CONTACT';me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials['R402_LOW_COURT_GRASS']);o['level_id']='SITE';o['source']='R399 measured court plane; annular contact between independent tower cylinder and R417 domain; no scan geometry.';bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();names.append(name)
out=R/'scenes/MUDAM_R420_KULE_AVLU_ESKI_ORTU_TEMIZLIGI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(x['nonManifold']==0 and x['zeroArea']==0 for x in checks)
(R/'reports/R420_COURT_CONTACTS.json').write_text(json.dumps(dict(scene=out.name,clipped=records,checks=checks,accepted=False,published=False,limits=['Removes demonstrated false legacy surface crossing south door. Does not establish source fidelity of provisional tower facade.','West tower architecture and other immediate ring tasks remain.']),indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-53,-47,4.6));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-57.4,-63.1,3.1))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=35;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R420_south_court_candidate.png');bpy.ops.render.render(write_still=True)
