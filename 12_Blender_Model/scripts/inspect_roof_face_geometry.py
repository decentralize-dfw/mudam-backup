from pathlib import Path
import bpy,json
B=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_R82_BATI_MERDIVEN_GIRIS_KABUK_v001.blend'));out=[]
for o in bpy.context.scene.objects:
 if o.name.startswith(('P06_MAIN_ROOF_FACE','P06_WEST_GLAZED')) or o.name in ['P10_MAIN_ROOF_FACE_6_GLASS_00_02','P11_WEST_6_00_00']:
  out.append(dict(name=o.name,type=o.type,vertices=[list(o.matrix_world@v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons]))
(B/'reports/ROOF_FACE_GEOMETRY.json').write_text(json.dumps(out,indent=2));print(json.dumps(out[:2],indent=2));print(len(out),'objects')
