import bpy,json,re,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R557_KUZEY_YAKLASIM_ZEMIN_BUTUNLUGU_ADAY_v001.blend'));original=bpy.context.scene
targets=[]
for o in original.objects:
 if o.type!='MESH' or o.hide_render:continue
 if any(m and m.name in ['R554_WEATHERED_COURSED_STONE_CC0','R545_DRY_EARTH_PATCHY_TURF'] for m in o.data.materials):targets.append(o)
vs=[];fs=[];mapping=[]
for o in targets:
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in p.vertices)for p in o.data.polygons);mapping.extend((o.name,l.index)for l in o.data.loops)
scene=bpy.data.scenes.new('R561_TEMP_AO_BAKE');bpy.context.window.scene=scene
me=bpy.data.meshes.new('R561_ATLAS_TEMP');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(me.name,me);scene.collection.objects.link(ob)
# Nearby solids provide contact occlusion without duplicating bake targets.
names={o.name for o in targets};occluders=0
for o in original.objects:
 if o.type!='MESH' or o.hide_render or o.name in names or o.name.startswith('R158_TREE_'):continue
 bb=[o.matrix_world@Vector(v)for v in o.bound_box]
 if max(v.x for v in bb)<-90 or min(v.x for v in bb)>90 or max(v.y for v in bb)<-95 or min(v.y for v in bb)>95:continue
 scene.collection.objects.link(o);occluders+=1

for item in scene.objects:item.select_set(False)
bpy.context.view_layer.objects.active=ob;ob.select_set(True);me.uv_layers.new(name='R561_AO_ATLAS');bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.004);bpy.ops.object.mode_set(mode='OBJECT')
img=bpy.data.images.new('R561_MUSEUM_RING_CONTACT_AO',width=2048,height=2048,alpha=False);img.colorspace_settings.name='Non-Color'
m=bpy.data.materials.new('R561_TEMP_AO_SHADER');m.use_nodes=True;nd=m.node_tree.nodes;nd.clear();out=nd.new('ShaderNodeOutputMaterial');em=nd.new('ShaderNodeEmission');ao=nd.new('ShaderNodeAmbientOcclusion');ao.samples=16;ao.inputs['Distance'].default_value=2;tx=nd.new('ShaderNodeTexImage');tx.image=img;nd.active=tx;m.node_tree.links.new(ao.outputs['Color'],em.inputs['Color']);m.node_tree.links.new(em.outputs[0],out.inputs['Surface']);me.materials.append(m)
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.bake.margin=8;scene.render.bake.use_clear=True
print('BAKING',len(targets),len(fs),occluders,flush=True);bpy.ops.object.bake(type='EMIT');img.filepath_raw=str(R/'textures/R561_museum_ring_contact_ao.png');img.file_format='PNG';img.save()
# Transfer the unique atlas coordinates back, preserving original geometry and existing UVs.
for o in targets:o.data.uv_layers.new(name='R561_AO_ATLAS')
for i,(name,li)in enumerate(mapping):bpy.data.objects[name].data.uv_layers['R561_AO_ATLAS'].data[li].uv=me.uv_layers['R561_AO_ATLAS'].data[i].uv
ng=bpy.data.node_groups.new('glTF Material Output R561','ShaderNodeTree');ng.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat');copies={}
for o in targets:
 for i,mat in enumerate(o.data.materials):
  if not mat:continue
  if mat.name not in copies:
   cp=mat.copy();cp.name=mat.name+'_R561_AO';cp.use_nodes=True;nd=cp.node_tree.nodes;lk=cp.node_tree.links;uv=nd.new('ShaderNodeUVMap');uv.uv_map='R561_AO_ATLAS';tex=nd.new('ShaderNodeTexImage');tex.image=img;lk.new(uv.outputs[0],tex.inputs[0]);g=nd.new('ShaderNodeGroup');g.node_tree=ng;lk.new(tex.outputs['Color'],g.inputs['Occlusion']);copies[mat.name]=cp
  o.data.materials[i]=copies[mat.name]
bpy.context.window.scene=original;bpy.data.scenes.remove(scene);bpy.data.objects.remove(ob,do_unlink=True)
out=R/'scenes/MUDAM_R561_SUR_ZEMIN_TEMAS_AO_BAKE_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in sorted(names):
 o=bpy.data.objects[name];uv=o.data.uv_layers['R561_AO_ATLAS'];assert all(math.isfinite(c)and -.00001<=c<=1.00001 for u in uv.data for c in u.uv);checks.append(dict(name=name,loops=len(uv.data)))
(R/'reports/R561_BUILD.json').write_text(json.dumps(dict(reopened=True,targets=checks,occluders=occluders,image='textures/R561_museum_ring_contact_ao.png',aoDistanceMetres=2,geometryChanged=False,lighting='Contact ambient occlusion only; dynamic sun lighting remains live.',accepted=False,published=False),indent=2));print('R561_SAVED',len(checks),flush=True)
