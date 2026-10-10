from pathlib import Path
import bpy,json,sys
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R127_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['after'];phase=args[0];file=r['file'] if phase=='after' else '12_Blender_Model/scenes/'+r['base_scene'];bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));S=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=16;S.render.resolution_x=1200;S.render.resolution_y=900;S.render.resolution_percentage=100;S.cycles.transparent_max_bounces=64
cd=bpy.data.cameras.new('R127_REVIEW');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);S.camera=cam
cuts=[]
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 nt=mat.node_tree
 for out in [n for n in nt.nodes if n.type=='OUTPUT_MATERIAL']:
  sock=out.inputs['Surface']
  if not sock.is_linked:continue
  original=sock.links[0].from_socket;g=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');gt=nt.nodes.new('ShaderNodeMath');gt.operation='GREATER_THAN';lt=nt.nodes.new('ShaderNodeMath');lt.operation='LESS_THAN';combine=nt.nodes.new('ShaderNodeMath');combine.operation='MAXIMUM';nt.links.new(g.outputs['Position'],xyz.inputs[0]);nt.links.new(xyz.outputs['Z'],gt.inputs[0]);nt.links.new(xyz.outputs['Z'],lt.inputs[0]);nt.links.new(gt.outputs[0],combine.inputs[0]);nt.links.new(lt.outputs[0],combine.inputs[1]);trans=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(combine.outputs[0],mix.inputs[0]);nt.links.new(original,mix.inputs[1]);nt.links.new(trans.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],sock);cuts.append((gt,lt))
def pt(p):
 x,y,z=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for name,eye,target,lens,zlo,zhi in [('lower_cover',(30,-6,24),(7,13,-.4),48,-1.1,-.15),('lower_side',(-27,38,18),(0,18,-.4),48,-1.1,-.15)]:
 if len(args)>1 and name!=args[1]:continue
 for gt,lt in cuts:gt.inputs[1].default_value=zhi;lt.inputs[1].default_value=zlo
 cam.location=Vector(eye);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=lens;S.render.filepath=str(B/'renders/qa'/f'R127_{phase}_{name}.png');bpy.ops.render.render(write_still=True)
