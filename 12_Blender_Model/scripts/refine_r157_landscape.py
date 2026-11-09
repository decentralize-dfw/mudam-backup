from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R157_ARAZI_YOLLAR_AGACLAR_v001.blend'));s=bpy.context.scene
# Normalize outdoor preview light; inherited Nishita illumination washed out terrain and vegetation.
s.world=bpy.data.worlds.new('R157_OUTDOOR_WORLD');s.world.use_nodes=True;bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.60,.72,.85,1);bg.inputs['Strength'].default_value=.4;s.view_settings.exposure=0
sun=bpy.data.objects.get('QA_SUN');sun.data.energy=2.2;sun.data.angle=.08
for o in s.objects:
 if o.type=='MESH' and o.name=='R154_FORT_ROUNDED_EARTH_ROOF':
  o.data.materials.clear();o.data.materials.append(bpy.data.materials['R157_CONTINUOUS_LANDCOVER'])
  for l in list(o.data.uv_layers):o.data.uv_layers.remove(l)
  atlas=o.data.uv_layers.new(name='UVMap');micro=o.data.uv_layers.new(name='MicroUV');o.data.uv_layers.active=atlas
  for li,loop in enumerate(o.data.loops):
   q=o.matrix_world@o.data.vertices[loop.vertex_index].co;atlas.data[li].uv=((q.x+500)/1150,(q.y+450)/1100);micro.data[li].uv=(q.x/2,q.y/2)
for label,eye,target in [('near',(150,-210,110),(0,-10,0)),('park',(-145,-210,65),(-45,-45,-5)),('far',(650,-710,610),(55,75,-8))]:
 cam=s.camera;cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/f'renders/qa/R157_{label}_v002.png');bpy.ops.render.render(write_still=True)
out=R/'scenes/MUDAM_R157_ARAZI_YOLLAR_AGACLAR_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and (o.name.startswith(('R152_','R154_')) or o.get('level_id')=='L00_APPROACH'):o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/near_site.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
r=json.loads((R/'reports/R157_BUILD.json').read_text());r['scene']=out.name;r['preview_lighting']='Neutral sky fill and sun; previous excessive environment illumination replaced';(R/'reports/R157_BUILD.json').write_text(json.dumps(r,indent=2));print('R157_V002_SAVED',flush=True)
