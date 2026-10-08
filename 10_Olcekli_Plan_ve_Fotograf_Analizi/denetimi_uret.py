"""Reproducible visual audit. Observations are human-readable evidence, not pose solves."""
from pathlib import Path
import json, copy, html
from collections import Counter
B=Path(__file__).resolve().parent; R=B.parent; O=B/'06_Tek_Tek_Denetim'
snapshot=O/'denetim_oncesi_atlas.json'
if not snapshot.exists():
    snapshot.write_text((B/'atlas_data.json').read_text(encoding='utf-8'),encoding='utf-8')
old=json.loads(snapshot.read_text(encoding='utf-8'))['photos']; byid={p['id']:p for p in old}
inventory={p['id']:p for p in json.loads((R/'00_Kaynaklar/envanter.json').read_text(encoding='utf-8'))}
overrides={}
def edit(ids,**fields):
    for i in ids: overrides.setdefault(f'{i:03}',{}).update(fields)
def unloc(ids,area=None,level=None):
    fields=dict(xy=None,target=None,quality='unresolved',radius_m=None,angle_uncertainty_deg=None)
    if area:fields['area']=area
    if level:fields['level']=level
    edit(ids,**fields)
def region(ids,xy=None,area=None,level=None,radius=None):
    fields=dict(target=None,quality='region',angle_uncertainty_deg=None)
    for key,val in [('xy',xy),('area',area),('level',level),('radius_m',radius)]:
        if val is not None:fields[key]=val
    edit(ids,**fields)
unloc([1],area='Pavyon ve nişli galeri / meydan tarafından')
region([5,11,12])
region([17],xy=[649,529],area='Grand Hall / asansör ve galeri geçişi adayı',radius=8)
unloc([19],area='Kavisli taş duvar / üst birleşim',level='belirsiz');edit([19],stair_system=None)
unloc([20],area='Duvara işlenmiş plan ve yönlendirme',level='belirsiz')
edit([23],area='0→+1 merdiveninin alt başlangıç korkuluğu',pitch='yakın detay; hafif aşağı')
region([30],xy=[575,425],area='Grand Hall / üçgen cam köşe detayı',radius=18)
region([31],xy=[575,440],radius=15)
region([32],xy=[454,419],area='Grand Hall → Jardin des Sculptures geçişi',radius=8)
region([33],xy=[380,345],area='Jardin des Sculptures / Grand Hall yönü',radius=12)
edit([42,44,50,54],level='ara')
edit([43],level='1',area='Doğu spiral merdiveni / üst sahanlık',pitch='üst sahanlıktan aşağı')
region([54],radius=9)
region([55],xy=[625,391],area='Alt fuaye / iniş boşluğunun altından çatıya',level='-1',radius=9)
edit([55],stair_system='STAIR_GH_DOWN_0_TO_MINUS1')
region([56],xy=[388,530],area='Zemin galeri eşiği / doğu kanadı adayı',radius=20)
unloc([57,58,60],area='Galeri / kat ve kanat çözülemedi',level='belirsiz')
region([61,62,63],xy=[388,613],area='Girişe yakın nişli galeri pencereleri / aday alan',radius=18)
region([64],xy=[575,385],area='Grand Hall / pavyona bakan cam çevresi adayı',radius=18)
region([66],xy=[893,345],area='Batı cam merdiven hacmi / 097 ile aday eşleşme',level='ara',radius=12)
edit([66,97],stair_system='STAIR_WEST_GLAZED_CANDIDATE')
edit([67],target=[110,280],area='Cam bağlantıdan pavyona doğru bakış')
unloc([69,70],area='Ahşap çift kanat kapı / oda ve kat belirsiz',level='belirsiz')
edit([79],area='Taş duvardaki teknik ızgara / işlev belirsiz')
region([89])
unloc([90],area='Düz eğik cam örtü ve geride pavyon feneri')
unloc([91],area='Taş parapet üstünde cam fener / cephe belirsiz')
unloc([94],area='Taş cephe ve düşey cam yarık / kanat belirsiz')
unloc([97],area='Batı cam merdiven hacmi / dış görünüş adayı')
unloc([108],area='Fort ve Mudam uzak görünüşü / çekim noktası belirsiz')
unloc([109],area='Pavyon ve nişli galeri / ağaçlar arkasından')
region([110])
region([114],xy=[591,428],area='Grand Hall / aşağı iniş üzerindeki üçgen cam',radius=12)
edit([114],stair_system='STAIR_GH_DOWN_0_TO_MINUS1')
unloc([116],area='Yüksekten giriş, pavyon ve çatı görünüşü')
unloc([124],area='Meydan / köprü / tarihi duvar panoraması')
rows=[]
for line in (O/'gozlemler.txt').read_text(encoding='utf-8').splitlines():
    ident,observed,refs,decision=line.split('|')
    p=byid[ident]; changes=overrides.get(ident,{})
    crosschecks=refs.split(',')
    level=changes.get('level',p['level'])
    quality=changes.get('quality',p['quality'])
    rows.append(dict(id=ident,review_date='2026-10-08',review_status='visually_reviewed',
        inspection='Individual image reviewed in 6-image sheets; ambiguous critical details enlarged. Plans 102/103/104 and section 101 also inspected.',
        observed_features=observed,crosscheck_ids=crosschecks,decision=decision,
        source_path=p['path'],source_url=p['source'],source_sha256=inventory[ident]['sha256'],
        previous_assignment={k:p.get(k) for k in ['level','area','xy','target','quality','radius_m','angle_uncertainty_deg','stair_system','evidence']},
        overrides=changes,current_level=level,current_quality=quality,
        level_status='unresolved' if level in ['belirsiz','ara'] else 'visual_inference_not_surveyed',
        camera_pose_verified=False,metric_geometry_approved=False,
        model_use='Visible form, material appearance and explicitly identified spatial relationships only; no inferred metric dimensions or camera constraints.',
        unresolved='Camera XYZ, yaw/pitch/roll, lens/distortion and construction dimensions remain unsolved.'))
assert len(rows)==105 and {r['id'] for r in rows}==set(byid)
assert all(r['observed_features'] and r['decision'] and r['crosscheck_ids'] for r in rows)
(O/'fotograf_denetimi.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
counts=Counter(r['current_quality'] for r in rows)
summary=f'''# Mudam — 105 fotoğrafın tek tek görsel denetimi

Denetim: 8 Ekim 2026. **105/105 fotoğraf ayrı ayrı incelendi. Metrik olarak doğrulanmış kamera pozu: 0.**

Görsel denetim tamamlandı; bu sonuç bütün mekânların, ölçülerin veya kamera açılarının kesinleştiği anlamına gelmez. Mevcut fotoğraf ve şemalarla desteklenmeyen atamalar kaldırıldı veya aday bölgeye indirildi. Orijinal kaynaklar değiştirilmedi. Önceki kayıtlar `denetim_oncesi_atlas.json` içinde korundu.

- Konum ve yön hipotezi: {counts['estimate']}; yalnız aday bölge: {counts['region']}; harita noktası kaldırılmış/çözülememiş: {counts['unresolved']}.
- {len(overrides)} kayıtta kat, yer, yön, sistem veya açıklama revizyonu; 105 kaydın tamamında ayrı gözlem ve karar.
- İnceleme: 18 karşılaştırma paftasında her fotoğraf; kritik belirsizliklerde büyütülmüş özgün görüntü. Fotoğraf sırası tek başına mekân kanıtı sayılmadı. Aynı arşivden iki fotoğraf bağımsız ölçüm kaynağı değildir.

## Modeli etkileyen düzeltmeler

1. **055:** 0→+1 merdiveni değil; alt fuayeden 0→−1 iniş boşluğunun altına bakış. 049–055 ve 115 aynı aşağı iniş sistemiyle ilişkilidir; çekim kotları aynı değildir.
2. **043:** Doğu spiral merdiveninin üst sahanlığı; önceki zemin kat ataması yanlış. +1 adayı güçlüdür; üst kat galeri içinin kapsamlı fotoğrafı değildir.
3. **042, 044, 050, 054:** Merdiven üzerinde/kenarında çekim; ara seviye olarak ayrıldı. Bir katın bitmiş döşeme kotuna otomatik oturtulamaz.
4. **066 / 067 / 097:** 066 basamaklı cam hacimdir, 067 düz pavyon bağlantısıdır. 067'nin bakışı pavyona doğrudur. 097 kırıklı cam merdivenin dış görünüşüdür. 066–097 batı merdiveni eşleşmesi adaydır; kamera ve uç kotları çözülmedi.
5. **032–033:** Grand Hall/heykel bahçesi geçiş yönleri yeniden ele alındı; güvenilmez yönler kaldırıldı.
6. **017, 019, 020, 056–064, 069–070:** Yakın detay veya seri sırasına dayanan oda/kat/merdiven atamaları sınırlandırıldı. 079 teknik ızgaradır; radyatör olduğu kanıtlı değildir.
7. **001, 090–091, 094, 109:** Cephe açıklamaları ve yer atamaları düzeltildi veya çözümsüz bırakıldı.
8. **108, 116, 124:** Uzak/yüksek/panoramik çekimlere atanmış doğrulanmamış zemin noktaları kaldırıldı. 108'in havadan çekim olduğu da kanıtlı değildir.

## Modelde kullanım kuralı

Fotoğraf kimliği, görünen eleman kimliği, kamera konumu ve eleman ölçüsü ayrı bilgilerdir. Gözlenen korkuluk, taş derzi, cam düğümü ve mekân ilişkisi kullanılabilir; kesin çap, duvar kalınlığı, basamak yüksekliği veya Z kotu sayı olarak kopyalanamaz. Geçici eserler ve sergi panoları kalıcı bina geometrisine eklenmez.

Tüm kayıtlarda `camera_pose_verified=false` ve `metric_geometry_approved=false`. Haritadaki daireler hâlâ aday alanlardır; yarıçap/±açı sayıları kalibre edilmiş hata payı değildir. Sadece modelle uyuyor diye kamera ve bina birbirini doğrulamış sayılmaz. Önce plan/kesit bağlantısı, sonra ortak sabit noktalarla çoklu fotoğraf uyumu ve tutarlı kamera çözümü gerekir.

Üç resmî kat şeması mekân ilişkisi için karşılaştırıldı. **101 kesiti**, ortadaki renkli küçük pavyon/kurgu ve teknik alt hacimleri içeriyor; uygulama aşaması/tarihi doğrulanmadan bugünkü yüksekliklerin ölçü kaynağı yapılamaz. Üst kat içleri, kafe içi, pavyon içi, galeri kanatları ve teknik hacimler eksik belgelenmiş durumdadır.

## Fotoğraf bazında kayıtlar

Her kayıttaki çapraz referanslar görsel karşılaştırma içindir; ölçü doğrulaması değildir.
'''
md=[summary]
cards=[]
for row in rows:
    p=byid[row['id']]; ident=row['id']; current=copy.deepcopy(p);current.update(row['overrides'])
    md.append(f"### {ident} — {current['area']}\n\n[Özgün fotoğraf](../../{p['path']}) · [Kaynak]({p['source']})\n\nGözlem: {row['observed_features']}\n\nKarar: {row['decision']}\n\nKarşılaştırma: {', '.join(row['crosscheck_ids'])}. Kat/alan: {row['current_level']}; harita durumu: {row['current_quality']}. Kamera ve metrik ölçüler doğrulanmadı.\n")
    cards.append(f'''<article id="foto-{ident}" data-search="{html.escape(ident+' '+current['area']+' '+row['observed_features'])}"><h2>{ident} · {html.escape(current['area'])}</h2><a href="../../{html.escape(p['path'])}" target="_blank"><img loading="lazy" src="../../{html.escape(p['path'])}" alt="Fotoğraf {ident}"></a><p><b>Gözlem:</b> {html.escape(row['observed_features'])}</p><p><b>Karar:</b> {html.escape(row['decision'])}</p><p>Karşılaştırma: {html.escape(', '.join(row['crosscheck_ids']))} · Kat/alan: {row['current_level']}</p><p class="note">Kamera pozu ve metrik ölçüler doğrulanmadı.</p><a href="{html.escape(p['source'])}" target="_blank">Kaynak</a></article>''')
(O/'FOTOGRAF_DENETIMI.md').write_text('\n'.join(md),encoding='utf-8')
page='''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mudam / 105 fotoğraf denetimi</title><style>body{margin:0;font:16px/1.55 system-ui;background:#edf0eb;color:#20353b}header{padding:24px;background:white;position:sticky;top:0;z-index:2;border-bottom:1px solid #ccd7d2}h1{font-size:24px;margin:0}header p{margin:8px 0}a{color:#087b93}input{font:inherit;padding:8px;width:min(480px,90%)}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px;padding:24px}article{background:white;padding:20px;border:1px solid #ccd7d2;border-radius:8px}h2{font-size:19px;margin:0 0 12px}img{width:100%;height:440px;object-fit:contain;background:#f4f4f0}.note{color:#975b18}article[hidden]{display:none}</style><header><h1>MUDAM / Tek tek fotoğraf denetimi</h1><p>105 fotoğraf incelendi · 0 doğrulanmış kamera pozu · Görsel gözlem ile ölçü onayı ayrıldı.</p><p><a href="../FOTOGRAF_ATLASI.html">Plan atlası</a> · <a href="FOTOGRAF_DENETIMI.md">Tam rapor</a> · <a href="fotograf_denetimi.json">Denetim verisi</a></p><input id="find" placeholder="Fotoğraf numarası veya görünen eleman" aria-label="Fotoğraflarda ara"><span id="count"> 105 / 105</span></header><main>'''+''.join(cards)+'''</main><script>document.querySelector('#find').oninput=e=>{let n=0;const q=e.target.value.toLocaleLowerCase('tr');document.querySelectorAll('article').forEach(a=>{a.hidden=!a.dataset.search.toLocaleLowerCase('tr').includes(q);if(!a.hidden)n++});document.querySelector('#count').textContent=' '+n+' / 105'};</script></html>'''
(O/'DENETIM.html').write_text(page,encoding='utf-8')
print('Reviewed',len(rows),'explicit changes',len(overrides),'map states',dict(counts))
