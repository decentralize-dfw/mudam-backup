from pathlib import Path
import sys,json,math,base64,io,re,csv,html,copy
from collections import Counter
BASE=Path(__file__).resolve().parent;ROOT=BASE.parent
sys.path.insert(0,str(BASE/'.deps'))
import numpy as np,pymupdf
from PIL import Image,ImageOps,ExifTags,ImageDraw
from pyproj import Transformer,CRS
from fotograf_yorumlari import D
C=json.loads((BASE/'kalibrasyon.json').read_text(encoding='utf-8'))
A=np.array(C['pdf_to_utm_matrix']);k=C['canonical_to_pdf_scale'];off=np.array(C['canonical_to_pdf_offset'])
T=A[:,:2]*k;tr=A[:,:2]@off+A[:,2]
E0,N0=293425.,5499960.
worldmatrix=[T[0,0],-T[1,0],T[0,1],-T[1,1],tr[0]-E0,N0-tr[1]]
inv=Transformer.from_crs(32632,4326,always_xy=True);geod=CRS(4326).get_geod()
def utm(p):return T@np.array(p)+tr
def world(p):
    e,n=utm(p);return float(e-E0),float(N0-n)
def data_uri(path):
    ext=Path(path).suffix.lower();mime={'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.webp':'image/webp'}[ext]
    return 'data:'+mime+';base64,'+base64.b64encode(Path(path).read_bytes()).decode()
def save_json(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def svg_to_png(svg,path,width=2400):
    doc=pymupdf.open(stream=svg.encode(),filetype='svg');p=doc[0];pix=p.get_pixmap(matrix=pymupdf.Matrix(width/p.rect.width,width/p.rect.width));pix.save(path)
for folder in ['01_Planlar','02_Harita','03_Fotograf_Konumlari','04_Onizlemeler','05_Fotograf_Paftalari']:(BASE/folder).mkdir(exist_ok=True)
inventory=json.loads((ROOT/'00_Kaynaklar/envanter.json').read_text(encoding='utf-8'));byid={x['id']:x for x in inventory}
plan_svgs={}
for level,ident in [('0','102'),('1','103'),('-1','104')]:
    uri=data_uri(ROOT/byid[ident]['path'])
    if level=='0':inner=f'<image href="{uri}" width="1108" height="960"/>'
    elif level=='1':
        inner=f'<g transform="translate(-.5 32)"><image href="{uri}" width="1108" height="960"/></g>'
        C['upper_registration']=dict(source_to_canonical=[1,-.5,32],method='Translation of common exterior tips; no distortion')
    else:
        s=573/517;dx=289.5-264*s;dy=161.5-147*s
        inner=f'<g transform="translate({dx} {dy}) scale({s})"><image href="{uri}" width="1000" height="866"/></g>'
        C['basement_registration']=dict(source_to_canonical=[s,dx,dy],method='Uniform scale + translation of common exterior tips; no distortion')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1108" height="960" viewBox="0 0 1108 960"><rect width="1108" height="960" fill="white"/>{inner}</svg>'
    plan_svgs[level]=svg
    path=BASE/'01_Planlar'/f'kat_{level}_ortak_olcek.svg';path.write_text(svg,encoding='utf-8')
    png=path.with_name(f'kat_{level}_4000px.png');svg_to_png(svg,str(png),4000)
    with Image.open(png) as im:width,height=im.size
    factor=1108/width
    wt=T*factor;center=tr+wt@np.array([.5,.5])
    png.with_suffix('.pgw').write_text('\n'.join(f'{x:.12f}' for x in [wt[0,0],wt[1,0],wt[0,1],wt[1,1],center[0],center[1]]),encoding='ascii')
    png.with_suffix('.prj').write_text(CRS(32632).to_wkt(),encoding='utf-8')
    # Map image has white-to-alpha only for diagram background compositing.
    with Image.open(png) as im:
        ar=np.array(im.convert('RGB'));alpha=np.clip((255-ar.min(axis=2)).astype(float)*2.8,0,255).astype('uint8')
        # Crop diagram callouts away from the map overlay only. Full-size source
        # exports retain all labels. Polygon follows the diagram, not the OSM fit.
        border=[(40,261),(91,213),(124,213),(173,261),(287,261),(287,158),(465,332),(687,332),(711,290),(746,242),(792,198),(865,158),(865,257),(942,337),(865,414),(865,535),(689,712),(617,714),(595,694),(557,694),(537,714),(464,713),(287,535),(287,299),(174,299),(124,347),(91,347),(40,297)]
        mask=Image.new('L',(width,height),0);ImageDraw.Draw(mask).polygon([(x/factor,y/factor) for x,y in border],fill=255)
        alpha=np.minimum(alpha,np.array(mask));rgba=np.dstack([ar,alpha]);Image.fromarray(rgba).save(BASE/'01_Planlar'/f'kat_{level}_harita_katmani.png')

# Exact source vectors for the two floors present in the official 2016 PDF.
doc=pymupdf.open(ROOT/'08_Belgeler/Mudam_Wim_Delvoye_2016_kat_semalari.pdf')
source=doc[4].get_svg_image()
for level,box in [('0',(290,225,240,153)),('1',(290,477,240,153))]:
    x,y,w,h=box;mm=C['meters_per_pdf_point']*2
    head=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w*mm:.6f}mm" height="{h*mm:.6f}mm" viewBox="{x} {y} {w} {h}">'
    svg=re.sub(r'<svg[^>]*>',head,source,count=1)
    path=BASE/'01_Planlar'/f'kat_{level}_2016_vektor_1_500.svg';path.write_text(svg,encoding='utf-8');svg_to_png(svg,str(path.with_suffix('.png')),5000)
with Image.open(ROOT/byid['083']['path']) as im:im.resize((3040,4656),Image.Resampling.LANCZOS).save(BASE/'01_Planlar/mimari_pafta_8x_referans_olceksiz.png')

ways=json.loads((BASE/'kaynak_veri/osm_ways_utm.json').read_text(encoding='utf-8'))
shapes=[];features=[]
for w in ways:
    pts=[[p[0]-E0,N0-p[1]] for p in w['xy']];tags=w['tags']
    if not pts or not any(-500<x<500 and -500<y<500 for x,y in pts):continue
    points=' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)
    if 'building' in tags:
        shapes.append(f'<polygon points="{points}" fill="#e5e3dc" stroke="#a7a59c" stroke-width="0.35"/>')
    elif tags.get('leisure')=='park' or tags.get('landuse') in ['forest','grass'] or tags.get('natural') in ['wood','scrub']:
        shapes.append(f'<polygon points="{points}" fill="#e9eddf" stroke="none"/>')
    elif 'highway' in tags:
        width=1 if tags['highway'] in ['footway','path','steps'] else 2.7
        shapes.append(f'<polyline points="{points}" fill="none" stroke="#cbc8bc" stroke-width="{width}"/>')
    elif tags.get('barrier') in ['wall','retaining_wall']:
        shapes.append(f'<polyline points="{points}" fill="none" stroke="#aaa392" stroke-width="0.7"/>')
    if w['id']=='9042342':
        mudam=w
        features.append(dict(type='Feature',properties=dict(osm_id=w['id'],source='OpenStreetMap contributors',license='ODbL',geometry_role='building_footprint_reference'),geometry=dict(type='Polygon',coordinates=[w['coordinates']])))
shapes.sort(key=lambda s:0 if '#e9eddf' in s else 2 if '#e5e3dc' in s else 1)
base='<g id="osm">'+''.join(shapes)+'</g>'
outline='<polygon points="'+' '.join(f'{p[0]-E0:.3f},{N0-p[1]:.3f}' for p in mudam['xy'])+'" fill="none" stroke="#bb3e20" stroke-width="0.45" stroke-dasharray="1.3 .8"/>'
save_json(BASE/'02_Harita/osm_bina_izi.geojson',dict(type='FeatureCollection',features=features))

photos=[x for x in inventory if x['status']=='ok' and 'width' in x and x['id'] not in ['082','083','084','085','096','101','102','103','104']]
assert set(D)=={x['id'] for x in photos},(set(D)-{x['id'] for x in photos},{x['id'] for x in photos}-set(D))
results=[];geo=[]
for x in photos:
    d=copy.deepcopy(D[x['id']]);d.update(id=x['id'],path=x['path'],source=x['source'],credit=x['credit'],width=x['width'],height=x['height'])
    ex=Image.open(ROOT/x['path']).getexif();ef=ex.get_ifd(34665);gps=ex.get_ifd(34853)
    d['capture_time']=str(ef.get(36867,''));d['camera_model']=str(ex.get(272,''));d['focal_length_mm']=float(ef[37386]) if ef.get(37386) else None
    d['panorama_metadata']='ICE' in str(ex.get(305,''));d['gps_coordinates_present']=bool(gps.get(2) and gps.get(4));d['fov_deg']=None
    d['fov_note']='Kadraj kırpması/düzeltmesi ve bazı dosyalardaki panorama birleştirmesi bilinmiyor; ışın fanı görüş alanı değil, yön yorumunun belirsizliğidir.'
    d['x_m']=d['y_m']=d['easting_m']=d['northing_m']=d['longitude']=d['latitude']=d['heading_deg']=None
    d['target_world']=None
    if d['xy']:
        e,n=utm(d['xy']);lon,lat=inv.transform(e,n);d.update(x_m=float(e-E0),y_m=float(N0-n),easting_m=float(e),northing_m=float(n),longitude=float(lon),latitude=float(lat))
        if d['target']:
            te,tn=utm(d['target']);tlon,tlat=inv.transform(te,tn);az,_,_=geod.inv(lon,lat,tlon,tlat)
            d['heading_deg']=int(round((az%360)/5)*5)%360;d['target_world']=list(world(d['target']))
    d['geometry_role']={'estimate':'visual_camera_estimate','region':'candidate_area_center_NOT_camera_position','unresolved':'unlocated'}[d['quality']]
    properties={key:value for key,value in d.items() if key not in ['xy','target','target_world']}
    geometry=dict(type='Point',coordinates=[round(d['longitude'],7),round(d['latitude'],7)]) if d['xy'] else None
    geo.append(dict(type='Feature',geometry=geometry,properties=properties));results.append(d)
save_json(BASE/'03_Fotograf_Konumlari/fotograf_konumlari.json',results)
save_json(BASE/'03_Fotograf_Konumlari/fotograf_konumlari.geojson',dict(type='FeatureCollection',features=geo))
cols=['id','level','quality','geometry_role','area','easting_m','northing_m','longitude','latitude','heading_deg','angle_uncertainty_deg','radius_m','pitch','evidence','capture_time','camera_model','focal_length_mm','panorama_metadata','gps_coordinates_present','fov_deg','fov_note','path','source']
with (BASE/'03_Fotograf_Konumlari/fotograf_konumlari.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');writer.writeheader();writer.writerows(results)

def img_layer(level,opacity=.72):
    uri=data_uri(BASE/'01_Planlar'/f'kat_{level}_harita_katmani.png')
    return '<g transform="matrix('+ ' '.join(f'{v:.10f}' for v in worldmatrix)+f')"><image href="{uri}" width="1108" height="960" opacity="{opacity}"/></g>'
def mark(p,labels=True):
    if p['x_m'] is None:return ''
    x,y=p['x_m'],p['y_m'];color='#087b93' if p['quality']=='estimate' else '#b77b18';r=p['radius_m']
    text=f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" fill-opacity=".05" stroke="{color}" stroke-opacity=".4" stroke-width=".25" stroke-dasharray="1 .8"/>'
    if p['target_world']:
        tx,ty=p['target_world'];dx,dy=tx-x,ty-y;norm=math.hypot(dx,dy);L=min(18,norm);ux,uy=dx/norm,dy/norm
        if norm:
            endx,endy=x+ux*L,y+uy*L
            text+=f'<path d="M{x} {y} L{endx} {endy}" stroke="{color}" stroke-width=".7" fill="none"/><path d="M{endx} {endy} L{endx-ux*2-uy} {endy-uy*2+ux} L{endx-ux*2+uy} {endy-uy*2-ux}Z" fill="{color}"/>'
    text+=f'<circle cx="{x}" cy="{y}" r="1.25" fill="{color}" stroke="white" stroke-width=".3"/>'
    if labels:text+=f'<text x="{x+1.6}" y="{y-1.7}" font-family="Arial" font-size="2.5" fill="{color}" stroke="white" stroke-width=".6" paint-order="stroke">{p["id"]}</text>'
    return text
def map_sheet(level,with_marks=False):
    x,y,w,h=-90,-100,180,180
    marks=''.join(mark(p) for p in results if p['level']==level) if with_marks else ''
    content=base+img_layer(level)+outline+marks
    for c in C['controls']:
        if with_marks:continue
        ex,ny=c['utm'];sx,sy=ex-E0,N0-ny;color='#a1341b' if c['role']=='fit' else '#6035a6'
        content+=f'<circle cx="{sx}" cy="{sy}" r=".8" fill="white" stroke="{color}" stroke-width=".25"/>'
    title=f'MUDAM | KAT {level} | 1:500'+(' | GORSEL KAMERA TAHMINLERI' if with_marks else ' | OSM KALIBRASYONU')
    footer='OSM ile uyum: 9 kontrol RMS 1.02 m / 2 dis kontrol RMS 1.91 m. Olcum projesi degildir.'
    content+=f'<rect x="-90" y="-100" width="180" height="12" fill="white"/><text x="-87" y="-95" font-size="3.4" font-family="Arial">{title}</text><text x="-87" y="-91" font-size="2.3" font-family="Arial">EPSG:32632 | Plan: Mudam | Harita: OpenStreetMap contributors / ODbL</text><rect x="-90" y="69" width="180" height="11" fill="white"/><text x="-87" y="73" font-size="2.1" font-family="Arial">{footer}</text><path d="M-80 65 H-60 M-80 64 V66 M-70 64 V66 M-60 64 V66" stroke="black" stroke-width=".4"/><text x="-80" y="62" font-size="2.8" font-family="Arial">0          10          20 m</text><path d="M78 -67 V-83 l-2 4 m2 -4 l2 4" stroke="black" stroke-width=".5" fill="none"/><text x="76.5" y="-85" font-size="3" font-family="Arial">N (UTM)</text>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="360mm" height="360mm" viewBox="{x} {y} {w} {h}">{content}</svg>'
for level in ['0','1','-1']:
    for marks in [False,True]:
        svg=map_sheet(level,marks);name=f'kat_{level}_'+('fotograf_isaretleri' if marks else 'OSM_eslestirme_1_500')
        (BASE/'02_Harita'/f'{name}.svg').write_text(svg,encoding='utf-8');svg_to_png(svg,str(BASE/'04_Onizlemeler'/f'{name}.png'),2600)

# Metre-based CAD reference, 1 drawing unit = 1 metre, global UTM coordinates.
dxf=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1015','9','$INSUNITS','70','6','0','ENDSEC','0','SECTION','2','ENTITIES']
for w in [mudam]:
    dxf+=['0','LWPOLYLINE','8','OSM_REFERENCE','90',str(len(w['xy'])-1),'70','1']
    for e,n in w['xy'][:-1]:dxf+=['10',str(e),'20',str(n)]
for p in results:
    if p['quality']!='estimate':continue
    e,n=p['easting_m'],p['northing_m'];dxf+=['0','POINT','8','PHOTO_ESTIMATES','10',str(e),'20',str(n),'30','0']
    if p['target']:
        te,tn=utm(p['target']);dxf+=['0','LINE','8','PHOTO_DIRECTIONS','10',str(e),'20',str(n),'11',str(te),'21',str(tn)]
    dxf+=['0','TEXT','8','PHOTO_IDS','10',str(e+1),'20',str(n+1),'40','1','1',p['id']]
dxf+=['0','ENDSEC','0','EOF'];(BASE/'02_Harita/OSM_bina_ve_kamera_tahminleri_metre.dxf').write_text('\n'.join(dxf),encoding='ascii')
save_json(BASE/'kalibrasyon.json',C)
save_json(BASE/'atlas_data.json',dict(photos=results,calibration=C,worldmatrix=worldmatrix,origin=[E0,N0],basemap=base,outline=outline))
(BASE/'atlas_data.js').write_text('window.MUDAM_DATA='+json.dumps(dict(photos=results,calibration=C,worldmatrix=worldmatrix,origin=[E0,N0],basemap=base,outline=outline),ensure_ascii=False,allow_nan=False)+';',encoding='utf-8')
print('PHOTOS',len(results),dict(Counter(p['quality'] for p in results)))
print('OUTPUT COMPLETE')
