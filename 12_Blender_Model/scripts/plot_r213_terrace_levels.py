from pathlib import Path
import json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];r=json.loads((R/'config/r213_access_measured.json').read_text())[-1];im=Image.new('RGB',(900,700),'white');d=ImageDraw.Draw(im)
for x,y,z in r['measurements']:
 px=60+(x+35)*25;py=620-(y-372)*25;t=max(0,min(1,z/4));color=(int(255*t),50,int(255*(1-t)));d.ellipse((px-4,py-4,px+4,py+4),fill=color)
for x in range(-35,-4,5):d.text((60+(x+35)*25,640),str(x),fill='black')
for y in range(372,397,4):d.text((10,620-(y-372)*25),str(y),fill='black')
d.text((300,20),'Reference heights: blue 0m - red 4m',fill='black');im.save(R/'renders/qa/R213_terrace_measurement_plot.png')
