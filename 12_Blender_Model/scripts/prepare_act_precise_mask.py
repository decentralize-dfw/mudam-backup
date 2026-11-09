"""Use the actual concave bridge boundary, never its convex hull."""
from pathlib import Path
import sys,json
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import Polygon
cache=root/'.local_source_cache/act_context'
rows=json.loads((cache/'architecture_hulls.json').read_text())
bridge=json.loads((root/'reports/R34_build_report.json').read_text())['union_boundary']
parts=[]
for row in rows:
    p=Polygon(bridge if row['name']=='R34_APPROACH_CONTINUOUS_DECK' else row['polygon'])
    if p.is_valid and p.area>.001:parts.append(p)
parts.append(Polygon(json.loads((cache/'mudam_exclusion.json').read_text())['polygon']))
mask=shapely.union_all(parts).buffer(.25,join_style='mitre')
(cache/'architecture_precise_exclusion.geojson').write_text(shapely.to_geojson(mask))
old=shapely.from_geojson((cache/'architecture_exclusion.geojson').read_text())
result=dict(old_area=old.area,new_area=mask.area,unnecessarily_cut_area_restored=old.difference(mask).area,basis='R34 actual concave union boundary replaces convex hull. Remaining architecture hulls and OSM museum footprint retained. 0.25m candidate clearance.')
(root/'reports/ACT2020_precise_mask.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
import pyproj
transform=pyproj.Transformer.from_crs(32632,4326,always_xy=True)
config_path=root/'config/act_context_candidate.json'
config=json.loads(config_path.read_text())
polygons=list(mask.geoms) if mask.geom_type=='MultiPolygon' else [mask]
assert all(not p.interiors for p in polygons),'Web ring schema needs hole support'
config['clipping_polygons_degrees']=[[[*transform.transform(x+293425,y+5499960)] for x,y in list(p.exterior.coords)[:-1]] for p in polygons]
config['mask_basis']=result['basis']
config['web_ground_preservation']='XY clipping only; local Blender LiDAR-ground restoration is not yet transferred to the streamed viewer'
config_path.write_text(json.dumps(config,indent=2),encoding='utf-8')
