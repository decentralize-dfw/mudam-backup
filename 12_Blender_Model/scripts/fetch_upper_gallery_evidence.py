"""Archive the project architect's published gallery/roof evidence with provenance."""
from urllib.request import Request,urlopen
from html.parser import HTMLParser
from pathlib import Path
import hashlib,json,re,io,html as html_module
from PIL import Image
R=Path(__file__).resolve().parents[2];D=R/'12_Blender_Model/references/upper_gallery_2007';D.mkdir(exist_ok=True,parents=True)
class Images(HTMLParser):
 def __init__(self):super().__init__();self.active=0;self.images=[];self.href=None
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='div':
   if self.active:self.active+=1
   elif 'post-body' in a.get('class',''):self.active=1
  if self.active:
   if t=='a':self.href=a.get('href')
   if t=='img':self.images.append(self.href or a.get('src'))
 def handle_endtag(self,t):
  if t=='div' and self.active:self.active-=1
  if t=='a':self.href=None
def fetch(url):return urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read()
manifest=[]
for post in ['photographs-of-completed-luxembourg','luxembourg-museum-gallery-opens']:
 url=f'https://imreyculbert.blogspot.com/2007/10/{post}.html';html=fetch(url);(D/(post+'.html')).write_bytes(html);parser=Images();parser.feed(html.decode('utf8'))
 for j,u in enumerate(parser.images):
  ident=('UG' if post.startswith('photographs') else 'UC')+f'{j+1:02d}';path=D/(ident+'.jpg')
  try:
   image_url=u.replace('http:','https:');content=fetch(image_url)
   if content.lstrip().startswith(b'<'):
    image_url=html_module.unescape(re.search(r'<img[^>]+src="([^"]+)"',content.decode('utf8')).group(1));content=fetch(image_url)
   im=Image.open(io.BytesIO(content));im.verify();path.write_bytes(content)
   manifest.append(dict(id=ident,path=path.relative_to(R).as_posix(),source_url=url,image_url=image_url,credit='Thomas Mayer, courtesy Imrey Culbert' if ident.startswith('UG') else 'Imrey Culbert; construction archive',publication_date='2007-10-05',sha256=hashlib.sha256(content).hexdigest(),camera_pose_verified=False))
   print(ident,len(content))
  except Exception as e:print(ident,'download failed',str(e))
(D/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('Evidence images saved:',len(manifest))
