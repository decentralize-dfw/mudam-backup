from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R231_ERASMUS_CAM_BAGLANTI_ADAY_v001.blend'));d=json.loads((R/'config/r231_cross_link_measure.json').read_text());c=bpy.context.scene.camera;c.location=(141,403,20);c.rotation_euler=(Vector((124.5,424,5.5))-c.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();a=Vector((*d['start'],0));u=Vector((*d['axis'],0));n=-Vector((*d['trans'],0));a+=n*d['width']/2;direction=c.matrix_world.to_quaternion()@Vector((0,0,-1));rows=[]
for x,y in [(520,650),(600,660),(850,650),(940,625)]:
 start=c.matrix_world@Vector(((x/1400-.5)*27,(.5-y/1000)*27*1000/1400,0));hit=start+direction*(n.dot(a-start)/n.dot(direction));rows.append(dict(pixel=[x,y],along=u.dot(hit-a),z=hit.z))
(R/'config/r232_cross_bottom_projection.json').write_text(json.dumps(dict(samples=rows,source='R231_lower_court_source.png',limits='Visible bottom edge projected onto cross-link front plane; approximate, occluded central join excluded'),indent=2));print(rows)
