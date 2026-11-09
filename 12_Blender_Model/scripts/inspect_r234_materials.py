from pathlib import Path
import bpy,json
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R232_ERASMUS_ENINE_CAM_KOT_ADAY_v001.blend'));rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith(('R187_','R193_','R172_','R194_')):rows.append(dict(name=o.name,materials=[m.name for m in o.data.materials],faces=len(o.data.polygons)))
print(json.dumps(rows));print('EARTH',[(m.name,[n.image.filepath for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]if m.use_nodes else [])for m in bpy.data.materials if any(k in m.name for k in ['EARTH','GRAVEL','FORT_STONE'])])
