from pathlib import Path
import sys,json,math
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,box
from shapely.ops import triangulate,unary_union
D=json.loads((R/'reports/R482_COURT_PATH_DOMAINS.json').read_text())
# Extend the independently authored ground to the retaining wall's western foot.
outline=D['lawn']['outline'];outline[6:8]=[[-42.75,31.05],[-53.635,20.165],[-57.415,20.165]]
def mesh(poly):
 vertices=[];faces=[];lookup={}
 def index(p):
  key=tuple(round(c,8) for c in p)
  if key not in lookup:lookup[key]=len(vertices);vertices.append(key)
  return lookup[key]
 lo=poly.bounds
 for ix in range(math.floor(lo[0]*2),math.ceil(lo[2]*2)):
  for iy in range(math.floor(lo[1]*2),math.ceil(lo[3]*2)):
   cell=poly.intersection(box(ix/2,iy/2,(ix+1)/2,(iy+1)/2))
   if cell.is_empty or cell.area<1e-10:continue
   for tr in triangulate(cell):
    if not cell.covers(tr.representative_point()):continue
    faces.append([index(p) for p in list(tr.exterior.coords)[:3]])
 return dict(outline=list(poly.exterior.coords)[:-1],vertices=vertices,faces=faces)
D['lawn']=mesh(Polygon(outline));D['cutout']=list(unary_union([Polygon(D[k]['outline']) for k in ['lawn','path','connector']]).exterior.coords)[:-1]
(R/'reports/R485_COURT_PATH_DOMAINS.json').write_text(json.dumps(D))
s=(R/'scripts/build_r482_court_path_v002.py').read_text().replace('R482_COURT_PATH_DOMAINS.json','R485_COURT_PATH_DOMAINS.json').replace('R482_NW_','R485_NW_').replace('MUDAM_R482_AVLU_YOL_SEV_BIRLESIM_ADAY_v002.blend','MUDAM_R485_AVLU_SUR_ZEMIN_ADAY_v001.blend').replace('R482_COURT_PATH_BUILD.json','R485_COURT_PATH_BUILD.json')
# The southeast field is low ground, not an extrapolation of the skylight bank.
s=s.replace('return max(floor,westz,northz,min(east,court(max(-58.22,min(-44.43,x)))))','east_weight=max(0,min(1,(y-29)/3)); eastz=floor+(min(east,court(max(-58.22,min(-44.43,x))))-floor)*east_weight\n return max(floor,westz,northz,eastz)')
(R/'scripts/build_r485_court.py').write_text(s)
