import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];W=R/'reports'
CACHE=R/'.local_source_cache/r588_ground'
CACHE.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v009.blend'))
out={}
for name in ['R152_CLASS2_TERRAIN','R523_WEST_MOAT_LOWER_GROUND_0','R588_WEST_CLASS2_GROUND_RESTORATION']:
 o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles()
 out[name]=dict(vertices=[list(o.matrix_world@v.co)for v in m.vertices],triangles=[dict(vertices=list(t.vertices),loops=list(t.loops),polygon=t.polygon_index,normal=list(t.normal),smooth=m.polygons[t.polygon_index].use_smooth,material=m.polygons[t.polygon_index].material_index)for t in m.loop_triangles],normals=[list(v.vector)for v in m.corner_normals],uv={l.name:[list(x.uv)for x in l.data]for l in m.uv_layers})
(CACHE/'R588_GROUND_FULL_INPUT.json').write_text(json.dumps(out))
print('EXPORT',[ (n,len(d['vertices']),len(d['triangles']))for n,d in out.items()])
