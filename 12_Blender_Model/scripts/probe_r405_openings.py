import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R405_KALE_DOGU_DUVAR_ACIKLIKLARI_ADAY_v001.blend'));d=json.loads((R/'reports/R405_WALL_OPENINGS.json').read_text());raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());ob=bpy.data.objects['R154_FORT_MASONRY_BODY'];rows=[]
for row in d['openings']:
 i=row['wallSegment'];v=Vector(raw['footprint'][i+1])-Vector(raw['footprint'][i]);t=Vector((v.x,v.y,0)).normalized();n=Vector((t.y,-t.x,0));p=Vector(row['center'])
 if n.dot(Vector((0,-90,-.5))-p)<0:n=-n
 hit,pt,no,face=ob.ray_cast(p+n*.2,-n);depth=(pt-p).dot(-n) if hit else None;rows.append(dict(kind=row['kind'],pixel=row['pixel'],hit=hit,depth=depth))
(R/'reports/R405_OPENING_DEPTH_CHECK.json').write_text(json.dumps(rows,indent=2));print(rows)
