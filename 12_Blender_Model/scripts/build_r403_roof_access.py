import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R402_KALE_ALCAK_KULE_AVLUSU_ADAY_v001.blend'))
px=[(273,787),(336,735),(353,752),(291,804)];xy=[Vector((-74.5+x*65/1100,-1.5-y*65/1100)) for x,y in px];c=json.loads((R/'reports/R387_ROOF_INPUT.json').read_text())['lowerPlane'];z=lambda p:c[0]*p.x+c[1]*p.y+c[2]
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o)
 if mat:me.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o['level_id']='SITE';return o
vs=[(p.x,p.y,z(p)+h) for h in [-.5,.5] for p in xy];faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];cut=mesh('R403_TEMP_ACCESS_CUT',vs,faces,None);changed=[]
for name in ['R389_FORT_LOWER_METAL_ROOF','R401_FORT_OPEN_END_TIMBER_DECK','R400_TIMBER_DECK_JOINTS']:
 o=bpy.data.objects[name];bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('R403_source_visible_roof_access','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);changed.append(name)
bpy.data.objects.remove(cut,do_unlink=True)
vs=[];fs=[]
def beam(a,b,width):
 a,b=Vector(a),Vector(b);t=(b-a).normalized();ref=Vector((0,0,1)) if abs(t.z)<.9 else Vector((1,0,0));u=t.cross(ref).normalized()*width/2;v=t.cross(u).normalized()*width/2;i=len(vs);vs.extend(tuple(q) for q in [a-u-v,b-u-v,b+u-v,a+u-v,a-u+v,b-u+v,b+u+v,a+u+v]);fs.extend([[i+j for j in f] for f in faces])
for i,p in enumerate(xy):
 q=xy[(i+1)%4];a=Vector((p.x,p.y,z(p)));b=Vector((q.x,q.y,z(q)));beam(a,b,.06)
 for h in [.12,1.05]:beam(a+Vector((0,0,h)),b+Vector((0,0,h)),.035)
 count=max(1,round((q-p).length/.13))
 for j in range(count+1):
  v=a.lerp(b,j/count);beam(v+Vector((0,0,.05)),v+Vector((0,0,1.05)),.025 if j not in [0,count] else .05)
o=mesh('R403_FORT_ROOF_ACCESS_GUARD',vs,fs,bpy.data.materials['R400_DARK_LOUVER_FRAMES']);o['source']='R336 roof-plan opening outline; Zinneke rooftop view 2 railing. Independently modeled. Nominal 1.05m guard height and 0.13m bar spacing are visual estimates, not surveyed.';changed.append(o.name)
out=R/'scenes/MUDAM_R403_KALE_CATI_ERISIM_ACIKLIGI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in changed:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
report=dict(scene=out.name,accepted=False,published=False,sourcePixels=px,checks=checks,limits=['Only source-visible roof opening and guard reconstructed. Interior staircase depth and lower landing are not visible in these sources and are not claimed complete.','Railing dimensions are photo-derived nominal modeling values. Whole marked perimeter remains incomplete.']);(R/'reports/R403_ROOF_ACCESS.json').write_text(json.dumps(report,indent=2));assert not any(x['nonManifold'] or x['zeroArea'] for x in checks),checks
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-28,-20,4));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-61.6,-53.15,2.8))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=28;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=667;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R403_rooftop_eye_candidate.png');bpy.ops.render.render(write_still=True);print('R403_READY')
