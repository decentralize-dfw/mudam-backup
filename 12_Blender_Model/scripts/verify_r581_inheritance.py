import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(R/path));out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  h=hashlib.sha256();h.update(struct.pack('<16f',*[v for row in o.matrix_world for v in row]));co=[0.0]*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',co);h.update(struct.pack('<%df'%len(co),*co));idx=[0]*len(o.data.loops);o.data.loops.foreach_get('vertex_index',idx);h.update(struct.pack('<%di'%len(idx),*idx));out[o.name]=dict(geometry=h.hexdigest(),hidden=o.hide_render)
 return out
old=snapshot('scenes/MUDAM_R580_KALE_DUVAR_KAPALI_KABUK_ADAY_v001.blend');new=snapshot('scenes/MUDAM_R581_BINA_TEMAS_AO_BAKE_ADAY_v001.blend');assert old==new;report=dict(unchanged=len(old),changed=0,added=0,removed=0);(R/'reports/R581_GEOMETRY_INHERITANCE.json').write_text(json.dumps(report,indent=2));print(report)
