"""Archive public building-authority image references with provenance."""
from pathlib import Path
import urllib.request,re,html,json,hashlib,concurrent.futures
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';out=B/'references/government_2006';out.mkdir(exist_ok=True);url='https://travaux.public.lu/fr/projets/projets-batiments/2006/nca.html';page=urllib.request.urlopen(url,timeout=30).read().decode();(out/'page.html').write_text(page,encoding='utf8');urls=sorted(set(re.findall(r'(?:https://travaux.public.lu)?/dam-assets/fr/abp/projets/realises/2006/nca/galeries/photos/[^"<>? /]+\.jpg',page)))
def fetch(u):
 u=html.unescape(u);u=('https://travaux.public.lu'+u) if u.startswith('/') else u;p=out/u.rsplit('/',1)[1]
 try:
  data=urllib.request.urlopen(u,timeout=25).read();p.write_bytes(data);im=Image.open(p);return dict(id='BP_'+p.stem,path=p.relative_to(R).as_posix(),source_url=u,source_page=url,sha256=hashlib.sha256(data).hexdigest(),size=list(im.size),credit='Administration des batiments publics; photo credits vary, see archived page',source_date='2006 project page; individual capture date unverified')
 except Exception as e:return dict(url=u,error=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:rows=list(ex.map(fetch,urls))
(out/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8');ok=[r for r in rows if 'path' in r];assert ok;im=Image.new('RGB',(1200,((len(ok)+3)//4)*230),'white');d=ImageDraw.Draw(im)
for i,r in enumerate(ok):
 a=Image.open(R/r['path']).convert('RGB');a.thumbnail((290,205));x=(i%4)*300;y=(i//4)*230;im.paste(a,(x,y+22));d.text((x+5,y+4),r['id'],fill='black')
im.save(B/'references/R39_government_contact_sheet.jpg');print('downloaded',len(ok),'failures',[x for x in rows if 'error' in x])
