exec(open(__file__.replace('measure_r563_return_plateau.py','measure_r500_west_terrace.py'),encoding='utf-8').read().split('line=')[0])
from PIL import Image,ImageDraw
q=p[(cl==1)&(p[:,0]>47)&(p[:,0]<53)&(p[:,1]>-59)&(p[:,1]<-52)&(p[:,2]>-4)&(p[:,2]<-.5)]
# Inspect all low non-ground returns; do not silently treat canopy as masonry.
rows=[]
for y in np.arange(-58.5,-52.49,.5):
 for x in np.arange(47.25,52.76,.5):
  a=q[(abs(q[:,0]-x)<.24)&(abs(q[:,1]-y)<.24)]
  if len(a)>1:rows.append(dict(x=float(x),y=float(y),n=len(a),z=np.quantile(a[:,2],[.1,.5,.9]).tolist()))
im=Image.new('RGB',(900,850),'white');dr=ImageDraw.Draw(im)
for a in rows:
 x=50+(a['x']-47)*125;y=50+(-52-a['y'])*110;z=a['z'][1];color=(int(min(255,max(0,(z+4)/3.5*255))),120,120);dr.rectangle((x-25,y-22,x+25,y+22),fill=color);dr.text((x-21,y-8),f'{z:.2f}',fill='black')
im.save(R/'renders/qa/R563_return_lidar_cells.png');(R/'reports/R563_RETURN_PLATEAU_CELLS.json').write_text(json.dumps(rows,indent=2));print('cells',len(rows))
