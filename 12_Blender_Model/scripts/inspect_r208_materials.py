from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R206_NOVOTEL_BUTUN_CATILAR_v001.blend'));o=bpy.data.objects['R154_FAR_GROUND'];out=[]
for i in [82762,79793,83700]:
 p=o.data.polygons[i];m=o.data.materials[p.material_index];out.append(dict(face=i,normal=list(p.normal),material=m.name,vertices=[list(o.data.vertices[j].co) for j in p.vertices],uv=[list(o.data.uv_layers.active.data[j].uv) for j in p.loop_indices],nodes=[dict(type=n.type,image=n.image.name if n.type=='TEX_IMAGE' and n.image else None) for n in m.node_tree.nodes]))
print(out);(R/'reports/R208_SEAM_MATERIALS.json').write_text(json.dumps(out,indent=2))
