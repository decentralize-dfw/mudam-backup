"""Extract lower stair radii and opening from PDF2016, not diagram line count."""
from pathlib import Path
import sys,json,math,numpy as np,hashlib
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(R/'10_Olcekli_Plan_ve_Fotograf_Analizi/.deps'));import pymupdf
C=json.loads((B/'config/foundation.json').read_text())['calibration'];k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];source=R/'08_Belgeler/Mudam_Wim_Delvoye_2016_kat_semalari.pdf';doc=pymupdf.open(source);draw=doc[4].get_drawings()
def point(v):return np.array([(v.x-ox)/k,(v.y-oy)/k])
def sample(item):
 if item[0]=='l':return [point(item[1]),point(item[2])]
 a,b,c,d=map(point,item[1:]);return [(1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for t in np.linspace(0,1,41)]
groups=[sum([sample(draw[i]['items'][j]) for i in range(219,230)],[]) for j in [0,2]];rows=[];values=[]
for ix,points in enumerate(groups):
 for x,y in points:rows.append([2*x,2*y,1 if ix==0 else 0,1 if ix==1 else 0]);values.append(x*x+y*y)
v=np.linalg.lstsq(rows,values,rcond=None)[0];center=v[:2];radii=[math.sqrt(v[j+2]+sum(center*center)) for j in range(2)];residuals=[max(abs(np.linalg.norm(p-center)-radii[j]) for p in points) for j,points in enumerate(groups)]
opening=[]
for item in draw[217]['items']:
 for p in sample(item):
  if not opening or np.linalg.norm(p-opening[-1])>1e-8:opening.append(p)
if np.linalg.norm(opening[0]-opening[-1])<1e-8:opening.pop()
cfg=dict(id='GH_DOWN_0_TO_MINUS1',base_scene='MUDAM_R04_UST_MERDIVEN_v003.blend',source_ids=['049','050','051','052','054','115','101','102','104','PDF2016'],source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),center_canonical=center.tolist(),outer_radius_canonical=radii[0],inner_radius_canonical=radii[1],fit_max_residual_canonical=residuals,fit_source_paths=list(range(219,230)),opening_source_path=217,opening_chord_canonical=[point(v).tolist() for v in draw[217]['items'][1][1:]],opening_canonical=[p.tolist() for p in opening],bottom_angle_deg=-135,nominal_top_angle_deg=45,top_edge_mode='intersection_with_source_opening_chord',risers_candidate=34,visible_treads=33,tread_display_thickness_m=.28,railing_height_m=1.05,glass_thickness_m=.016,rail_diameter_m=.042,glass_panels_per_side_candidate=12,glass_joint_gap_m=.004,base_channel_width_m=.034,base_channel_height_m=.026,stone_edge_band_width_m=.055,stone_edge_band_depth_m=.18,nosing_band_width_m=.018,assumptions=['The diagram arc geometry is traced/fitted, but its sparse tread count is not a real riser count.','34 risers is a replaceable candidate close to the current upper-stair average rise; exact count and basement level are unresolved.','Bottom at -135 degrees follows the existing direction candidate; the upper endpoints meet the source opening chord. Metric photo registration is not solved.','052 establishes a stepped underside. Constant 0.28 m displayed tread thickness is not a structural section.','Glass thickness, guard height, pane divisions, channels and nosing material are unmeasured candidates.','104 omits the staircase symbol; it supports the lower foyer region, not a separate measured stair trace.','Sub-pixel curve-fit residual is only numerical agreement with a visitor diagram, never building survey accuracy.'])
# The inner path is interpreted together with 114/055, not as another stair tread.
peninsula=[]
for item in draw[218]['items']:
 for p in sample(item):
  if not peninsula or np.linalg.norm(p-peninsula[-1])>1e-8:peninsula.append(p)
# Ordered open boundary: base-left, three Beziers, base-right.
edge=[point(draw[218]['items'][5][1])]+sum([sample(it) for it in draw[218]['items'][:3]],[])+[point(draw[218]['items'][3][2])]
edge=[p for j,p in enumerate(edge) if j==0 or np.linalg.norm(p-edge[j-1])>1e-7]
cfg['peninsula_edge_canonical']=[p.tolist() for p in edge]
cfg['corner_void_canonical']=[[587,334],[688,334],[688,435]]
cfg['source_ids']=list(dict.fromkeys(cfg['source_ids']+['045','046','047','048','053','055','114']))
cfg['assumptions']+=['114 and 055 establish a ground-floor peninsula with curved glass and straight wings. Path 218 supplies its working curve; 102 supplies the triangular corner void. Their exact registration is conditional.', 'Path 217 is the stair envelope, not the full ground-floor void. The old v003 full semicircular hole interpretation is rejected.', 'The stair top connection follows path 217 chord while the ground peninsula joins path 218; local transition between the two is inferred.']
(B/'config/lower_stair.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('LOWER_STAIR_SOURCE_FIT',center.tolist(),radii,residuals)
