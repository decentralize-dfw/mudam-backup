from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'scripts/measure_r328_independent_lidar.py').read_text();exec(compile(s[:s.index('rows=[]')],'<x>','exec'))
from PIL import Image,ImageDraw
im=Image.new('RGB',(1200,1000),'white');d=ImageDraw.Draw(im)
mask=(p[:,0]>-5.5)&(p[:,0]<69.5)&(p[:,1]<-18.75)&(p[:,1]>-81.25)&np.isin(cl,[1,2,6])&(p[:,2]<0)
q=p[mask];q=q[np.argsort(q[:,2])]
for x,y,z in q:
 px=(x+5.5)*16;py=(-18.75-y)*16;t=max(0,min(1,(z+9)/9));col=(int(255*t),int(200*(1-abs(t-.5)*2)),int(255*(1-t)));d.ellipse((px-1,py-1,px+1,py+1),fill=col)
im.save(R/'renders/qa/R351_pavilion_lidar.png')
