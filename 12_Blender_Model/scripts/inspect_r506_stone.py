import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R505_KULE_CATISI_FOTOGRAF_MALZEME_ADAY_v001.blend'));out={}
for name in ['R154_FORT_STONE_PBR','R406_FORT_DRESSED_SANDSTONE','R129_HISTORIC_MASONRY_APPEARANCE_CANDIDATE']:
 m=bpy.data.materials[name];ns=[]
 for n in m.node_tree.nodes:
  row=dict(name=n.name,type=n.type)
  if n.type=='TEX_IMAGE':row.update(image=n.image.filepath if n.image else None,colorSpace=n.image.colorspace_settings.name if n.image else None)
  if n.type=='UVMAP':row['uv']=n.uv_map
  if n.type=='BSDF_PRINCIPLED':row['values']={k:list(n.inputs[k].default_value) if k=='Base Color' else n.inputs[k].default_value for k in ['Base Color','Metallic','Roughness']}
  ns.append(row)
 out[name]=dict(nodes=ns,links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
(R/'reports/R506_STONE_NODES.json').write_text(json.dumps(out,indent=2));print(out)
