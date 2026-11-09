exec(open('12_Blender_Model/scripts/render_r255_towers.py',encoding='utf-8-sig').read().split('s.camera.location=')[0])
s.camera.location=(90,570,65);s.camera.rotation_euler=(Vector((240,370,48))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=145;s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1600;s.render.resolution_y=1400;s.render.resolution_percentage=100
if not s.world:s.world=bpy.data.worlds.new('World')
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R260_towers_rear_source.png');bpy.ops.render.render(write_still=True)
