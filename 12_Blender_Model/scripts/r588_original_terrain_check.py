import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];W=R/'reports'
CACHE=R/'.local_source_cache/r588_ground'
CACHE.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v009.blend'))
o=bpy.data.objects['R152_CLASS2_TERRAIN'];bm=bmesh.new();bm.from_mesh(o.data);b=[f for f in bm.faces if f.calc_area()<1e-10];print('INHERITED_ZERO',len(b));(W/'R588_ORIGINAL_TERRAIN_DEGENERACY.json').write_text(json.dumps(dict(count=len(b),faces=[[[*v.co]for v in f.verts]for f in b])));bm.free()
