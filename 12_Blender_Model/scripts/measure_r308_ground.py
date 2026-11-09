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
a=np.array([178.3125,26.625]);b=np.array([332.4375,282.375]);u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]])
for station in np.linspace(5,np.linalg.norm(b-a)-5,12):
 xy=a+u*station+n*5;x,y=T.transform(xy[0]+293425,xy[1]+5499960);c,r=(~tr)*(x,y);z=float(map_coordinates(g,[[r-.5],[c-.5]],order=1)[0]-datum);out.append(dict(station=float(station),xy=xy.tolist(),ground=z))
(R/'config/r308_podium_ground.json').write_text(json.dumps(out,indent=2));print(out)
