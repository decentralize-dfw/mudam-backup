from pathlib import Path
import sys,json,math
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon
from shapely import constrained_delaunay_triangles
d=json.loads((R/'reports/R515_SOUTH_MOAT_FLOOR_PLANE.json').read_text());raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());fit=next(q for q in json.loads((R/'reports/R445_CLASS1_BASTION_FITS.json').read_text()) if q['tower']=='SOUTH')['fit'];cx,cy=fit[:2];phi=math.atan2(-raw['direction'][1],-raw['direction'][0]);circle=[]
for i in range(192):
 a=math.tau*i/192;ux,uy=math.cos(a),math.sin(a);c0,sx,sy=d['coefficients'];rx,ry=d['center'];z=(c0+sx*(cx-rx+fit[2]*ux)+sy*(cy-ry+fit[2]*uy))/(1-fit[3]*(sx*ux+sy*uy));r=fit[2]+fit[3]*z-.04;circle.append((cx+r*ux,cy+r*uy))
wedge=Polygon([(cx,cy)]+[(cx+8*math.cos(phi-math.pi/2+i*math.pi/96),cy+8*math.sin(phi-math.pi/2+i*math.pi/96))for i in range(97)]);poly=Polygon(raw['footprint']).intersection(wedge).difference(Polygon(circle));parts=list(poly.geoms) if hasattr(poly,'geoms') else [poly];d['pieces']=[dict(outline=list(p.exterior.coords)[:-1],triangles=[list(t.exterior.coords)[:3] for t in constrained_delaunay_triangles(p).geoms])for p in parts if p.area>.001];d['area']=poly.area;d['basis']='Missing lower ground within original terrain cut, outside reconstructed battered bastion foot; 4cm hidden overlap into masonry. Plane is independent source-checked ground grade.';(R/'reports/R515_SOUTH_MOAT_FLOOR_DOMAIN.json').write_text(json.dumps(d,indent=2));print(d['area'],len(d['pieces']))

