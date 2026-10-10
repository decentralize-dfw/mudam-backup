from pathlib import Path
import bpy,json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R146_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
for name in r['materials']:
 m=bpy.data.materials[name];print(name)
 for n in m.node_tree.nodes:
  print(n.type,n.name,getattr(n,'uv_map',''),[(x.name,str(x.default_value)) for x in n.inputs if not x.is_linked and hasattr(x,'default_value')][:3])
 print([(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])

o=bpy.data.objects['P11_WEST_STONE_BASE_10'];print('OBJECT',o.name,[(x.link,x.material.name) for x in o.material_slots],[(p.index,p.material_index) for p in o.data.polygons],[(m.name,m.type) for m in o.modifiers]);print('OVERRIDE',bpy.context.view_layer.material_override);print('UV',[(u.name,u.active_render) for u in o.data.uv_layers]);print('FACE3UV',[list(o.data.uv_layers['R146_STONE_METRIC_UV'].data[i].uv) for i in o.data.polygons[3].loop_indices])

for name in r['materials']:
 m=bpy.data.materials[name];print('USE',name,m.use_nodes);print([(n.image.name,n.extension,n.image.size[:]) for n in m.node_tree.nodes if n.type=='TEX_IMAGE'])

print('VIEW',bpy.context.scene.view_settings.view_transform,bpy.context.scene.view_settings.look,bpy.context.scene.view_settings.exposure);print('WORLD',[(n.name,n.type) for n in bpy.context.scene.world.node_tree.nodes]);print('SUN',[(o.name,o.data.energy) for o in bpy.context.scene.objects if o.type=='LIGHT'])
