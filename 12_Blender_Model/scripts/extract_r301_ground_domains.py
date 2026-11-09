from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R300_ALT_MAHALLE_13_KUTLE_TAMAMLAMA_ADAY_v001.blend'))
targets=['R182_DISTRICT_164184549','R182_DISTRICT_930614764','R171_546345955'];domains=[]
for name in targets:
 o=bpy.data.objects[name];p=[o.matrix_world@v.co for v in o.data.vertices];base=min(v.z for v in p);ring=[list(v) for v in p if abs(v.z-base)<.001];domains.append(dict(name=name,base=base,ring=ring,bounds=[min(v.x for v in p)-1,max(v.x for v in p)+1,min(v.y for v in p)-1,max(v.y for v in p)+1]))
triangles=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS','R300_DISTRICT_EDGE_GROUND'] or o.name.startswith(('R182_EXTENSION_','R210_GROUND_CONTINUITY_','R202_ALZETTE_'))):continue
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
  if not any(max(v.x for v in p)>=b['bounds'][0] and min(v.x for v in p)<=b['bounds'][1] and max(v.y for v in p)>=b['bounds'][2] and min(v.y for v in p)<=b['bounds'][3] for b in domains):continue
  triangles.append(dict(object=o.name,points=[list(v) for v in p]))
(R/'config/r301_ground_domains.json').write_text(json.dumps(dict(domains=domains,triangles=triangles)));print('Reference ground triangles',len(triangles),flush=True)
