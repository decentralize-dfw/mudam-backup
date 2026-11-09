import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R406_KALE_DOGU_TAS_ACIKLIK_DETAYI_ADAY_v001.blend'));raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());q=next(t for t in raw['towers'] if t['name']=='CENTRE');cx,cy=q['center'];r=q['radius']-.18;roof=q['roof'];c=json.loads((R/'reports/R399_FRONT_COURT_PLANES.json').read_text())['tower_forecourt']['plane'];base=c[0]*cx+c[1]*cy+c[2]-.06;stone=bpy.data.materials['R154_FORT_STONE_PBR'];dressed=bpy.data.materials['R406_FORT_DRESSED_SANDSTONE'];names=[]
def mesh(name,vs,fs,ma):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(ma);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o['level_id']='SITE';names.append(name)
 uv=me.uv_layers.new(name='UVMap')
 for l in me.loops:
  p=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(math.atan2(p.y-cy,p.x-cx)*r/4,p.z/4)
 return o
for name in ['R154_TOWER_CENTRE','R154_TOWER_LOWER_COPING_CENTRE']:
 o=bpy.data.objects[name];o.hide_render=True;o.hide_viewport=True;o.hide_set(True);o['R407_replaced']='Photo-supported continuous tower foot reaches low courtyard; no broad projecting interior base ring in source photo.'
profile=[(r,base),(r,roof-.6),(q['radius']+.08,roof-.4),(q['radius']+.17,roof-.25),(q['radius']+.17,roof)];N=96;vs=[(cx+rr*math.cos(math.tau*i/N),cy+rr*math.sin(math.tau*i/N),z) for rr,z in profile for i in range(N)];fs=[list(range(N-1,-1,-1)),list(range((len(profile)-1)*N,len(profile)*N))]
for k in range(len(profile)-1):fs.extend([(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for i in range(N)])
tower=mesh('R407_CENTRAL_TOWER_BODY',vs,fs,stone)
def cut_window(phi,width,lo,hi):
 normal=Vector((math.cos(phi),math.sin(phi),0));tangent=Vector((-normal.y,normal.x,0));p=Vector((cx,cy,0))+normal*r;vs=[tuple(p+tangent*x+normal*depth+Vector((0,0,z))) for depth in [-.5,.2] for x,z in [(-width/2,lo),(width/2,lo),(width/2,hi),(-width/2,hi)]];o=mesh('R407_TEMP_CUT',vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone);bpy.context.view_layer.objects.active=tower;mod=tower.modifiers.new('Photo visible rectangular recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=o;bpy.ops.object.modifier_apply(modifier=mod.name);names.remove(o.name);bpy.data.objects.remove(o,do_unlink=True)
angles=[math.radians(a) for a in [5,45,85]]
for a in angles:cut_window(a,.48,base+.5,base+1.55)
# Preserve the inherited three exterior-facing slit locations as provisional;
# this correction addresses the photographed court-facing side only.
oldangle=math.atan2(-raw['direction'][1],-raw['direction'][0])
for j in [-1,0,1]:cut_window(oldangle+j*.44,.32,roof-1.525,roof-.675)
vs=[];fs=[]
def stonepiece(poly,phi):
 k=len(poly);start=len(vs)
 for dep in [-.01,.13]:
  for x,z in poly:
   a=phi+x/r;vs.append((cx+(r+dep)*math.cos(a),cy+(r+dep)*math.sin(a),z))
 fs.extend([[start+i for i in range(k-1,-1,-1)],[start+k+i for i in range(k)]]);fs.extend([(start+i,start+(i+1)%k,start+(i+1)%k+k,start+i+k) for i in range(k)])
spring=roof-1.34
for phi in angles:
 for j in range(12):
  a=math.pi*j/12;b=math.pi*(j+1)/12;stonepiece([(.56*math.cos(a),spring+.56*math.sin(a)),(.56*math.cos(b),spring+.56*math.sin(b)),(.73*math.cos(b),spring+.73*math.sin(b)),(.73*math.cos(a),spring+.73*math.sin(a))],phi)
 for sign in [-1,1]:
  stonepiece([(sign*.56,base),(sign*.73,base),(sign*.73,spring),(sign*.56,spring)],phi)
  stonepiece([(sign*.47,spring-.16),(sign*.82,spring-.16),(sign*.82,spring),(sign*.47,spring)],phi)
mesh('R407_CENTRAL_TOWER_BLIND_ARCADES',vs,fs,dressed)
out=R/'scenes/MUDAM_R407_KALE_ORTA_KULE_AVLU_BAGLANTISI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(x['nonManifold'] or x['zeroArea'] for x in checks),checks
(R/'reports/R407_CENTRAL_TOWER.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,base=base,checks=checks,source='Zinneke rooftop views 1 and 2; classified court plane R399; inherited tower footprint and cap level.',limits=['Court-facing three bays are photo-proportioned, not surveyed. Other sides remain provisional; no complete tower or ring acceptance.','Outer towers, end shoulders and other marked museum boundaries remain incomplete.']),indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-46,-37,5.4));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((cx,cy,3.1))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=45;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R407_central_tower_candidate.png');bpy.ops.render.render(write_still=True);print('R407_READY')
