import urllib.request,urllib.parse,json,concurrent.futures,io
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];out=R/'references/r541_moat_photos';out.mkdir(exist_ok=True)
params=dict(action='query',generator='categorymembers',gcmtitle='Category:Mudam',gcmtype='file',gcmlimit='100',prop='imageinfo',iiprop='url|extmetadata',iiurlwidth='500',format='json')
url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
def read(url):
 return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MudamModelReference/1.0 (architectural reference study)'}),timeout=45).read()
metadata=json.loads(read(url));(out/'metadata.json').write_text(json.dumps(metadata,indent=2));pages=list(metadata.get('query',{}).get('pages',{}).values())
def fetch(p):
 try:
  info=p['imageinfo'][0];data=read(info.get('thumburl',info['url']));im=Image.open(io.BytesIO(data));im.thumbnail((500,500));im.convert('RGB').save(out/(str(p['pageid'])+'.jpg'));return p
 except Exception as e:return dict(error=str(e),title=p.get('title'))
with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:results=list(pool.map(fetch,pages))
good=[p for p in results if 'error'not in p];sheet=Image.new('RGB',(1500,((len(good)+4)//5)*230),'white');draw=ImageDraw.Draw(sheet)
for k,p in enumerate(good):
 im=Image.open(out/(str(p['pageid'])+'.jpg'));im.thumbnail((294,195));x=(k%5)*300;y=(k//5)*230;sheet.paste(im,(x,y));draw.text((x,y+198),str(p['pageid']),fill='black');draw.text((x,y+211),p['title'][5:43],fill='black')
sheet.save(out/'contact_sheet.jpg');(out/'fetch_results.json').write_text(json.dumps(results,indent=2));print('REFERENCES',len(good),'/',len(pages))
