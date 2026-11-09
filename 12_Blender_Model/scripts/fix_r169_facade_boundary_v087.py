from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_ARKA_ACIKLIKLAR_v080.blend'));center=Vector((-81.746925354,-294.516082764,-69));right=Vector((-.97769629955,-.2100233883,0));n=Vector((-.2100236565,.97769629955,0));o=bpy.data.objects['ARCH_WALL_MASS_0'];mat=o.data.materials[0]
def screen(p):return 1024+(p-center).dot(right)*2048/36
def depth(x):return -1.28 if x<700 else (-.74 if x>1200 else 0)
bm=bmesh.new();bm.from_mesh(o.data)
for x in [700,1200]:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=center+right*((x-1024)*36/2048),plane_no=right,clear_inner=False,clear_outer=False)
vv=[];ff=[]
for f in bm.faces:
 move=n*depth(screen(f.calc_center_median()));base=len(vv);vv.extend([v.co+move for v in f.verts]);ff.append(tuple(range(base,len(vv))))
bm.free()
for x in [700,1200]:
 p=center+right*((x-1024)*36/2048);dl=depth(x-.01);dr=depth(x+.01);base=len(vv);vv.extend([Vector((p.x,p.y,z))+n*d for z,d in [(-75,dl),(-75,dr),(-65.1,dr),(-65.1,dl)]]);ff.append(tuple(range(base,base+4)))
me=bpy.data.meshes.new('Measured stepped rear facade');me.from_pydata(vv,[],ff);me.update();o.data=me;me.materials.append(mat)
# These four rear aperture groups belong to the main rear wall; projection apertures retain positions.
for ob in bpy.context.scene.objects:
 if not any(ob.name.startswith(p) for p in ['ARCH_REAR_GLAZING_','ARCH_REAR_FRAME_','ARCH_REAR_FRAME_H_']):continue
 suffix=ob.name.replace('ARCH_REAR_GLAZING_','').replace('ARCH_REAR_FRAME_H_','').replace('ARCH_REAR_FRAME_','');idx=int(suffix.split('_')[0])
 if idx>=4:continue
 mean=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices);move=n*depth(screen(mean))
 for v in ob.data.vertices:v.co+=move
s=bpy.context.scene;s['acceptance']='Unaccepted architectural WIP. Rear side fields have independent measured offsets; transitions at house boundaries remain provisional.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_CEPHE_SINIRI_v087.blend'));target=Vector((-80,-301,-66));s.camera.location=target+Vector((-20,31,30));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/qa/R169_architectural_rear_v081.png');pass
(R/'reports/R169_ARCHITECTURAL_REAR_STEP_v087.json').write_text(json.dumps(dict(accepted=False,offsets=[-1.28,0,-.74],evidence='rear_body_measurements_v081.json: coherent vertical source patches x470/490 and1850/1870',limits='House transition pixel700/1200 remains provisional; left balcony projection separately required. No global fidelity claim.'),indent=2));print('STEPPED_REAR_SAVED')
