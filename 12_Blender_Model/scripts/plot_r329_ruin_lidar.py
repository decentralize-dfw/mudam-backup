from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<lidar coordinates>','exec'))
from PIL import Image,ImageDraw
for label,file,cx,cy,scale in [('north','R326_NORTH_RUIN_PLAN.json',-35,68,44),('east','R327_EAST_RUIN_PLAN.json',60,-30,42)]:
 im=Image.new('RGB',(1200,900),'#eeeeee');draw=ImageDraw.Draw(im);pixel=scale/1200
 keep=(np.abs(p[:,0]-cx)<scale/2)&(np.abs(p[:,1]-cy)<scale*3/8)&np.isin(cl,[1,6])&(p[:,2]>-1)&(p[:,2]<1)
 for point in p[keep]:
  x=(point[0]-cx+scale/2)/pixel;y=(cy+scale*3/8-point[1])/pixel;t=max(0,min(1,(point[2]+.5)/1.0));color=(int(20+160*t),int(100+80*(1-t)),int(180-130*t));draw.ellipse((x-1,y-1,x+1,y+1),fill=color)
 report=json.loads((R/'reports'/file).read_text())
 for polygon in [report['outline'],*report['recesses']]:draw.line([tuple(a) for a in polygon]+[tuple(polygon[0])],fill='#d90030',width=2)
 draw.text((15,15),'Independent LiDAR architectural returns (-1m to +1m); red: current authored outlines',fill='black')
 im.save(R/f'renders/qa/R329_{label}_lidar_plan.png')
print('R329_LIDAR_PLAN_READY')
