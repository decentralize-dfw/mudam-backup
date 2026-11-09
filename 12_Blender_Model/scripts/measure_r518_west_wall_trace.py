import bpy,json,statistics
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'))
dg=bpy.context.evaluated_depsgraph_get()
# Cap centre trace in the 1400px orthographic source render; not extracted mesh.
pixels=[(215,306),(270,315),(341,320),(410,319),(467,337),(545,309),(650,309),(740,310),(785,312),(832,325),(874,345),(907,386),(932,429),(943,471),(939,540),(933,620),(927,720),(921,821),(915,910),(912,950),(908,1007),(935,1041),(1011,1110),(1115,1217),(1142,1241),(1169,1244),(1214,1214),(1280,1159),(1330,1115),(1380,1070)]
rows=[]
for px,py in pixels:
 x=-56+px*76/1400;y=18-py*76/1400;hits=[]
 for dx,dy in [(0,0),(.08,0),(-.08,0),(0,.08),(0,-.08)]:
  h,p,n,idx,o,m=bpy.context.scene.ray_cast(dg,Vector((x+dx,y+dy,50)),Vector((0,0,-1)),distance=90)
  if h:hits.append(p.z)
 rows.append(dict(pixel=[px,py],xy=[x,y],z=statistics.median(hits),range=max(hits)-min(hits),samples=hits))
(R/'reports/R518_WEST_WALL_TRACE.json').write_text(json.dumps(dict(source='R517_whole_west_wall_source.png',pixelScale=76/1400,rows=rows,accepted=False),indent=2));print([(r['pixel'],round(r['z'],3),round(r['range'],3))for r in rows])
