"""Plot evaluated wall sections without treating the visitor diagrams as survey drawings."""
from pathlib import Path
import json,re
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/DUVAR_ENVANTERI.json').read_text());m=json.loads((B/'references/source_manifest.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];revision=re.search(r'_R\d+_',r['scene'])[0].strip('_')
for level,id in [('L00','102'),('LP1','103'),('LM1','104'),('PAV_LM1','104')]:
 im=Image.open(R/next(s['path'] for s in m if s['id']==id)).convert('RGB')
 if id=='104':
  scale,dx,dy=C['basement_registration']['source_to_canonical'];im=im.transform((1108,960),Image.Transform.AFFINE,(1/scale,0,-dx/scale,0,1/scale,-dy/scale),Image.Resampling.BICUBIC,fillcolor='white')
 im=Image.blend(im,Image.new('RGB',im.size,'white'),.4);d=ImageDraw.Draw(im)
 for sec in r['sections']:
  if sec['level']==level:
   for seg in sec['segments']:d.line([tuple(p) for p in seg],fill='#c02e22',width=2)
 d.rectangle((0,0,850,23),fill='white');d.text((10,7),f'{level} / {revision} wall sections. Geometry comparison; NOT surveyed accuracy.',fill='black');im.save(B/'references'/('DUVAR_KONTROL_'+level+'.png'))
 if revision=='R74' and level=='LP1':im.crop((455,589,550,715)).resize((665,882)).save(B/'renders/qa/R74_studio_plan.png')
print(revision,len(r['objects']),'classified wall candidates; four source overlays refreshed')
