import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R420_KULE_AVLU_ESKI_ORTU_TEMIZLIGI_ADAY_v001.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();old=bpy.data.objects['R154_FORT_ROUNDED_EARTH_ROOF'];targets=[o for o in s.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('R417_','R402_','R420_','R419_SOUTH_TOWER_BODY','R407_CENTRAL_TOWER_BODY','R154_TOWER_WEST','R408_WEST','R389_FORT','R401_FORT'))];old.data.calc_loop_triangles();covered=[];uncovered=[]
for i,tr in enumerate(old.data.loop_triangles):
 p=old.matrix_world@(sum((old.data.vertices[j].co for j in tr.vertices),Vector())/3);hits=[]
 for o in targets:
  inv=o.matrix_world.inverted();hit,loc,no,fi=o.evaluated_get(dg).ray_cast(inv@Vector((p.x,p.y,15)),inv.to_3x3()@Vector((0,0,-1)))
  if hit:hits.append(dict(name=o.name,z=(o.matrix_world@loc).z))
 row=dict(triangle=i,center=list(p),area=tr.area,hits=hits)
 (covered if hits else uncovered).append(row)
report=dict(coveredCount=len(covered),uncoveredCount=len(uncovered),coveredArea=sum(x['area'] for x in covered),uncoveredArea=sum(x['area'] for x in uncovered),uncovered=uncovered,covered=covered)
(R/'reports/R422_LEGACY_COVERAGE.json').write_text(json.dumps(report));print({k:v for k,v in report.items() if k not in ['covered','uncovered']})
