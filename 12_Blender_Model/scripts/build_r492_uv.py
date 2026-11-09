import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R491_DOGU_ALT_HENDEK_ADAY_v001.blend'));rows=json.loads((R/'reports/R492_SITE_UV_AUDIT.json').read_text());changes=[]
for row in rows:
 o=bpy.data.objects[row['name']];me=o.data
 if row['grass']:
  uv=me.uv_layers.get('UVMap');err=max((abs(uv.data[l.index].uv.x-((o.matrix_world@me.vertices[l.vertex_index].co).x+500)/1150)+abs(uv.data[l.index].uv.y-((o.matrix_world@me.vertices[l.vertex_index].co).y+450)/1100) for l in me.loops),default=0)
  if err>1e-6:
   for l in me.loops:
    v=o.matrix_world@me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x+500)/1150,(v.y+450)/1100)
   changes.append(dict(name=o.name,fix='georeferenced albedo UV restored',previousMaxUvError=err))
 for mat,name in row['missing']:
  if name!='MicroUV':raise RuntimeError(row)
  uv=me.uv_layers.get(name) or me.uv_layers.new(name=name)
  for l in me.loops:
   v=o.matrix_world@me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x/6,v.y/6)
  changes.append(dict(name=o.name,fix='missing metric micro normal UV restored'))
 # Keep default albedo coordinates as active render layer.
 if me.uv_layers.get('UVMap'):me.uv_layers.active=me.uv_layers['UVMap'];me.uv_layers['UVMap'].active_render=True
out=R/'scenes/MUDAM_R492_SUR_CEVRE_UV_DUZELTME_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));missing=[]
for row in rows:
 o=bpy.data.objects[row['name']]
 for mat in o.data.materials:
  if mat and mat.use_nodes:
   missing.extend((o.name,n.uv_map) for n in mat.node_tree.nodes if n.type=='UVMAP' and n.uv_map and n.uv_map not in o.data.uv_layers)
assert not missing,missing;(R/'reports/R492_UV_FIX.json').write_text(json.dumps(dict(changes=changes,reopenedMissingUv=missing,geometryChanged=False,accepted=False,published=False),indent=2));print(changes)
