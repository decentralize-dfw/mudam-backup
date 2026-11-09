from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
from shapely.geometry import Polygon
from PIL import Image,ImageDraw
d=json.loads((R/'reports/R385_ROOF_BOUNDARIES.json').read_text());v=np.array(d['outline']);poly=Polygon(v);sign=1 if poly.exterior.is_ccw else -1;rows=[]
for i,pt in enumerate(v):
 tangent=v[(i+1)%len(v)]-v[i-1];tangent/=np.linalg.norm(tangent);normal=sign*np.array([tangent[1],-tangent[0]])
 ids=tree.query_ball_point(pt,3.5);q=p[ids];q=q[np.isin(cl[ids],[1,2,6])];local=q[:,:2]-pt;t=local@normal;u=local@tangent;bands=[]
 for a in np.arange(-2.7,2.71,.2):
  zz=q[(abs(u)<.55)&(abs(t-a)<.15),2];zz=zz[(zz>1)&(zz<5)]
  bands.append([round(float(a),2),len(zz),round(float(np.median(zz)),3) if len(zz)>2 else None])
 rows.append(dict(i=i,point=pt.tolist(),normal=normal.tolist(),bands=bands))
im=Image.new('RGB',(1200,880),'white');dr=ImageDraw.Draw(im)
for r in rows:
 ox=(r['i']%4)*300;oy=(r['i']//4)*145;dr.text((ox+4,oy+3),str(r['i']),fill='black')
 for a,n,z in r['bands']:
  if z is not None:
   x=ox+150+a*40;y=oy+135-(z-1)*30;dr.ellipse((x-2,y-2,x+2,y+2),fill='blue')
 dr.line([(ox+150,oy+15),(ox+150,oy+140)],fill='gray')
im.save(R/'renders/qa/R386_roof_edge_profiles.png');(R/'reports/R386_ROOF_EDGES.json').write_text(json.dumps(dict(stations=rows),indent=2))
print([(r['i'],r['bands']) for r in rows])
