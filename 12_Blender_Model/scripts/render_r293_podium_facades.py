import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r166/source.blend'))
s=bpy.context.scene;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.render.engine='CYCLES';s.world=bpy.data.worlds.new('Reference');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
s.camera.data.type='ORTHO';s.camera.data.ortho_scale=145;s.render.resolution_x=2000;s.render.resolution_y=650;s.render.resolution_percentage=100;s.cycles.samples=4
for label,a,b,sign in [('road',(189.375,24.375),(255,126.375),1),('forest',(189.375,24.375),(302.25,95.25),-1)]:
 a=Vector((*a,17));b=Vector((*b,17));u=(b-a).normalized();normal=Vector((-u.y,u.x,0))*sign;target=(a+b)/2;s.camera.location=target+normal*150;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/f'renders/qa/R293_podium_{label}_source.png');bpy.ops.render.render(write_still=True)
