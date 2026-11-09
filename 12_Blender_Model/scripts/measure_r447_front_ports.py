import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R446_KALE_EGIMLI_BURC_GOVDESI_ADAY_v001.blend'));d=json.loads((R/'reports/R440_FRONT_PHOTO_CAMERA.json').read_text());eye=Vector(d['cameraParameters'][:3]);right,up,forward=map(Vector,d['basis']);f=d['focalPixels'];body=bpy.data.objects['R154_FORT_MASONRY_BODY'];inv=body.matrix_world.inverted();rows=[]
for label,px,py,w,h,shape in [('WEST_ROUND',194,423,23,23,'circle'),('SOUTH_ROUND',1055,434,23,23,'circle'),('WEST_SLIT_A',183,522,17,35,'rect'),('WEST_SLIT_B',278,527,20,37,'rect'),('WEST_SLIT_C',398,528,17,35,'rect'),('SOUTH_SLIT_A',873,535,17,34,'rect'),('SOUTH_SLIT_B',962,536,19,35,'rect'),('SOUTH_SLIT_C',1065,534,17,33,'rect'),('SOUTH_SLIT_D',1141,532,11,29,'rect'),('CURTAIN_HIGH',647,411,11,22,'rect'),('CURTAIN_LOW',646,509,11,22,'rect')]:
 ray=(forward+right*((px-640)/f)+up*((420-py)/f)).normalized();hit,p,n,i=body.ray_cast(inv@eye,inv.to_3x3()@ray);world=body.matrix_world@p;depth=(world-eye).dot(forward);rows.append(dict(label=label,pixel=[px,py],hit=hit,point=list(world),normal=list(body.matrix_world.to_3x3()@n),width=w*depth/f,height=h*depth/f,shape=shape))
(R/'reports/R447_PHOTO_OPENING_POSITIONS.json').write_text(json.dumps(rows,indent=2));print(rows)
