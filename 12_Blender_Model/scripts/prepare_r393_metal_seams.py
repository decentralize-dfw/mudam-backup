from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,LineString
d=json.loads((R/'reports/R387_ROOF_INPUT.json').read_text());roof=Polygon(d['roofOutline']);upper=Polygon(d['raisedOutline']);rows=[];axis=(1/math.sqrt(2),-1/math.sqrt(2));normal=(1/math.sqrt(2),1/math.sqrt(2))
for label,domain,plane in [('lower',roof.difference(upper),d['lowerPlane']),('upper',upper,d['upperPlane'])]:
 for k in range(-180,0):
  u=k*.55;cx,cy=u*normal[0],u*normal[1];line=LineString([(cx-axis[0]*120,cy-axis[1]*120),(cx+axis[0]*120,cy+axis[1]*120)]);cut=domain.intersection(line)
  for seg in ([cut] if cut.geom_type=='LineString' else getattr(cut,'geoms',[])):
   if seg.geom_type=='LineString' and seg.length>.08:rows.append(dict(label=label,a=list(seg.coords[0]),b=list(seg.coords[-1]),plane=plane))
(R/'reports/R393_METAL_SEAMS_INPUT.json').write_text(json.dumps(dict(seams=rows,source='Visible transverse standing seams in R336; estimated spacing 0.55m, authored strip geometry. No scan faces/photo textures.',spacingSurveyed=False),indent=2));print(len(rows))
