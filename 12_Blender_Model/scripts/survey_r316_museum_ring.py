from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];src=R/'.local_source_cache/act_context/local_glb';target=Vector((-10,-15,0))
def render(label):
 s=bpy.context.scene;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=target+Vector((0,0,220));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=220;s.render.engine='CYCLES';s.cycles.samples=4;s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/f'renders/qa/R316_museum_ring_{label}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);tiles=[]
for row in json.loads((src/'manifest.json').read_text())['tiles']:
 pts=row['bounds_local'];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if hi[0]<-120 or lo[0]>100 or hi[1]<-125 or lo[1]>95:continue
 bpy.ops.import_scene.gltf(filepath=str(src/row['file']));tiles.append(row['file'])
render('source');out=R/'.local_source_cache/r316';out.mkdir(exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(out/'museum_ring_reference.blend'),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R314_ECCL_GUNEY_KOSE_OTURUM_ADAY_v001.blend'));records=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if hi[0]<-120 or lo[0]>100 or hi[1]<-125 or lo[1]>95:continue
 if any(k in o.name.upper() for k in ['WALL','MOAT','FORT','BRIDGE','RUIN','BASTION','APPROACH']):records.append(dict(name=o.name,bounds=[lo,hi],source=str(o.get('source','')),status=str(o.get('status',''))))
render('candidate');(R/'reports/R316_MUSEUM_RING_INVENTORY.json').write_text(json.dumps(dict(accepted=False,referenceOnlyTiles=tiles,objects=records,scope='Only immediate museum fortifications and grade connections; remote environment production suspended'),indent=2));print('R316_READY',len(records))
