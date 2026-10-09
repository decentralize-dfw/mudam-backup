"""Read-only whole-building wall inventory and three-floor comparison sections."""
from pathlib import Path
import bpy,bmesh,json,sys,re
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
release=verified_current_scene()
if '--' in sys.argv:release={'file':sys.argv[sys.argv.index('--')+1]}
bpy.ops.wm.open_mainfile(filepath=str(R/release['file']))
C=json.loads((B/'config/foundation.json').read_text())['calibration'];M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
def canonical(p):
 a=p.x+293425-M[0][2];b=p.y+5499960-M[1][2];u=(M[1][1]*a-M[0][1]*b)/det;v=(-M[1][0]*a+M[0][0]*b)/det
 return [(u-off[0])/k,(v-off[1])/k]
levels={'LM1':-5.326293513972+1.2,'PAV_LM1':-3.83+1.2,'L00':1.2,'LP1':4.859074784676+1.2,'HIGH':12.5}
rows=[];sections=[];deps=bpy.context.evaluated_depsgraph_get();excluded=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 kind=ob.get('element_type','');text=ob.name+' '+kind
 candidate=bool(re.search('WALL|FACADE|FRONT_|ATRIUM_BASE|UPSTAND|LINER|P05_WEST_END|STONE_BASE|STONE_SIDE_ENVELOPE|RECESS_(JAMB|HEAD|TOP)|CORE_(BODY|CAP)|STONE_CORE|NORTH_BASE|NORTH_STONE_GABLE|P07_GH_EAST_PORTAL|R30_(LEFT_JAMB|RIGHT_JAMB|STONE_HEAD)|R31_PASSAGE_SIDE|R19_(BOOTH_FRONT|FRONT_)|R52_BAY_2_INTERIOR_HEAD',text,re.I))
 if not candidate:continue
 if ob.get('level_id')=='SITE' or re.search('HISTORIC|MOAT|R35_WALL|R68_WALL|R54_WINDOW',text,re.I):excluded.append(ob.name);continue
 if ob.name=='P06_HIGH_EAVE_UPSTAND_4' or ob.name.startswith('R26_WALL_HEAD'):continue
 if re.search('RAIL|BRACKET|UPLIGHT|LAMP_RECESS|CEILING|LIGHT_|GLASS|GLAZ|ROD|PROFILE|WINDOW_FRAME|P12_FRONT_HEADER|R63_SIGN',text,re.I):continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();me.calc_loop_triangles();vs=[eo.matrix_world@v.co for v in me.vertices]
 bm=bmesh.new();bm.from_mesh(me);volume=bm.calc_volume(signed=True);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
 lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
 rows.append(dict(name=ob.name,kind=kind,zone=ob.get('zone_id',''),level=ob.get('level_id',''),sources=ob.get('source_ids',''),status=ob.get('status',''),assumption=ob.get('assumption_note',''),bounds=[lo,hi],volume=volume,nonmanifold=nonmanifold,canonical_vertices=[[*canonical(v),v.z] for v in vs]))
 for level,z in levels.items():
  if not lo[2]<z<hi[2]:continue
  seg=[]
  for tri in me.loop_triangles:
   points=[vs[i] for i in tri.vertices];hits=[]
   for a,b in zip(points,points[1:]+points[:1]):
    if a.z<z<=b.z or b.z<z<=a.z:hits.append(a.lerp(b,(z-a.z)/(b.z-a.z)))
   if len(hits)==2 and (hits[0]-hits[1]).length>1e-6:seg.append([canonical(p) for p in hits])
  if seg:sections.append(dict(name=ob.name,level=level,segments=seg))
 eo.to_mesh_clear()
(B/'reports/DUVAR_ENVANTERI.json').write_text(json.dumps(dict(scene=release['file'],levels=levels,objects=rows,sections=sections,excluded_site_walls=excluded,scope='Heuristic inventory candidates require architectural classification; not a completion receipt.'),ensure_ascii=False,indent=2),encoding='utf8')
print('WALL_CANDIDATES',len(rows))
for row in rows:print(row['name'],'|',row['kind'],'|',row['zone'],'|',round(row['bounds'][0][2],2),round(row['bounds'][1][2],2))
