from pathlib import Path
import sys,json,numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import rasterio,pyproj
from shapely.geometry import LineString,Point
from scipy.ndimage import gaussian_filter,map_coordinates
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text(encoding='utf-8'));w={r['id']:r for r in ways}
def xy(k):return [(x-293425,y-5499960) for x,y in w[k]['xy']]
line=LineString(xy('172705752')+xy('26435587')[1:]+xy('840229557')[1:]).offset_curve(1.82,join_style=2);d=json.loads((R/'config/r200_bridge_alignment.json').read_text());s0=line.project(Point(d['centerline'][0]));s1=line.project(Point(d['centerline'][-1]));grade=json.loads((R/'reports/R200_BRIDGE_GRADE.json').read_text())['grade']
with rasterio.open(R/'references/terrain_lidar2024/mudam_extended_mnt_2024.tif') as f:g=gaussian_filter(f.read(1),2);tr=f.transform;crs=f.crs
T=pyproj.Transformer.from_crs(32632,crs,always_xy=True);datum=json.loads((R/'.local_source_cache/r154/terrain.json').read_text())['datum'];out=[]
for s in np.arange(max(0,s0-100),min(line.length,s1+100)+1,10):
 p=line.interpolate(s);x,y=T.transform(p.x+293425,p.y+5499960);c,r=(~tr)*(x,y);z=float(map_coordinates(g,[[r-.5],[c-.5]],order=1)[0]-datum);out.append(dict(station=float(s-s0),xy=[p.x,p.y],ground=z,rail=grade[0]*(s-s0)+grade[1]))
(R/'config/r305_approach_profile.json').write_text(json.dumps(dict(s0=s0,s1=s1,fullLength=line.length,profile=out),indent=2));print([(round(v['station']),round(v['ground'],1),round(v['rail'],1)) for v in out])

ss=np.linspace(s0-100,s0,101);path=[list(line.interpolate(v).coords[0]) for v in ss]
(R/'config/r305_north_approach.json').write_text(json.dumps(dict(path=path,stations=list(np.linspace(-100,0,101)),grade=grade,sourceWays=['172705752'],limits=['North100m source-mapped railway only','Grade extrapolated from ACT fit and agrees with cached LiDAR centerline to0.2m','South approach and whole arch fidelity remain unresolved']),indent=2))
