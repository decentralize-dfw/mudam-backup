import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from shapely.geometry import Polygon,Point,LineString,box
from shapely import constrained_delaunay_triangles
old=json.loads((R/'reports/R321_WEST_CREST_MEASUREMENTS.json').read_text());trace=json.loads((R/'reports/R518_WEST_WALL_TRACE.json').read_text())['rows']
# Replace the wrongly straight central bend; retain the distant ends.
curve=np.array([q['xy']for q in trace[8:14]]);A=np.c_[2*curve,np.ones(len(curve))];fit=np.linalg.lstsq(A,(curve*curve).sum(1),rcond=None)[0];centre=fit[:2];radius=float(np.sqrt(fit[2]+(centre*centre).sum()));angles=np.unwrap(np.arctan2(curve[:,1]-centre[1],curve[:,0]-centre[0]));arc=[]
for angle in np.linspace(angles[0],angles[-1],49):
 t=(angle-angles[0])/(angles[-1]-angles[0]);xy=centre+radius*np.array([np.cos(angle),np.sin(angle)]);arc.append([*xy,float(trace[8]['z']*(1-t)+trace[13]['z']*t)])
wall=[q['measuredCrest']for q in old[:6]]+[[*q['xy'],q['z']]for q in trace[6:8]]+arc+[[*q['xy'],q['z']]for q in trace[14:16]]+[q['measuredCrest']for q in old[11:]]
terr=json.loads((R/'reports/R322_WEST_TERRACE.json').read_text());oldpoly=Polygon(terr['polygon']);newpoly=Polygon([p[:2]for p in wall]+terr['polygon'][16:]);assert newpoly.is_valid
floorpix=[(0,250),(340,260),(510,330),(520,370),(270,560),(250,540),(0,535)]
floor=Polygon([(-24+x*26/800,8-y*26/800)for x,y in floorpix]).union(oldpoly.difference(newpoly)).union(LineString([q[:2]for q in wall]).buffer(1.8,quad_segs=2).difference(newpoly).intersection(box(-24,-18,0,3)))
floor=floor.simplify(.025,preserve_topology=True)
rows=json.loads((R/'reports/R511_GROUND_CONTACT_AUDIT.json').read_text())['rows'];pts=np.array([[q['x'],q['y'],q['ground']]for q in rows if floor.buffer(.5).contains(Point(q['x'],q['y'])) and -8.1<q['ground']<-7.4 and q.get('source') is not None and abs(q['source']-q['ground'])<.25]);assert len(pts)>20,len(pts)
A=np.c_[pts[:,:2],np.ones(len(pts))];mask=np.arange(len(pts))%4!=0;coef=np.linalg.lstsq(A[mask],pts[mask,2],rcond=None)[0];err=A[~mask]@coef-pts[~mask,2]
def pieces(poly):
 return [dict(outline=list(p.exterior.coords)[:-1],triangles=[list(t.exterior.coords)[:3]for t in constrained_delaunay_triangles(p).geoms])for p in (poly.geoms if hasattr(poly,'geoms')else[poly])if p.area>.001]
d=dict(wall=wall,terraceOutline=list(newpoly.exterior.coords)[:-1],oldTerraceOutline=list(oldpoly.exterior.coords)[:-1],removed=pieces(oldpoly.difference(newpoly)),added=pieces(newpoly.difference(oldpoly)),floor=pieces(floor),floorPlane=coef.tolist(),heldout=dict(count=int(sum(~mask)),rms=float(np.sqrt(np.mean(err**2))),max=float(max(abs(err)))),accepted=False)
(R/'reports/R522_WEST_REBUILD_DOMAINS.json').write_text(json.dumps(d,indent=2));print(d['heldout'],oldpoly.area,newpoly.area,floor.area)
