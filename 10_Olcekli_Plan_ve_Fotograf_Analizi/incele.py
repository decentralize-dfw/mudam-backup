from pathlib import Path
import sys,json,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'.deps'))
import pyproj,fitz
from PIL import Image,ImageDraw,ImageFont
r=ET.parse(BASE/'kaynak_veri/mudam_osm_dogu.osm').getroot()
nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in r.findall('node')}
t=pyproj.Transformer.from_crs(4326,32632,always_xy=True)
ways=[]
for w in r.findall('way'):
    tags={x.get('k'):x.get('v') for x in w.findall('tag')}
    coords=[nodes[n.get('ref')] for n in w.findall('nd') if n.get('ref') in nodes]
    ways.append(dict(id=w.get('id'),tags=tags,coordinates=coords,xy=[t.transform(*p) for p in coords],node_ids=[n.get('ref') for n in w.findall('nd')]))
m=next(w for w in ways if w['id']=='9042342')
print('Mudam',m)
(BASE/'kaynak_veri/osm_ways_utm.json').write_text(json.dumps(ways,ensure_ascii=False),encoding='utf-8')
cx=sum(p[0] for p in m['xy'])/len(m['xy']);cy=sum(p[1] for p in m['xy'])/len(m['xy'])
im=Image.new('RGB',(1500,1300),'white');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
scale=5
def pp(x,y):return 750+(x-cx)*scale,650-(y-cy)*scale
for w in ways:
    pts=[pp(*p) for p in w['xy']]
    if len(pts)<2:continue
    if 'building' in w['tags']:d.polygon(pts,fill='#efefec',outline='#bdbdb8')
    elif 'highway' in w['tags']:d.line(pts,fill='#c8c6b4',width=3)
    elif w['tags'].get('barrier') in ['wall','retaining_wall']:d.line(pts,fill='#bbb',width=2)
d.polygon([pp(*p) for p in m['xy']],fill='#c4e5f2',outline='#167093')
for j,p in enumerate(m['xy'][:-1]):
    x,y=pp(*p);d.ellipse((x-3,y-3,x+3,y+3),fill='red');d.text((x+4,y-8),str(j),font=font,fill='#a00000')
d.text((25,20),'OSM 9042342 / EPSG:32632 / North up',font=font,fill='black')
im.save(BASE/'kaynak_veri/osm_kose_kontrol.png')
doc=fitz.open(BASE.parent/'08_Belgeler/Mudam_Wim_Delvoye_2016_kat_semalari.pdf')
p=doc[4]
(BASE/'kaynak_veri/resmi_vektor_plan_sayfa5.svg').write_text(p.get_svg_image(),encoding='utf-8')
print('pdf vector paths',len(p.get_drawings()))
