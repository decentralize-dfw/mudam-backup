"""Interior-envelope diagnostic: actual floor support and upper cover, not mesh watertightness."""
from pathlib import Path
import bpy,json,sys,math,re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(B/'scripts'));from release_utils import verified_current_scene
r=verified_current_scene();r={'file':sys.argv[sys.argv.index('--')+1]} if '--' in sys.argv else r;bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));F=json.loads((B/'config/foundation.json').read_text());C=F['calibration'];P=json.loads((B/'config/ground_gallery_access.json').read_text());U=json.loads((B/'config/upper_gallery_room.json').read_text());L=json.loads((B/'config/lower_gallery_rooms.json').read_text());Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};up=Vector((0,0,1))
def point(p,z=0):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def inside(p,poly):
 x,y=p;v=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:v=not v
 return v
regions=[]
for n in ['GH','ENT','EAST_GARDEN','WEST_CAFE','LINK','PAV']:regions.append(dict(id=n,level='L00',z=0,poly=F['polygons'][n]))
for n,p in P['source_gallery_polygons'].items():regions.append(dict(id='GROUND_GALLERY_'+n,level='L00',z=0,poly=p))
for n,p in U['source_polygons_canonical'].items():regions.append(dict(id='UPPER_GALLERY_'+n,level='LP1',z=Z['Z_LP1_FINISH'],poly=p))
for n,p in L['rooms'].items():
 s,dx,dy=C['basement_registration']['source_to_canonical'];regions.append(dict(id='LOWER_GALLERY_'+n,level='LM1',z=Z['Z_LM1_FINISH'],poly=[[x*s+dx,y*s+dy] for x,y in p]))
s,dx,dy=C['basement_registration']['source_to_canonical'];regions.append(dict(id='LOWER_FOYER',level='LM1',z=Z['Z_LM1_FINISH'],poly=[[x*s+dx,y*s+dy] for x,y in L['foyer_polygon']]))
regions.append(dict(id='READING',level='LP1',z=Z['Z_LP1_FINISH'],poly=json.loads((B/'config/reading_room.json').read_text())['room_inner_polygon']))
regions.append(dict(id='STUDIO',level='LP1',z=Z['Z_LP1_FINISH'],poly=json.loads((B/'config/upper_studio.json').read_text())['inner_polygon']))
regions.append(dict(id='UPPER_BRIDGE',level='LP1',z=Z['Z_LP1_FINISH'],poly=[[465,555],[689,555],[689,598],[465,598]]))
regions.append(dict(id='LIFT_LANDING',level='LP1',z=Z['Z_LP1_FINISH'],poly=json.loads((B/'config/upper_lift_landing.json').read_text())['landing_polygon']))
regions.append(dict(id='PAV_LOWER',level='PAV_LM1',z=-3.83,poly=F['polygons']['PAV']))
A=json.loads((B/'config/auditorium_room.json').read_text());s,dx,dy=C['basement_registration']['source_to_canonical'];regions.append(dict(id='AUDITORIUM',level='LM1',z=Z['Z_LM1_FINISH']+A['row_count']*A['row_rise_m'],poly=[[x*s+dx,y*s+dy] for x,y in [(A['room_x'][0],A['front_y']),(A['room_x'][1],A['front_y']),(A['room_x'][1],A['rear_y']),(A['room_x'][0],A['rear_y'])]],variable_floor=True))
verts=[];faces=[];owners=[];names=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or ob.get('level_id')=='SITE':continue
 text=ob.name+' '+ob.get('element_type','')
 if re.search('TREE|MOAT|HISTORIC|LAMP|LENS|SPOT|UPLIGHT|FIXTURE|RAIL|HANDRAIL|SEAT|CHAIR|SIGN|CONTROL|BUTTON',text,re.I):continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();start=len(verts);verts.extend(eo.matrix_world@v.co for v in me.vertices);index=len(names);names.append(ob.name)
 for f in me.polygons:faces.append(tuple(start+i for i in f.vertices));owners.append(index)
 eo.to_mesh_clear()
tree=BVHTree.FromPolygons(verts,faces);rows=[];summaries=[]
for reg in regions:
 poly=reg['poly'];lo=[min(p[i] for p in poly) for i in [0,1]];hi=[max(p[i] for p in poly) for i in [0,1]];n=0;fd=0;ru=0;deep=0;sideopen=0
 for x in range(math.ceil(lo[0])+4,math.floor(hi[0]),8):
  for y in range(math.ceil(lo[1])+4,math.floor(hi[1]),8):
   if not inside([x,y],poly):continue
   n+=1;floor=tree.ray_cast(point([x,y],reg['z']+.05),-up,12);roof=tree.ray_cast(point([x,y],reg['z']+1.2),up,45)
   row=dict(region=reg['id'],level=reg['level'],canonical=[x,y],floor_z=reg['z'],floor_hit=None if floor[0] is None else dict(name=names[owners[floor[2]]],z=floor[0].z,distance=floor[3]),cover_hit=None if roof[0] is None else dict(name=names[owners[roof[2]]],z=roof[0].z,distance=roof[3]))
   escaped=[]
   for angle in range(0,360,45):
    direction=Vector((math.cos(math.radians(angle)),math.sin(math.radians(angle)),0));hit=tree.ray_cast(point([x,y],reg['z']+1.2),direction,200)
    if hit[0] is None:escaped.append(angle)
   row['unclosed_side_directions']=escaped;sideopen+=bool(escaped)
   row['floor_missing']=floor[0] is None;row['cover_missing']=roof[0] is None;row['floor_below_expected']=floor[0] is not None and floor[3]>.25;fd+=row['floor_missing'];ru+=row['cover_missing'];deep+=row['floor_below_expected'];rows.append(row)
 summaries.append(dict(region=reg['id'],samples=n,floor_missing=fd,cover_missing=ru,floor_below_expected=deep,side_escape_samples=sideopen))
q=dict(file=r['file'],summaries=summaries,samples=rows,regions=regions,limits=['Diagnostic grid only; openings for stairs and multilevel voids need source classification.','An upper hit can be a floor, roof or frame. Continuous edge/side closure needs separate inspection.','Reference bounds and heights remain conditional. Do not fill every flagged sample indiscriminately.'],construction_acceptance=False);(B/'reports/KABUK_TARAMASI.json').write_text(json.dumps(q,indent=2),encoding='utf8');print(json.dumps(summaries,indent=2))
