from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
from shapely.geometry import Polygon,Point
from PIL import Image,ImageDraw
# Architectural plan trace from orthographic R336, not a transferred scan surface.
pixels=[(242,744),(323,833),(432,710),(539,598),(643,508),(697,478),(747,464),(799,470),(841,491),(878,458),(893,263),(866,217),(656,208),(616,251),(640,296),(641,332),(625,377),(590,428),(543,483),(464,566),(367,666),(290,725)]
xy=[(-74.5+x*65/1100,-1.5-y*65/1100) for x,y in pixels]
poly=Polygon(xy);assert poly.is_valid
rows=[]
for i,(x,y) in enumerate(xy):
 ids=tree.query_ball_point((x,y),.45);q=p[ids];c=cl[ids];q=q[np.isin(c,[1,2,6])];z=q[:,2];z=z[(z>0)&(z<6)]
 rows.append(dict(i=i,xy=[x,y],zMedian=float(np.median(z)) if len(z) else None,n=len(z),z10=float(np.quantile(z,.1)) if len(z) else None,z90=float(np.quantile(z,.9)) if len(z) else None))
im=Image.open(R/'renders/qa/R336_fort_roof_source.png').convert('RGB');dr=ImageDraw.Draw(im);dr.line(pixels+[pixels[0]],fill=(255,30,20),width=3)
for row,px in zip(rows,pixels):dr.text(px,str(row['i'])+':'+str(round(row['zMedian'],2) if row['n'] else '?'),fill=(255,255,0))
im.save(R/'renders/qa/R385_roof_outline_controls.png')
(R/'reports/R385_ROOF_BOUNDARIES.json').write_text(json.dumps(dict(outline=xy,pixels=pixels,controls=rows,source='R336 orthographic view plus classified ACT2024 level samples; outline candidate'),indent=2))
print(rows)
