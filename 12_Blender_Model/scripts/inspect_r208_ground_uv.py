from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R207_GERCEK_BITKI_CAKISMA_TEMIZLIGI_v001.blend'));out=[]
for name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS']:
 o=bpy.data.objects[name];out.append(dict(name=name,uv=[l.name for l in o.data.uv_layers],materials=[dict(name=m.name,nodes=[dict(type=n.type,uv=n.uv_map if n.type=='UVMAP' else None,image=n.image.name if n.type=='TEX_IMAGE' and n.image else None) for n in m.node_tree.nodes]) for m in o.data.materials],down=sum(p.normal.z<0 for p in o.data.polygons),faces=len(o.data.polygons)))
(R/'reports/R208_GROUND_UV_AUDIT.json').write_text(json.dumps(out,indent=2));print(out)
