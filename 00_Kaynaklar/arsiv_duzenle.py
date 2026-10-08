from pathlib import Path
import json,csv,hashlib,html,re
from collections import Counter
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
a=json.loads((ROOT/'00_Kaynaklar/envanter.json').read_text(encoding='utf-8'))
groups={}
def assign(ids,cat,title,tags=''):
    for i in ids:groups[f'{i:03}']=(cat,title,tags)
assign(range(1,7),'05_Dis_Mekan/Cepheler','Tas_cephe_ve_cam_pavyon','cephe; pavyon; taş; tarihi duvar')
assign([7],'07_Yapi_Detaylari/Tas_ve_Beton','Tas_kaplama_kose_detayi','taş; derz; köşe')
assign(range(8,14),'05_Dis_Mekan/Giris_ve_Yaklasim','Giris_koprusu_ve_sacak','giriş; köprü; saçak; meydan')
assign([14],'04_Ic_Mekan/Giris_ve_Dolasim','Giris_cam_kapisi','giriş; dolaşım')
assign([15,16],'07_Yapi_Detaylari/Aydinlatma','Giris_tavan_ve_aydinlatma','tavan; aydınlatma')
assign([17,19],'04_Ic_Mekan/Giris_ve_Dolasim','Tas_duvar_ve_dogal_isik','duvar; ışık; dolaşım')
assign([18,20],'07_Yapi_Detaylari/Yonlendirme','Bilgi_ve_yonlendirme_panosu','yönlendirme; pano')
assign([21,22,23,32,41,42,50,51,52,53,54,55],'04_Ic_Mekan/Merdivenler_ve_Dolasim','Merdiven_ve_katlar_arasi_dolasim','merdiven; beton; dolaşım')
assign([24,43,44,46,47,48,49],'07_Yapi_Detaylari/Korkuluk_ve_Kupeste','Cam_korkuluk_ve_metal_kupeste','cam; korkuluk; küpeşte; birleşim')
assign([25,26,27,31,45],'04_Ic_Mekan/Grand_Hall','Grand_Hall_genel_gorunum','Grand Hall; ışık; hacim; cam çatı')
assign([28,29,30,35,36,37,38,39,40,68],'07_Yapi_Detaylari/Cam_Cati_ve_Struktur','Cam_cati_celik_tasiyici_ve_birlesim','cam çatı; çelik; strüktür; birleşim')
assign([33,34],'04_Ic_Mekan/Cam_Ortulu_Salonlar','Cam_ortulu_sergi_salonu','sergi; cam örtü; doğal ışık')
assign([56,57,58,61,62],'04_Ic_Mekan/Galeriler','Galeri_sergi_ve_pencere','galeri; sergi; ahşap döşeme; pencere')
assign([59,60,69,70,79],'07_Yapi_Detaylari/Tas_ve_Beton','Duvar_tavan_kapi_ve_malzeme_detayi','taş; tavan; kapı; malzeme')
assign([63,65],'03_Vaziyet_ve_Peyzaj/Tarihi_Duvarlar_ve_Cevre','Tarihi_duvarlar_park_ve_yaklasim','Fort Thüngen; tarihi duvar; peyzaj; çevre')
assign([64],'07_Yapi_Detaylari/Cam_Cati_ve_Struktur','Cam_cephe_dograma_detayi','cam; doğrama; cephe')
assign([66,67],'04_Ic_Mekan/Cam_Gecit','Cam_gecit_ve_pavyon_baglantisi','cam geçit; köprü; pavyon')
assign([71,72,73,76],'04_Ic_Mekan/Oditoryum','Oditoryum_ve_ahsap_duvarlar','oditoryum; ahşap; akustik')
assign([74,75],'07_Yapi_Detaylari/Tavan_ve_Akustik','Oditoryum_kaset_tavan','tavan; akustik; kaset')
assign([77,78],'04_Ic_Mekan/Asansor_ve_Servis','Asansor_ve_erisim','asansör; erişim')
assign([80],'07_Yapi_Detaylari/Yonlendirme','Tuvalet_yonlendirmesi','yönlendirme; tabela')
assign([81],'04_Ic_Mekan/Asansor_ve_Servis','Tuvalet_lavabo_ve_servis','tuvalet; lavabo; servis')
assign([82,96],'03_Vaziyet_ve_Peyzaj/Vaziyet_Planlari','Vaziyet_plani_ve_arazi_profili','vaziyet; peyzaj; arazi profili')
assign([83],'01_Kat_Planlari/Mimari_Pafta','Uc_kat_planinin_mimari_paftasi','kat planı; mimari çizim; üç kat')
assign([84,101],'02_Kesitler','Mimari_kesit','kesit; kat ilişkisi; cam çatı')
assign([85],'06_Perspektif_ve_Cizimler','Dis_perspektif_mimari_cizimi','perspektif; mimari çizim')
assign([86,88],'05_Dis_Mekan/Tarihi_Duvarlarla_Iliski','Muze_ve_tarihi_sur_duvarlari','cephe; tarihi duvar; Fort Thüngen')
assign([87],'05_Dis_Mekan/Giris_ve_Yaklasim','Yaklasim_koprusu_ve_cam_cati','köprü; yaklaşım; cam çatı')
assign([89,90,91,92,93,94,95,97,98,99,100],'05_Dis_Mekan/Cepheler','Tas_cephe_ve_cam_cati','cephe; cam çatı; taş; pavyon')
assign([102,103,104],'01_Kat_Planlari/Resmi_Kat_Semalari','Resmi_kat_semasi','kat planı; ziyaretçi şeması; ölçüsüz')
assign([108],'03_Vaziyet_ve_Peyzaj/Tarihi_Duvarlar_ve_Cevre','Kent_park_ve_muze_panorama','peyzaj; kent; panorama; Fort Thüngen')
assign([109],'05_Dis_Mekan/Cepheler','Muze_ve_agaclar','cephe; ağaç; cam çatı')
assign([110,114],'04_Ic_Mekan/Grand_Hall','Grand_Hall_isik_ve_cam_cati','Grand Hall; ışık; cam çatı')
assign([115],'04_Ic_Mekan/Merdivenler_ve_Dolasim','Merdiven_ve_dogal_isik','merdiven; ışık')
assign([116],'05_Dis_Mekan/Havadan_Gorunum','Muze_havadan_genel_gorunum','havadan; kütle; yaklaşım; yerleşim')
assign([119],'05_Dis_Mekan/Cepheler','Cam_cati_cepheden_gorunum','cam çatı; cephe; siluet')
assign([122,123,124],'03_Vaziyet_ve_Peyzaj/Park_Drai_Eechelen','Park_peyzaj_yol_ve_bitkilendirme','peyzaj; park; yol; bitkilendirme; MDP')
for x in a:
    if x['status']!='ok':continue
    if x['id'] in groups:
        cat,title,tags=groups[x['id']];x.update(category=cat,description=title.replace('_',' '),tags=tags)
        if x['id'] in ['102','103','104']:title+={'102':'_zemin_0','103':'_ust_arti_1','104':'_alt_eksi_1'}[x['id']]
        source='WikiArquitectura' if 'wikiarquitectura' in x['source'] else 'ArchEyes' if 'archeyes' in x['source'] else 'MDP_GreatGardens' if 'greatgardens' in x['source'] else 'Mudam'
        src=(ROOT/x['path']).resolve();dest=(ROOT/cat/(x['id']+'_'+title+'_'+source+src.suffix)).resolve()
        if not src.is_relative_to(ROOT) or not dest.is_relative_to(ROOT):raise ValueError('workspace outside target')
        dest.parent.mkdir(parents=True,exist_ok=True)
        if src!=dest:
            if dest.exists():raise ValueError('destination exists '+str(dest))
            src.rename(dest)
        x['path']=dest.relative_to(ROOT).as_posix()
    else:x.update(description='Yardımcı resmî belge / rehber',tags='PDF; belge; rehber')
    if x['id'] in ['108','109','110','116']:x['credit']='© Christian Aschman / Mudam Luxembourg (resmî sayfa atfı)'
    if x['id']=='115':x['credit']='© Kiyohiko Higashide / Mudam Luxembourg'
    if x['id']=='119':x['credit']='© Rémi Villaggi / Mudam Luxembourg'
    x.pop('error',None)

ok=[x for x in a if x['status']=='ok']
for x in ok:
    dest=ROOT/x['path'];assert dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest()==x['sha256']
    if dest.suffix.lower()!='.pdf':
        with Image.open(dest) as im:im.verify()
(ROOT/'00_Kaynaklar/envanter.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
fields=['id','path','description','category','tags','width','height','bytes','credit','source','url','sha256','status','error','name']
with (ROOT/'00_Kaynaklar/dosya_envanteri.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(a)
counts=Counter(x['category'].split('/')[0] for x in ok)
info='MUDAM MİMARİ ARAŞTIRMA ARŞİVİ\nHazırlanma tarihi: 8 Ekim 2026\n\n'+f'Toplam: {len(ok)} kaynak dosyası; {sum("width" in x for x in ok)} görsel, {sum(x["path"].endswith(".pdf") for x in ok)} PDF.\nBoyut: {sum(x["bytes"] for x in ok)/1048576:.1f} MiB.\n\n'
info+='KLASÖRLER\n'+'\n'.join(f'{k}: {v} dosya' for k,v in sorted(counts.items()))
info+='\n\nKULLANIM\nKATALOG.html: tüm görsellerin çevrimdışı küçük resim kataloğu; görsele tıklayarak kaynak dosyasını açabilirsiniz.\n00_Kaynaklar/dosya_envanteri.csv: her dosyanın kaynak sayfası, doğrudan bağlantısı, kredi, çözünürlük, etiket ve SHA-256 bilgisi.\n00_Kaynaklar/envanter.json: aynı bilgiler ve erişilemeyen kaynakların kayıtları.\n09_Onizlemeler: kategori bazında görsel kontrol paftaları.\niletisim.md: kullanıcının sağladığı kişiler, e-postalar ve demo temas planı.\n\nÇİZİMLER\nResmî 0, +1 ve -1 kat şemaları ayrı dosyalardadır; ölçülendirme içermez.\nWikiArquitectura mimari kat paftası: 380 x 582 piksel; üç plan birlikte yayımlanmıştır. Ölçek ve ölçüler bu kopyadan güvenilir biçimde türetilemez.\nWikiArquitectura kesiti: 380 x 220 piksel. ArchEyes kesiti: 1250 x 852 piksel; daha ayrıntılı inceleme için tercih edilebilir.\nWikiArquitectura vaziyet paftası: 650 x 457 piksel. ArchEyes vaziyet/arazi profili: 1200 x 810 piksel.\nDosyalar kaynak çözünürlüğünde tutuldu; yapay olarak büyütülmedi. Fotoğraflara göre yapılan sınıflandırmalar görsel yorumdur; belirsiz salonlara kesin mekân adı verilmedi.\n2016 Wim Delvoye PDF’si sergiye ait tarihsel kat şemaları içerir; güncel mimari proje seti değildir.\n\nKAYNAKLAR\nhttps://es.wikiarquitectura.com/edificio/museo-de-arte-moderno-grand-duc-jean-mudam/\nhttps://archeyes.com/the-mudam-by-i-m-pei-where-old-meets-new/\nhttps://www.mudam.com/visit/architecture\nhttps://www.mudam.com/resources/press\nhttps://www.greatgardensoftheworld.com/gardens/michel-desvigne/\nhttps://micheldesvignepaysagiste.com/fr/node/786\nhttps://fondskirchberg.public.lu\n\nERİŞİM NOTLARI\nKullanıcı tarafından verilen eski /fr/floor-plans sayfası 404 döndü; üç kat şemasının doğrudan CDN bağlantıları üzerinden dosyalar indirildi. 0 ve +1 için /_default_4/ yerine /images/ kullanıldı.\nMDP proje sayfasının indirilmesi 403 döndü. Park fotoğrafları Great Gardens üzerindeki Draï Eechelen bölümünden, © MDP kredisiyle alındı.\nResmî mimarlık sayfasındaki bazı ek fotoğraflar bağlantı kesilmesi nedeniyle indirilemedi; eksik kayıtlar envanterde error olarak işaretlidir.\nBu taramada ölçülü PDF uygulama paftası, DWG veya tam proje seti elde edilmedi. Arşiv erişilebilen kaynaklarla sınırlıdır.\n\nGÖRSEL KREDİLERİ\nWikiArquitectura fotoğraf serisi: WikiArquitectura, Haziran 2019 (kaynak sayfa atfı).\nArchEyes fotoğrafları: © Michael Nguyen; çizimler: © I. M. Pei (kaynak atfı).\nResmî fotoğraflar: Mudam Luxembourg; Christian Aschman, Kiyohiko Higashide, Rémi Villaggi.\nPark fotoğrafları: © MDP / Great Gardens of the World.\nİndirme, görseller için yeniden yayımlama veya ticari kullanım izni sağlamaz; kaynak/kredi bilgileri dosya bazında kaydedildi.\n'
(ROOT/'00_Kaynaklar/arsiv_bilgisi.txt').write_text(info,encoding='utf-8')
pre=ROOT/'09_Onizlemeler';pre.mkdir(exist_ok=True)
sections=[]
for category in sorted(counts):
    batch=[x for x in ok if x['category'].split('/')[0]==category]
    cards=[]
    for x in batch:
        e=html.escape;path=e(x['path'],quote=True)
        if 'width' in x:
            cards.append(f'<figure><a href="{path}"><img loading="lazy" src="{path}" alt="{e(x["description"])}"></a><figcaption><b>{x["id"]} · {e(x["description"])}</b><small>{e(x["category"])} · {x["width"]} × {x["height"]}</small><small>{e(x["credit"])}</small><a href="{e(x["source"],quote=True)}">Kaynak</a></figcaption></figure>')
        else:cards.append(f'<figure><a href="{path}">{e(x["name"])}</a><p>PDF belge</p></figure>')
    sections.append(f'<section id="{category}"><h2>{category.replace("_"," ")} — {len(batch)} dosya</h2><div class="grid">'+''.join(cards)+'</div></section>')
    imgs=[x for x in batch if 'width' in x]
    for start in range(0,len(imgs),20):
        part=imgs[start:start+20];sheet=Image.new('RGB',(1440,((len(part)+3)//4)*260),'#eee');d=ImageDraw.Draw(sheet)
        for j,x in enumerate(part):
            with Image.open(ROOT/x['path']) as im:thumb=ImageOps.contain(im.convert('RGB'),(350,230))
            xx=j%4*360;yy=j//4*260;sheet.paste(thumb,(xx+(350-thumb.width)//2,yy));d.text((xx+5,yy+233),x['id']+' '+x['description'][:35],fill='black')
        sheet.save(pre/f'{category}_{start//20+1:02}.jpg')
nav=' '.join(f'<a href="#{c}">{c.replace("_"," ")}</a>' for c in sorted(counts))
page=f'<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mudam mimari görsel arşivi</title><style>body{{font:16px system-ui;margin:28px;background:#f5f4f0;color:#222}}h1{{font-size:32px}}nav{{display:flex;flex-wrap:wrap;gap:18px;padding:20px 0}}a{{color:#245a74}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:18px}}figure{{margin:0;background:white;padding:14px;border:1px solid #ddd}}img{{width:100%;height:240px;object-fit:contain}}small{{display:block;margin:8px 0;color:#555}}section{{margin-top:40px}}</style><h1>Mudam · Mimari araştırma arşivi</h1><p>8 Ekim 2026 · {len(ok)} dosya · Plan / kesit / iç mekân / dış mekân / peyzaj / yapı detayları</p><p>Görsele tıklayarak tam dosyayı açın. <a href="00_Kaynaklar/dosya_envanteri.csv">Kaynak ve çözünürlük envanteri</a> · <a href="00_Kaynaklar/arsiv_bilgisi.txt">Arşiv bilgisi</a> · <a href="iletisim.md">İletişim planı</a></p><nav>{nav}</nav>'+''.join(sections)+'</html>'
(ROOT/'KATALOG.html').write_text(page,encoding='utf-8')
print('Verified all source files and image decoding. Catalog complete. Files:',len(ok));print(dict(sorted(counts.items())))
