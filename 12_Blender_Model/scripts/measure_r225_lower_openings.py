from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R220_ERASMUS_ARKA_BAGLANTI_ADAY_v001.blend'));cam=bpy.context.scene.camera;cam.location=(171,366,27);cam.rotation_euler=(Vector((126,414,6))-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
p=json.loads((R/'config/r218_front_volumes_measured.json').read_text())['parts'][1]['polygon'];a=Vector((*p[3],0));b=Vector((*p[2],0));u=(b-a).normalized();n=Vector((u.y,-u.x,0));direction=cam.matrix_world.to_quaternion()@Vector((0,0,-1));rects=[(856,600,886,696),(909,600,939,699),(962,601,991,703),(1013,603,1044,706),(1066,604,1096,708),(1118,605,1147,710),(1168,606,1197,712),(842,580,1205,724)];rows=[]
for r in rects:
 pts=[]
 for x,y in [(r[0],r[1]),(r[2],r[1]),(r[2],r[3]),(r[0],r[3])]:
  start=cam.matrix_world@Vector(((x/1400-.5)*65,(.5-y/1000)*65*1000/1400,0));t=n.dot(a-start)/n.dot(direction);hit=start+direction*t;pts.append((u.dot(hit-a),hit.z))
 rows.append(dict(pixelRect=r,u0=min(v[0]for v in pts),u1=max(v[0]for v in pts),z0=min(v[1]for v in pts),z1=max(v[1]for v in pts)))
(R/'config/r225_lower_openings_projected.json').write_text(json.dumps(dict(wallLength=(b-a).length,origin=list(a),u=list(u),normal=list(n),openings=rows,source='R221_erasmus_front_source.png',method='Manually observed window rectangles projected onto independently modeled facade plane; approximate scan bounds'),indent=2));print(rows,flush=True)


