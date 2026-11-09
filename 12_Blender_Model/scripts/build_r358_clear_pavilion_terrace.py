import bpy,bmesh,json,math,ast
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R355_PAVYON_SUR_DONUSU_ADAY_v001.blend'))
data={k:v for k,v in json.loads((R/'reports/R347_PAVILION_PLANES.json').read_text()).items() if v.get('valid')};regions=[];records=[]
for row in data.values():
 poly=row['outline']
 for face in tessellate_polygon([[Vector((x,y,0)) for x,y in poly]]):regions.append([poly[i] if isinstance(i,int) else (i.x,i.y) for i in face])
# Reuse the already verified attribute-preserving polygon clipper, executing
# only its function and terrain loop, never the other candidate's workflow.
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text())
clip=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='clip')
loop=next(n for n in source.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='ob')
code=ast.unparse(loop).replace("ob.name not in ['R152_CLASS2_TERRAIN']","not (ob.name == 'R322_WEST_MUSEUM_TERRACE')")
exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));exec(compile(code,'<terrain and path cut>','exec'))

out=R/'scenes/MUDAM_R358_PAVYON_TERAS_TEMIZLIK_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'reports/R358_TERRACE_CLEARANCE.json').write_text(json.dumps(dict(scene=out.name,clipped=records,accepted=False,published=False),indent=2))
print(records)
