exec(open('12_Blender_Model/scripts/render_r255_towers.py',encoding='utf-8-sig').read().split('s.camera.location=')[0])
s.camera.location=(246,408,220);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=70;s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100
if not s.world:s.world=bpy.data.worlds.new('World')
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R256_tower_b_source_top.png');bpy.ops.render.render(write_still=True)
