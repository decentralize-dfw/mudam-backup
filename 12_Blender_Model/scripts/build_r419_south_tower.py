import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R418_KALE_OLCULU_KULE_CATILARI_ADAY_v001.blend'));raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());q=next(t for t in raw['towers'] if t['name']=='SOUTH');cx,cy=q['center'];r=q['radius']-.18;fit=json.loads((R/'reports/R418_TOWER_CAP_PLANES.json').read_text())['SOUTH']['coef'];roof=fit[0]+fit[1]*(q['radius']+.2);c=json.loads((R/'reports/R399_FRONT_COURT_PLANES.json').read_text())['tower_forecourt']['plane'];base=c[0]*cx+c[1]*cy+c[2]-.06;stone=bpy.data.materials['R154_FORT_STONE_PBR'];dressed=bpy.data.materials['R406_FORT_DRESSED_SANDSTONE'];names=[]
def mesh(name,vs,fs,ma):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(ma);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o['level_id']='SITE';names.append(name)
 uv=me.uv_layers.new(name='UVMap')
 for l in me.loops:
  p=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(math.atan2(p.y-cy,p.x-cx)*r/1.6,p.z/1.6)
 return o
for name in ['R154_TOWER_SOUTH','R154_TOWER_LOWER_COPING_SOUTH','R408_SOUTH_TOWER_COURT_FOOT']:
 o=bpy.data.objects[name];o.hide_render=True;o.hide_viewport=True;o.hide_set(True);o['R419_replaced']='Photo-supported continuous tower foot reaches low courtyard; no broad projecting interior base ring in source photo.'
profile=[(r,base),(r,roof-.30),(q['radius']+.08,roof-.20),(q['radius']+.17,roof-.12),(q['radius']+.17,roof)];N=192;vs=[(cx+rr*math.cos(math.tau*i/N),cy+rr*math.sin(math.tau*i/N),z) for rr,z in profile for i in range(N)];fs=[list(range(N-1,-1,-1)),list(range((len(profile)-1)*N,len(profile)*N))]
for k in range(len(profile)-1):fs.extend([(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for i in range(N)])
tower=mesh('R419_SOUTH_TOWER_BODY',vs,fs,stone)
def cut_window(phi,width,lo,hi):
 normal=Vector((math.cos(phi),math.sin(phi),0));tangent=Vector((-normal.y,normal.x,0));p=Vector((cx,cy,0))+normal*r;vs=[tuple(p+tangent*x+normal*depth+Vector((0,0,z))) for depth in [-.5,.2] for x,z in [(-width/2,lo),(width/2,lo),(width/2,hi),(-width/2,hi)]];o=mesh('R419_TEMP_CUT',vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone);bpy.context.view_layer.objects.active=tower;mod=tower.modifiers.new('Photo visible rectangular recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=o;bpy.ops.object.modifier_apply(modifier=mod.name);names.remove(o.name);bpy.data.objects.remove(o,do_unlink=True)
angles=[math.radians(a) for a in [48,72,96,120,144]]
for i,a in enumerate(angles):cut_window(a,1.0 if i==3 else .48,base+.04 if i==3 else base+.55,base+2.16 if i==3 else base+1.62)
# Preserve the inherited three exterior-facing slit locations as provisional;
# this correction addresses the photographed court-facing side only.
oldangle=math.atan2(-raw['direction'][1],-raw['direction'][0])
for j in [-1,0,1]:cut_window(oldangle+j*.44,.32,roof-1.525,roof-.675)
vs=[];fs=[]
def stonepiece(poly,phi):
 k=len(poly);start=len(vs)
 for dep in [-.01,.045]:
  for x,z in poly:
   a=phi+x/r;vs.append((cx+(r+dep)*math.cos(a),cy+(r+dep)*math.sin(a),z))
 fs.extend([[start+i for i in range(k-1,-1,-1)],[start+k+i for i in range(k)]]);fs.extend([(start+i,start+(i+1)%k,start+(i+1)%k+k,start+i+k) for i in range(k)])
spring=roof-1.25
for phi in angles:
 for j in range(12):
  a=math.pi*j/12+.003;b=math.pi*(j+1)/12-.003;stonepiece([(.64*math.cos(a),spring+.64*math.sin(a)),(.64*math.cos(b),spring+.64*math.sin(b)),(.83*math.cos(b),spring+.83*math.sin(b)),(.83*math.cos(a),spring+.83*math.sin(a))],phi)
 for sign in [-1,1]:
  stonepiece([(sign*.64,base),(sign*.83,base),(sign*.83,spring),(sign*.64,spring)],phi)
  stonepiece([(sign*.54,spring-.16),(sign*.92,spring-.16),(sign*.92,spring),(sign*.54,spring)],phi)
mesh('R419_SOUTH_TOWER_BLIND_ARCADES',vs,fs,dressed)
# Photo 1: one full-height door among narrow window bays; orientation provisional.
phi=angles[3];normal=Vector((math.cos(phi),math.sin(phi),0));tangent=Vector((-normal.y,normal.x,0));origin=Vector((cx,cy,0))+normal*(r-.46)
doorMat=bpy.data.materials.new('R419_DARK_DOOR');doorMat.diffuse_color=(.055,.065,.058,1);doorMat.use_nodes=True;doorMat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.055,.065,.058,1)
dv=[tuple(origin+tangent*x+normal*d+Vector((0,0,z))) for d in [0,.06] for x,z in [(-.47,base+.06),(.47,base+.06),(.47,base+2.13),(-.47,base+2.13)]]
mesh('R419_SOUTH_RECESSED_DOOR',dv,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],doorMat)
vs=[];fs=[]
for i,phi in enumerate(angles):
 w=1.0 if i==3 else .48;lo=base+.04 if i==3 else base+.55;hi=base+2.16 if i==3 else base+1.62
 for sign in [-1,1]:
  x=sign*w/2;y=x+sign*.15;stonepiece([(x,lo),(y,lo),(y,hi+.14),(x,hi+.14)],phi)
 stonepiece([(-w/2,hi),(w/2,hi),(w/2,hi+.14),(-w/2,hi+.14)],phi)
 stonepiece([(-w/2-.15,lo-.10),(w/2+.15,lo-.10),(w/2+.15,lo),(-w/2-.15,lo)],phi)
mesh('R419_SOUTH_OPENING_JAMBS',vs,fs,dressed)
out=R/'scenes/MUDAM_R419_GUNEY_KULE_AVLU_CEPHESI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(x['nonManifold'] or x['zeroArea'] for x in checks),checks
(R/'reports/R419_SOUTH_TOWER.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,base=base,checks=checks,source='Zinneke rooftop views 1 and 2; classified court plane R399; inherited tower footprint and cap level.',limits=['Five court-facing bays and door follow visible photographic typology. Angular positions 48/72/96/120/144 degrees and opening dimensions are provisional visual estimates; scan is torn/occluded. NOT source-position accepted.','West tower architecture, south bay alignment, material fidelity and other marked boundaries remain incomplete. R418 measured south roof is unchanged; no scan mesh or photo texture transferred.']),indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-53,-47,4.6));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((cx,cy,3.1))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=35;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R419_south_tower_candidate.png');bpy.ops.render.render(write_still=True);print('R419_READY')
