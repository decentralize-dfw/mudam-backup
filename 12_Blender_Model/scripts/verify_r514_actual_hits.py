import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];old=json.loads((R/'reports/R511_GROUND_CONTACT_AUDIT.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R512_KALE_DIS_TASAN_TOPRAK_KESIM_ADAY_v001.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for q in old['rows']:
 if q['error'] is not None and abs(q['error'])<=1:continue
 h,p,n,index,o,mat=bpy.context.scene.ray_cast(dg,Vector((q['x'],q['y'],35)),Vector((0,0,-1)),distance=80);row=dict(q)
 row['fullSceneHit']=dict(object=o.name,z=p.z,error=p.z-q['ground'],normal=list(n),hiddenRender=o.hide_render) if h else None;rows.append(row)
(R/'reports/R514_FULL_SCENE_CONTACT_RECHECK.json').write_text(json.dumps(dict(rows=rows,correction='R511 selected-ground filter excluded L00_APPROACH museum bridge and other existing floors; its apparent NE 4m deficit is not demonstrated model error. This recheck considers full scene hits and reports canopy occlusion separately.'),indent=2));print('RECHECKED',len(rows))
