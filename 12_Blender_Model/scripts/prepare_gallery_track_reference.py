"""Analytical overlay: candidate runs against the unchanged 102 floor diagram."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
P=json.loads((B/'config/gallery_track_lights.json').read_text())
source=next(s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id']=='102')
im=Image.open(R/source['path']).convert('RGB');d=ImageDraw.Draw(im)
for track in P['tracks']:
 a,b=track['start'],track['end'];d.line([tuple(a),tuple(b)],fill='#a52821',width=4)
 for t in track['fixture_fractions']:
  x=a[0]+t*(b[0]-a[0]);y=a[1]+t*(b[1]-a[1]);d.ellipse((x-4,y-4,x+4,y+4),fill='#a52821',outline='white',width=1)
 d.text((a[0]+6,a[1]-14),track['id'],fill='#a52821')
canvas=Image.new('RGB',(im.width,im.height+70),'white');canvas.paste(im,(0,0));d=ImageDraw.Draw(canvas)
d.text((24,im.height+12),'R70 / CONDITIONAL PARTIAL LAYOUT - NOT A MEASURED LIGHTING PLAN',fill='#a52821')
d.text((24,im.height+34),'102 footprint; 061/062 fixture family. Count, coordinates and mounting dimensions remain candidates.',fill='black')
canvas.save(B/'references/R70_track_plan_candidates.png')
