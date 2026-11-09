import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R403_KALE_CATI_ERISIM_ACIKLIGI_ADAY_v001.blend'));raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());outline=raw['footprint'];body=bpy.data.objects['R154_FORT_MASONRY_BODY'];records=[]
# Recover the precise orthographic camera used for the source reference.
eye=Vector((0,-90,-.5));target=Vector((-39,-42,-.5));direction=(target-eye).normalized();right=direction.cross(Vector((0,0,1))).normalized()
def cross(a,b):return a.x*b.y-a.y*b.x
def locate(px,py):
 origin=eye+right*((px-800)*55/1600)+Vector((0,0,(400-py)*55/1600));hits=[]
 for i in range(43,50):
  a,b=Vector(outline[i]),Vector(outline[i+1]);v=b-a;den=cross(direction.to_2d(),v)
  if abs(den)<1e-8:continue
  u=cross(a-origin.to_2d(),direction.to_2d())/den;t=cross(a-origin.to_2d(),v)/den
  if 0<=u<=1 and t>0:
   p=origin+direction*t;tan=Vector((v.x,v.y,0)).normalized();normal=Vector((tan.y,-tan.x,0))
   if normal.dot(eye-p)<0:normal=-normal
   hits.append((t,p,tan,normal,i))
 if not hits:raise ValueError(('source pixel misses selected wall',px,py))
 return min(hits,key=lambda x:x[0])[1:]
# Temporary closure exists solely to make true recess Boolean operands robust.
# It is removed after cutting; the independent roof remains the assembly cap.
bm=bmesh.new();bm.from_mesh(body.data);boundary=[e for e in bm.edges if e.is_boundary];baseline=len(boundary);capmat=bpy.data.materials.new('R405_TEMP_CAP');body.data.materials.append(capmat);capindex=len(body.data.materials)-1
filled=bmesh.ops.holes_fill(bm,edges=boundary,sides=0)['faces']
for f in filled:f.material_index=capindex
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()
def cutter(shape,p,t,n):
 vs=[tuple(p+t*x+n*d+Vector((0,0,z))) for d in [-.55,.2] for x,z in shape];k=len(shape);fs=[list(range(k-1,-1,-1)),list(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)];me=bpy.data.meshes.new('R405_CUT');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('R405_CUT',me);bpy.context.scene.collection.objects.link(ob);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('R405_photo_supported_recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=ob;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(ob,do_unlink=True)
for px,py in [(233,444),(448,447),(656,449),(861,447),(1063,446)]:
 p,t,n,seg=locate(px,py);shape=[(.34*math.cos(math.tau*j/32),.34*math.sin(math.tau*j/32)) for j in range(32)];cutter(shape,p,t,n);records.append(dict(kind='round_opening',pixel=[px,py],center=list(p),wallSegment=seg,radius=.34))
for px in [241,451,656,860,1061]:
 p,t,n,seg=locate(px,526);shape=[(-.575,-.72),(.575,-.72)]+[(.575*math.cos(math.pi*j/16),.40+.30*math.sin(math.pi*j/16)) for j in range(17)];cutter(shape,p,t,n);records.append(dict(kind='segmental_arch_recess',pixel=[px,526],center=list(p),wallSegment=seg,width=1.15))
for px in [183,309,392,509,596,714,797,924,1000]:
 p,t,n,seg=locate(px,532);cutter([(-.19,-.48),(.19,-.48),(.19,.48),(-.19,.48)],p,t,n);records.append(dict(kind='narrow_recess',pixel=[px,532],center=list(p),wallSegment=seg,width=.38))
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index==capindex],context='FACES');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);check=dict(boundaryEdges=sum(e.is_boundary for e in bm.edges),otherNonManifold=sum(not e.is_manifold and not e.is_boundary for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces),baselineBoundary=baseline);bm.free()
body['R405_source']='Independent wall openings: ACT orthographic R404 clipped reference locates them; architectural form confirmed by source photo086. No scan geometry or photo texture transferred.'
out=R/'scenes/MUDAM_R405_KALE_DOGU_DUVAR_ACIKLIKLARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));report=dict(scene=out.name,accepted=False,published=False,openings=records,check=check,limits=['Opening centers from low-resolution scan visual reference, forms from photo086. Dimensions have visual uncertainty; rear depth 0.55m is not surveyed.','Only the visible five bays reconstructed; adjoining wall and tower details remain incomplete.']);(R/'reports/R405_WALL_OPENINGS.json').write_text(json.dumps(report,indent=2));assert check['boundaryEdges']==baseline and check['otherNonManifold']==0 and check['zeroArea']==0,check
# Compare only the relevant facade, keeping this visibility setup out of saved master.
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and ob.name!='R154_FORT_MASONRY_BODY':ob.hide_render=True
s=bpy.context.scene;bpy.ops.object.camera_add(location=eye);s.camera=bpy.context.object;s.camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=55;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R405_fort_east_wall_candidate.png');bpy.ops.render.render(write_still=True);print('R405_READY')
