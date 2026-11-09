from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<coordinates>','exec'))
from PIL import Image,ImageDraw
center=np.array([-46.727,-38.136]);axis=np.array([1,1])/2**.5;normal=np.array([-1,1])/2**.5;dp=p[:,:2]-center;u=dp@axis;t=dp@normal;mask=(abs(u)<.4)&(abs(t)<15)&(p[:,2]>0)&(p[:,2]<6)&np.isin(cl,[1,2,6]);q=np.column_stack([t[mask],p[mask,2]]);im=Image.new('RGB',(1200,500),'white');draw=ImageDraw.Draw(im)
for tx,z in q:
 x=600+tx*35;y=450-z*65;draw.ellipse((x-2,y-2,x+2,y+2),fill=(35,70,160))
for z in range(7):draw.line([(50,450-z*65),(1150,450-z*65)],fill=(200,200,200));draw.text((5,450-z*65),str(z),fill='black')
rows=[]
for a in np.arange(-12,12,.5):
 z=q[(q[:,0]>=a)&(q[:,0]<a+.5),1]
 if len(z):rows.append([round(float(a),2),len(z),*[round(float(v),3) for v in np.quantile(z,[.1,.5,.9])]])
print(rows);im.save(R/'renders/qa/R383_fort_cross_section.png');(R/'reports/R383_FORT_SECTION.json').write_text(json.dumps(dict(center=center.tolist(),normal=normal.tolist(),samples=rows),indent=2))
