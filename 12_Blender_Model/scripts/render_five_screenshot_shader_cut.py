"""R95 review with the same three cameras as R92; no review-only hiding."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R95_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration']
def point(p):
 x,y,z=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['after'];phase=args[0];file=r['file'] if phase=='after' else '12_Blender_Model/scenes/'+r['base_scene'];bpy.ops.wm.open_mainfile(filepath=str(R/file));S=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=20;S.render.resolution_x=1400;S.render.resolution_y=1050;S.render.resolution_percentage=100
cd=bpy.data.cameras.new('R73_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam;images=[]
# Review-only section at z4.2m to expose the ground circulation, as in SS4.
# A review-only world-height shader cut avoids mutating or evaluating thousands of meshes.
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 nt=mat.node_tree
 for out in [n for n in nt.nodes if n.type=='OUTPUT_MATERIAL']:
  sock=out.inputs['Surface']
  if not sock.is_linked:continue
  original=sock.links[0].from_socket
  geometry=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');gt=nt.nodes.new('ShaderNodeMath');gt.operation='GREATER_THAN';gt.inputs[1].default_value=4.2
  transparent=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(geometry.outputs['Position'],xyz.inputs[0]);nt.links.new(xyz.outputs['Z'],gt.inputs[0]);nt.links.new(gt.outputs[0],mix.inputs[0]);nt.links.new(original,mix.inputs[1]);nt.links.new(transparent.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],sock)
S.cycles.transparent_max_bounces=64
for name,eye,target,lens in [('west_ground_cut',(610,220,24),(750,420,0),40),('east_ground_cut',(490,180,27),(395,420,0),40)]:
 cam.location=point(eye);t=point(target);cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R95_shader_{name}.png');bpy.ops.render.render(write_still=True);images.append(dict(image=Path(S.render.filepath).name,eye_canonical=eye,target_canonical=target,lens=lens,section_z=4.2))
(B/'reports'/'R95_shader_ground_cut_render.json').write_text(json.dumps(dict(file=file,images=images,all_active_surroundings=True,metric_camera_match=False),indent=2),encoding='utf8')
