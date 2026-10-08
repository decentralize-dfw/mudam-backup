from arsiv_topla import ROOT, fetch
import json, re, html, concurrent.futures, urllib.parse, urllib.request
from PIL import Image, ImageOps, ImageDraw

items=json.loads((ROOT/'00_Kaynaklar/envanter.json').read_text(encoding='utf-8'))
extra=[]
def add(url,source,cat,name,credit):
    extra.append(dict(id=f'{107+len(extra):03}',url=url,source=source,category=cat,name=name,credit=credit))
s=html.unescape((ROOT/'00_Kaynaklar/mudam_mimarlik.html').read_text(encoding='utf-8')).replace('\\/','/')
for url in sorted(set(re.findall(r'https://dbf[^\s"<>]+/images/_huge/[^\s"<>]+\.webp',s))):
    url=re.sub(r'\\u([0-9a-fA-F]{4})',lambda m:chr(int(m[1],16)),url)
    filename=url.rsplit('/',1)[1]
    add(urllib.parse.quote(url,safe=':/%'),'https://www.mudam.com/visit/architecture','Gecici','Mudam_resmi_'+filename,'Mudam Luxembourg; sayfadaki fotoğraf kredisine bakınız')
s=(ROOT/'00_Kaynaklar/greatgardens.html').read_text(encoding='utf-8')
for url in dict.fromkeys(re.findall(r'href="(https://www.greatgardensoftheworld.com/wp-content/uploads/[^\s"]+Luxembourg[^\s"]+\.jpg)"',s)):
    add(urllib.parse.quote(url,safe=':/%'),'https://www.greatgardensoftheworld.com/gardens/michel-desvigne/','03_Vaziyet_ve_Peyzaj/Park_Drai_Eechelen',url.rsplit('/',1)[1],'© MDP / Great Gardens of the World')
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: items+=list(pool.map(fetch,extra))
for x in items:
    if x['status']!='error' or 'resmi_kat' not in x['name']:continue
    filename=x['url'].rsplit('/',1)[1]
    candidates=[x['url'],x['url'].replace('/_default_4/','/'),x['url'].replace('d2smv9sex1hihw','dbf642yz813mr'),x['url'].replace('d2smv9sex1hihw','dbf642yz813mr').replace('/_default_4/','/')]
    for candidate in candidates:
        trial=dict(x);trial['url']=candidate
        result=fetch(trial)
        if result['status']=='ok':x.update(result);break
(ROOT/'00_Kaynaklar/envanter.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
batch=[x for x in extra if x['status']=='ok'];sheet=Image.new('RGB',(1440,((len(batch)+3)//4)*260),'#eee');d=ImageDraw.Draw(sheet)
for j,x in enumerate(batch):
    with Image.open(ROOT/x['path']) as im: thumb=ImageOps.contain(im.convert('RGB'),(350,230))
    xx=j%4*360;yy=j//4*260;sheet.paste(thumb,(xx,yy));d.text((xx+5,yy+233),x['id']+' '+x['name'][:36],fill='black')
sheet.save(ROOT/'00_Kaynaklar/kontrol_ek.jpg')
