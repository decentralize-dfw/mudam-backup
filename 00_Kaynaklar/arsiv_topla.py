from pathlib import Path
import re, json, urllib.request, urllib.parse, concurrent.futures, hashlib, io
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
items = []
def add(url, source, category, name='', credit=''):
    if any(x['url']==url for x in items): return
    items.append(dict(id=f'{len(items)+1:03}', url=url, source=source, category=category, name=name or Path(urllib.parse.urlparse(url).path).name, credit=credit))

wiki='https://es.wikiarquitectura.com/edificio/museo-de-arte-moderno-grand-duc-jean-mudam/'
for url in dict.fromkeys(re.findall(r'href="(https://es.wikiarquitectura.com/wp-content/uploads/[^"]+)"', (ROOT/'00_Kaynaklar/wikiarquitectura.html').read_text(encoding='utf-8'))):
    if not re.search(r'\.(jpg|jpeg|png)$',url,re.I): continue
    filename=Path(urllib.parse.urlparse(url).path).name
    if 'plantas' in filename: cat='01_Kat_Planlari'; name='Kat_planlari_mimari_pafta_WikiArquitectura.jpg'
    elif 'mudam-sec' in filename: cat='02_Kesitler'; name='Mimari_kesit_WikiArquitectura.jpg'
    elif 'mudam-empl' in filename: cat='03_Vaziyet_ve_Peyzaj'; name='Vaziyet_plani_WikiArquitectura.jpg'
    elif 'persp-ext' in filename: cat='06_Perspektif_ve_Cizimler'; name='Dis_perspektif_cizimi_WikiArquitectura.jpg'
    else: cat='Gecici'; name=filename
    add(url,wiki,cat,name,'WikiArquitectura; sayfadaki fotoğraf serisi Haziran 2019')

arch='https://archeyes.com/the-mudam-by-i-m-pei-where-old-meets-new/'
s=(ROOT/'00_Kaynaklar/archeyes.html').read_text(encoding='utf-8')
for url in dict.fromkeys(re.findall(r'https://(?:i0.wp.com/)?archeyes.com/wp-content/uploads/[^\s<>"?]+\.(?:jpg|png|jpeg)',s)):
    if not any(x in url.lower() for x in ['musam','mudam']): continue
    url=url.replace('https://i0.wp.com/','https://')
    filename=Path(urllib.parse.urlparse(url).path).name
    drawing='Michael-Nguyen' not in filename
    add(url,arch,'06_Perspektif_ve_Cizimler' if drawing else 'Gecici',filename,'I. M. Pei (çizim; kaynak atfı)' if drawing else '© Michael Nguyen / ArchEyes')

for level,filename in [('0','image_2025-09-08-141746_igpk.jpeg'),('arti_1','image_2025-09-08-141833_bosb.jpeg'),('eksi_1','image_2025-09-08-141851_vxua.jpeg')]:
    add('https://d2smv9sex1hihw.cloudfront.net/images/_default_4/'+filename,'https://www.mudam.com/fr/floor-plans','01_Kat_Planlari',f'Mudam_resmi_kat_plani_{level}.jpeg','Mudam Luxembourg; kullanıcı tarafından verilen doğrudan bağlantı')
add('https://d2smv9sex1hihw.cloudfront.net/documents/2026_03_17_EDUBOX_JK.pdf','https://www.mudam.com','08_Belgeler','Mudam_EDUBOX_2026.pdf','Mudam Luxembourg')
add('https://fondskirchberg.public.lu/dam-assets/publications/LCTO-Archi-web-EN.pdf','https://fondskirchberg.public.lu','08_Belgeler','Kirchberg_mimarlik_gezi_rehberi_EN.pdf','Fonds Kirchberg / LCTO')

def fetch(x):
    dest=ROOT/('00_Kaynaklar/Indirilenler' if x['category']=='Gecici' else x['category'])/(x['id']+'_'+x['name'])
    dest.parent.mkdir(parents=True,exist_ok=True)
    try:
        req=urllib.request.Request(x['url'],headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=40) as r: data=r.read()
        if dest.suffix.lower()!='.pdf':
            with Image.open(io.BytesIO(data)) as im: x['width'],x['height']=im.size; im.verify()
        elif not data.startswith(b'%PDF'): raise ValueError('PDF yerine farklı içerik geldi')
        dest.write_bytes(data)
        x.update(path=dest.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),status='ok')
    except Exception as e: x.update(status='error',error=str(e))
    print(x['id'], x['status'], x['name'],flush=True)
    return x

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: items=list(pool.map(fetch,items))
    (ROOT/'00_Kaynaklar/envanter.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
    imgs=[x for x in items if x['status']=='ok' and 'width' in x]
    for start in range(0,len(imgs),24):
        batch=imgs[start:start+24]; sheet=Image.new('RGB',(1440,((len(batch)+3)//4)*260),'#eeeeee'); d=ImageDraw.Draw(sheet)
        for j,x in enumerate(batch):
            with Image.open(ROOT/x['path']) as im: thumb=ImageOps.contain(im.convert('RGB'),(350,230))
            xx=(j%4)*360; yy=(j//4)*260
            sheet.paste(thumb,(xx+(350-thumb.width)//2,yy))
            d.text((xx+8,yy+232),x['id']+' '+x['name'][:41],fill='black')
        sheet.save(ROOT/'00_Kaynaklar'/f'kontrol_{start//24+1:02}.jpg')
    print('TOTAL',len(items),'OK',sum(x['status']=='ok' for x in items),flush=True)
