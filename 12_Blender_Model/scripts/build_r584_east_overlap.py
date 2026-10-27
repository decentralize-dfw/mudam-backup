import bpy,json,ast,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R580_KALE_DUVAR_KAPALI_KABUK_ADAY_v001.blend'))
d=json.loads((R/'reports/R378_EAST_GROUND_PLANES.json').read_text())['east_long_moat'];poly=d['outline'];regions=[];records=[]
for t in tessellate_polygon([[Vector((*p,0))for p in poly]]):regions.append([poly[i]if isinstance(i,int)else(i.x,i.y)for i in t])
o=bpy.data.objects['R152_FORECOURT_2'];before=sum(p.area for p in o.data.polygons)
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(n for n in source.body if isinstance(n,ast.FunctionDef)and n.name=='clip');loop=next(n for n in source.body if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='ob');exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));code=ast.unparse(loop).replace("ob.name not in ['R152_CLASS2_TERRAIN']", "ob.name != 'R152_FORECOURT_2'");exec(compile(code,'<forecourt cut>','exec'))
o=bpy.data.objects['R152_FORECOURT_2'];after=sum(p.area for p in o.data.polygons);assert 0<before-after<200,(before,after)
# Source-confirmed long moat floor must be unobstructed at previously intersecting positions.
dg=bpy.context.evaluated_depsgraph_get();checks=[]
for x,y in [(50,20),(52,20),(52,10)]:
 hit,p,n,f,obj,m=bpy.context.scene.ray_cast(dg,Vector((x,y,3)),Vector((0,0,-1)),distance=15);assert hit and obj.name=='R378_EAST_LONG_MOAT_RUIN_FLOOR',(x,y,obj.name);checks.append(dict(x=x,y=y,object=obj.name,z=p.z))
out=R/'scenes/MUDAM_R584_DOGU_HENDEK_CIFT_ZEMIN_TEMIZ_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));assert len(bpy.data.objects['R152_FORECOURT_2'].data.polygons)>0
(R/'reports/R584_EAST_DOUBLE_SURFACE_FIX.json').write_text(json.dumps(dict(reopened=True,changed=records,removedOverlapArea=before-after,retainedArea=after,checks=checks,source='R378 independent classified-ground floor footprint; R541 source overhead confirms grass moat, no paving overlay.',accepted=False,published=False),indent=2));print('R584_SAVED',before-after,checks,flush=True)
