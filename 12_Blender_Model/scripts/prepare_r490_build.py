from pathlib import Path
import json,sys
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,box
from shapely.ops import triangulate,unary_union
D=json.loads((R/'reports/R487_PASSAGE_PLANE.json').read_text());p=unary_union([Polygon(D['outline']),Polygon([(-37.6,30.9),(-30.6,38),(-27.8,38),(-33.5,30.9)])]);D['outline']=list(p.exterior.coords)[:-1];vs=[];fs=[];ids={}
for lo,hi in zip([0]+D['knots'],D['knots']+[60]):
 part=p.intersection(box(-80,lo,0,hi))
 for tr in triangulate(part):
  if not part.covers(tr.representative_point()):continue
  f=[]
  for xy in list(tr.exterior.coords)[:3]:
   key=tuple(round(c,8) for c in xy)
   if key not in ids:ids[key]=len(vs);vs.append(key)
   f.append(ids[key])
  fs.append(f)
D.update(vertices=vs,faces=fs,northEvidence='Visible source floor at y31/35/36/37 remains approximately -4.7m. Source roof occludes y33/34; continuation underneath inferred from visible ends, not directly measured. Northern termination y38 needs final junction validation.');(R/'reports/R490_PASSAGE_DOMAIN.json').write_text(json.dumps(D,indent=2))
s=(R/'scripts/build_r487_passage.py').read_text().replace('MUDAM_R486_AVLU_DUSEY_BAGLANTI_ADAY_v002.blend','MUDAM_R489_AVLU_KOYU_YATAY_BANT_ADAY_v001.blend').replace('R487_PASSAGE_PLANE.json','R490_PASSAGE_DOMAIN.json').replace('R487_NW_MINERAL_PASSAGE','R490_NW_MINERAL_PASSAGE').replace('MUDAM_R487_KUZEYBATI_ALT_GECIT_ADAY_v001.blend','MUDAM_R490_TAM_KUZEYBATI_GECIT_ADAY_v001.blend').replace('R487_BUILD.json','R490_BUILD.json').replace('R487_northwest_oblique.png','R490_northwest_oblique.png')
s=s.replace('records=[]',"records=[]\nold=bpy.data.objects.get('R487_NW_MINERAL_PASSAGE')\nif old:bpy.data.objects.remove(old,do_unlink=True)",1)
s=s.replace("vs=[(x,y,height(x,y)+dz) for dz in [0,-.3] for x,y in D['vertices']]","vs=[(x,y,height(x,y) if upper else -8) for upper in [True,False] for x,y in D['vertices']]")
(R/'scripts/build_r490_passage.py').write_text(s)
