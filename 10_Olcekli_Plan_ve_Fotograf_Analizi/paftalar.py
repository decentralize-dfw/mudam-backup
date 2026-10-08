from pathlib import Path
import json,base64,io,math,textwrap,html,sys
from PIL import Image,ImageOps
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'.deps'))
import pymupdf
D=json.loads((B/'atlas_data.json').read_text(encoding='utf-8'))
def uri(path,size=1400):
    im=ImageOps.exif_transpose(Image.open(path)).convert('RGBA');im.thumbnail((size,size))
    out=io.BytesIO();im.save(out,format='PNG');return 'data:image/png;base64,'+base64.b64encode(out.getvalue()).decode()
plans={l:uri(B/'01_Planlar'/f'kat_{l}_harita_katmani.png') for l in ['0','1','-1']}
def lines(s,x,y,width=86,size=17):
    return ''.join(f'<text x="{x}" y="{y+i*(size+7)}" font-size="{size}">{html.escape(t)}</text>' for i,t in enumerate(textwrap.wrap(s,width)))
for p in D['photos']:
    if len(sys.argv)>1 and p['id'] not in sys.argv[1:]:continue
    level=p['level'] if p['level'] in plans else '0'
    x,y=p['x_m'],p['y_m'];r=p['radius_m'] or 0
    xmin,ymin,xmax,ymax=-90,-100,90,80
    if x is not None:xmin=min(xmin,x-r-10);xmax=max(xmax,x+r+10);ymin=min(ymin,y-r-10);ymax=max(ymax,y+r+10)
    extent=max(xmax-xmin,ymax-ymin);cx=(xmin+xmax)/2;cy=(ymin+ymax)/2;xmin=cx-extent/2;ymin=cy-extent/2
    matrix=' '.join(map(str,D['worldmatrix']))
    content=D['basemap']+f'<g transform="matrix({matrix})"><image href="{plans[level]}" width="1108" height="960" opacity=".85"/></g>'+D['outline']
    color='#087b93' if p['quality']=='estimate' else '#b77b18'
    if x is not None:
        content+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" fill-opacity=".13" stroke="{color}" stroke-width=".4" stroke-dasharray="1 1"/>'
        if p['target_world']:
            tx,ty=p['target_world'];a=math.atan2(ty-y,tx-x);da=math.radians(p['angle_uncertainty_deg']);L=20
            q=[(x,y),(x+L*math.cos(a-da),y+L*math.sin(a-da)),(x+L*math.cos(a+da),y+L*math.sin(a+da))]
            content+='<polygon points="'+' '.join(f'{u},{v}' for u,v in q)+f'" fill="{color}" fill-opacity=".2"/>'
            ex,ey=x+L*math.cos(a),y+L*math.sin(a)
            content+=f'<path d="M{x} {y} L{ex} {ey}" stroke="{color}" stroke-width=".9"/>'
        content+=f'<circle cx="{x}" cy="{y}" r="1.7" fill="{color}"/><text x="{x+3}" y="{y-3}" font-size="4" fill="{color}">{p["id"]}</text>'
    content+=f'<path d="M{xmin+10} {ymin+extent-10} h20" stroke="black" stroke-width=".6"/><text x="{xmin+10}" y="{ymin+extent-13}" font-size="3.5">20 m</text><text x="{xmin+extent-28}" y="{ymin+9}" font-size="3.5">N (UTM) ↑</text>'
    quality={'estimate':'TAHMİNİ KONUM + YÖN','region':'YALNIZCA ADAY BÖLGE','unresolved':'KONUM ÇÖZÜLEMEDİ'}[p['quality']]
    heading=f'≈ {p["heading_deg"]}° ±{p["angle_uncertainty_deg"]}° (gerçek kuzeyden)' if p['heading_deg'] is not None else 'Yön belirlenemedi'
    note=f'Kat/alan: {p["level"]} | {heading} | Aday yarıçap: {r} m' if x is not None else 'Bu fotoğrafın kamera noktası denetimde doğrulanamadı; haritada gösterilmiyor.'
    note+=' | Kamera/ölçü onayı: YOK'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1040" viewBox="0 0 1500 1040"><rect width="1500" height="1040" fill="white"/><g font-family="Arial" fill="#18373b"><text x="30" y="43" font-size="27">MUDAM / FOTOĞRAF {p["id"]} / {quality}</text>'+lines(p['area'],30,75,120,20)
    mapsvg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="1300" viewBox="{xmin} {ymin} {extent} {extent}"><rect x="{xmin}" y="{ymin}" width="{extent}" height="{extent}" fill="#f4f3ed"/>{content}</svg>'
    mapdoc=pymupdf.open(stream=mapsvg.encode(),filetype='svg')
    mapuri='data:image/png;base64,'+base64.b64encode(mapdoc[0].get_pixmap().tobytes('png')).decode()
    svg+=f'<image href="{mapuri}" x="55" y="100" width="650" height="650"/><image href="{uri(B.parent/p["path"])}" x="755" y="100" width="715" height="650" preserveAspectRatio="xMidYMid meet"/>'
    svg+=lines(note,30,787,130,19)+lines(p['evidence'],30,825,145,18)+lines('Düşey bakış: '+p['pitch']+'. Daire ve fan görsel yorum aralığıdır; ölçüm doğruluğu veya objektif görüş açısı değildir.',30,900,155,16)+lines('Plan: Mudam | Harita: © OpenStreetMap contributors / ODbL | Fotoğraf: '+p['credit'],30,964,160,15)+lines('Harita eşleştirme RMS: 1,02 m; ayrılmış kontrol RMS: 1,91 m. Pafta haritasında ölçek çubuğunu kullanın.',30,1010,160,15)+'</g></svg>'
    destination=B/'05_Fotograf_Paftalari'/f'foto_{p["id"]}.svg'
    temporary=destination.with_suffix('.svg.tmp')
    temporary.write_text(svg,encoding='utf-8')
    temporary.replace(destination)
    if p['id'] in ['021','071','087','122']:
        doc=pymupdf.open(stream=svg.encode(),filetype='svg');doc[0].get_pixmap().save(B/'04_Onizlemeler'/f'foto_{p["id"]}.png')
print('İstenen fotoğraf paftaları hazır')
