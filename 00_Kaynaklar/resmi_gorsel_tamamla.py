from arsiv_topla import ROOT
import json, subprocess, concurrent.futures, re, hashlib
from PIL import Image
a=json.loads((ROOT/'00_Kaynaklar/envanter.json').read_text(encoding='utf-8'))
def recover(x):
    if x['status']!='error' or not x['name'].startswith('Mudam_resmi_') or 'kat_plani' in x['name']:return
    url=x['url'].replace('/_huge/','/_1600xAUTO_crop_center-center_none/')
    dest=ROOT/'00_Kaynaklar/Indirilenler'/(x['id']+'_'+x['name'])
    p=subprocess.run(['curl.exe','-sSL','--fail','--max-time','20',url,'-o',str(dest)],capture_output=True)
    if p.returncode==0:
        try:
            with Image.open(dest) as im:x['width'],x['height']=im.size;im.verify()
            data=dest.read_bytes();x.update(url=url,path=dest.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),status='ok');x.pop('error',None)
        except Exception as e:x['error']=str(e)
    else:x['error']=p.stderr.decode(errors='replace').strip()
    print(x['id'],x['status'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(recover,a))
x=next(x for x in a if x['id']=='103');dest=ROOT/'01_Kat_Planlari/Mudam_resmi_kat_plani_arti_1.jpeg'
if dest.exists():
    with Image.open(dest) as im:x['width'],x['height']=im.size;im.verify()
    data=dest.read_bytes();x.update(url=x['url'].replace('/_default_4/','/'),path=dest.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),status='ok');x.pop('error',None)
dest=ROOT/'08_Belgeler/Mudam_Wim_Delvoye_2016_kat_semalari.pdf';data=dest.read_bytes()
a.append(dict(id='125',name=dest.name,url='https://d2smv9sex1hihw.cloudfront.net/documents/EN_Wim_Delvoye_MUDAM_2016.pdf',source='https://www.mudam.com',category='08_Belgeler',path=dest.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),status='ok',credit='Mudam Luxembourg; 2016 sergi rehberi; tarihsel kat şemaları'))
(ROOT/'00_Kaynaklar/envanter.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
imgs=[x for x in a if int(x['id'])>=107 and x['status']=='ok' and 'width' in x]
from PIL import ImageOps, ImageDraw
sheet=Image.new('RGB',(1440,((len(imgs)+3)//4)*260),'#eee');d=ImageDraw.Draw(sheet)
for j,x in enumerate(imgs):
    with Image.open(ROOT/x['path']) as im:thumb=ImageOps.contain(im.convert('RGB'),(350,230))
    xx=j%4*360;yy=j//4*260;sheet.paste(thumb,(xx,yy));d.text((xx+5,yy+233),x['id']+' '+x['name'][:36],fill='black')
sheet.save(ROOT/'00_Kaynaklar/kontrol_ek.jpg')
