from pathlib import Path
import json,re
B=Path(__file__).resolve().parent
C=json.loads((B.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kalibrasyon.json').read_text(encoding='utf-8'))
tasks=[
('P00','Ortam ve kaynak manifesti',[], 'Blender sürümü, donanım, kaynak kimliği ve tarih listesi','Kaynakların tamamı dosyaya çözülür; orijinaller korunur'),
('P01','Üst kat referans araştırması',['P00'],'+1 fotoğraf ve ışıklık kanıt listesi','Katı doğrulanmış görüntüler veya açık eksik listesi'),
('P02','Kesit tarihi ve izi',['P00'],'101 kesitinin plan izi ve mevcut bina uyum raporu','Ortak köşeler eşleşir; belirsiz/eski öğeler ayrılır'),
('P03','Yatay referans aktarımı',['P00'],'Üç kat, OSM ve kontrol köşeleri','İki nokta ve yön testi; atlas Y işareti doğru'),
('P04','Düşey ölçü çözümü',['P02','P03'],'Kot tablosu, aralıklar, kesitler','Kat ve merdiven zinciri tutarlı; bilinmeyenler görünür'),
('P05','Tüm bina sade geometrisi',['P04'],'Kabuk, çatı, pavyon ve ana boşluklar','Plan, kesit, silüet birlikte tutarlı'),
('P06','Kamera eşleştirme pilotu',['P05'],'İç/dış kameralar ve artık raporu','Panoramalar ayrılmış; kontrol görüntüleri çözüme katılmamış'),
('P07','Beton duvar ve döşemeler',['P05','P06'],'Katlara bağlı yapı gövdeleri','Açıklık ve boşluklar sürekli; taşıyıcı ile kaplama ayrı'),
('P08','Kapı pencere ve mekân listesi',['P05'],'Eleman kimlikleri, aileleri ve oda bağlantıları','Bütün plan açıklıkları sayılmış; ölçü güveni ayrı'),
('P09','Merdiven ve sahanlıklar',['P07'],'Ana, alt ve doğu spiral aileleri','Rıht toplamı kot farkını kapatır; alt yüzey referansla tutarlı'),
('P10','Ana cam örtü',['P07'],'Çatı yüzeyi, ana/ikincil sistem ve paneller','Silüet, bölüntü ve oturmalar çoklu görünüşte tutarlı'),
('P11','Yan salon ve pavyon örtüleri',['P10'],'Doğu, batı, pavyon, bağlantı alt sistemleri','Aynalama varsayımı yok; kenar panelleri çözülmüş'),
('P12','Üç örnek detay bölgesi',['P08','P09','P10'],'Giriş kapısı, ana korkuluk, galeri penceresi','Yakın görünüş ve kesit; parametre değişiminde bağlantılar korunur'),
('P13','Taş yüzeyler ve derzler',['P12'],'Dış/iç taş, söve, portal ve döşeme','Köşe dönüşü, fiziksel modül ve kesim sırası tutarlı'),
('P14','Bütün kapı ve pencereler',['P12'],'Tip kütüphanesi ve örnekler','Kapı boşluğu/kanadı ayrılmış; eşik, kasa ve söve tamam'),
('P15','Korkuluk ve metal birleşimler',['P12'],'Cam panel, küpeşte, görünen bağlantılar','Eğri ve kot merdivene bağlı; varsayılan tutucular etiketli'),
('P16','Zemin ve alt kat iç bitişleri',['P13','P14','P15'],'Galeri, fuaye, oditoryum ve servis görünür detayları','Tavan, döşeme, kapı ve sabit donanım kontrol edilmiş'),
('P17','Üst kat iç bitişleri',['P01','P13','P14','P15'],'Üst galeriler, dolaşım ve ışıklıklar','Kanıtlı ayrıntılar ile temsilî bölgeler açıkça ayrılmış'),
('P18','Arazi tarihî duvar ve peyzaj',['P03','P05'],'Yakın çevre ve bina oturuşu','Arazi kotunun güven düzeyi belli; bağlantılar havada değil'),
('P19','Malzeme ve ışık',['P11','P16','P17','P18'],'Malzeme kütüphanesi ve nötr/gündüz/gece kontrolleri','Doku ölçeği tutarlı; cam ve yansıma farklı açılarda testli'),
('P20','Kat ayırma ve kesit',['P16','P17','P19'],'Görünürlük grupları ve kesit durumları','Tüm kat ve kesit testleri; kapı boşlukları kapanmıyor'),
('P21','Hafif türev ve dışa aktarma',['P20'],'Ana model ve hedef ortam türevi','Birim/eksen/malzeme geri yüklemede doğru; performans ölçülmüş'),
('P22','Teslim doğrulaması',['P21'],'Sürümlü dosyalar, kontrol görüntüleri ve açık sorun raporu','Temiz oturumda açılır; kapsam ve belirsizlikler denetlenmiş')]
obj={'schema_version':1,'date':'2026-10-08','state':'planning_only','policy':'Bağımlılık tamamlanması teknik kontrolü ifade eder, ayrıca kullanıcı izni gerektirmez. Kaynak eksikliği etkilenen sistemde temsilî teslim olarak açıkça kaydedilebilir; tam doğrulama sayılmaz.','tasks':[{'id':i,'title':t,'depends_on':dep,'deliverable':out,'acceptance':accept,'status':'not_started','open_issues':[]} for i,t,dep,out,accept in tasks]}
(B/'is_paketleri.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
params=[]
def p(i,title,value,status,sources,dep,unit='m'):
    params.append(dict(id=i,property=title,value=value,draft_value=None,unit=unit,min=None,max=None,status=status,source_ids=sources,dependencies=dep,method=None,recheck_trigger='Yeni ölçülü kaynak veya çoklu görünüş uyuşmazlığı',notes=''))
p('UNIT_SCALE','Blender birimi başına metre',1,'project_convention',[],[])
p('ORIGIN_E','Yerel orijin doğu UTM',293425,'project_convention',['kalibrasyon.json'],['all_xy'])
p('ORIGIN_N','Yerel orijin kuzey UTM',5499960,'project_convention',['kalibrasyon.json'],['all_xy'])
p('Z_L00_FINISH','Zemin bitmiş döşeme göreli kotu',0,'project_convention',[],['all_z'])
p('PLAN_M_PER_PX','1108 piksel ortak plan ölçeği',0.11879670016202512,'map_fit_estimate',['kalibrasyon.json'],['all_xy'],'m/px')
unknown=[
('Z_LP1_FINISH','Üst kat bitmiş kotu',['102','103','101'],['walls','stairs','openings']),
('Z_LM1_FINISH','Alt kat bitmiş kotu',['104','101','051'],['walls','stairs','openings']),
('Z_TECH_FINISH','Teknik alt hacim kotu',['101'],['technical_proxy']),
('SLAB_L00','Zemin beton döşeme kalınlığı',['101'],['slab_edges','stair_landings']),
('SLAB_LP1','Üst beton döşeme kalınlığı',['101'],['slab_edges','stair_landings']),
('SLAB_LM1','Alt beton döşeme kalınlığı',['101'],['slab_edges']),
('Z_ROOF_MAIN_BASE','Ana cam örtü oturma kotu',['101','026','087'],['roof_main']),
('Z_ROOF_MAIN_APEX','Ana cam örtü tepe kotu',['101','087','119'],['roof_main']),
('Z_ROOF_EAST_BASE','Doğu örtü oturma kotu',['034','041'],['roof_east']),
('Z_ROOF_WEST_BASE','Batı örtü oturma kotu',['093'],['roof_west']),
('Z_PAV_FINISH','Pavyon bitmiş döşeme kotu',['066','067','101'],['pavilion','link']),
('Z_PAV_APEX','Pavyon tepe kotu',['089','101'],['roof_pavilion']),
('WALL_CONCRETE_EXT','Dış beton duvar ailesi kalınlığı',['101'],['walls','openings']),
('WALL_CONCRETE_INT','İç beton duvar ailesi kalınlığı',['101'],['walls','openings']),
('STONE_THICKNESS','Taş kaplama ailesi kalınlığı',['005','063'],['stone','reveals']),
('STONE_COURSE','Taş sıra modülü',['001','003','017'],['stone_pattern']),
('STONE_JOINT','Taş derz genişliği',['005','019'],['stone_pattern']),
('DOOR_ENT_WIDTH','Giriş kapı ailesi açıklık eni',['013','014'],['entrance']),
('DOOR_ENT_HEIGHT','Giriş kapı ailesi açıklık yüksekliği',['013','014'],['entrance']),
('WINDOW_GAL_DEPTH','Galeri pencere nişi derinliği',['061','062','063'],['windows']),
('STEEL_MAIN_WIDTH','Ana çatı profil dış eni',['035','036','090'],['roof_main']),
('STEEL_SECONDARY_WIDTH','İkincil çatı profil dış eni',['037','038'],['roof_panels']),
('GLASS_THICKNESS','Görünür camın gerçek kalınlığı',['039','040'],['glazing']),
('RAIL_HEIGHT','Korkuluk ailesi yüksekliği',['023','046','050'],['railings']),
('HANDRAIL_DIAMETER','Küpeşte ailesi kesit boyutu',['024','043','044'],['railings']),
('STAIR_MAIN_RISE','Ana merdiven rıhtı',['021','022'],['stairs']),
('STAIR_MAIN_GOING','Ana merdiven basamak derinliği',['021','022'],['stairs']),
('STAIR_SPIRAL_RADIUS','Doğu spiral dış yarıçapı',['041','042','102'],['stairs_east']),
('LINK_FLOOR_SLOPE','Cam geçit kot farkı',['066','067'],['link']),
('TERRAIN_MOAT_BOTTOM','Hendek taban göreli kotu',['002','088','124'],['terrain'])]
for i,title,sources,dep in unknown:p(i,title,None,'unresolved',sources,dep)
(B/'parametreler.json').write_text(json.dumps({'schema_version':1,'units':'metres unless specified','crs':'EPSG:32632','atlas_to_blender':'X=x_m; Y=-y_m; Z=relative_finish_level','note':'Aile parametreleri başlangıç şablonudur; her farklı tip ve örnek ayrıca kayıt alır. Null bilinmeyendir. Genel yapım standardı gerçek bina ölçüsü yerine kullanılmaz.','calibration_reference':'../10_Olcekli_Plan_ve_Fotograf_Analizi/kalibrasyon.json','parameters':params},ensure_ascii=False,indent=2),encoding='utf-8')
# Check dependency graph and local document links.
ids={t[0] for t in tasks};seen=set()
for i,t,dep,out,accept in tasks:
    assert set(dep)<=seen,(i,dep)
    seen.add(i)
assert len(ids)==len(tasks)
for md in B.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
        if not target.startswith('http'):assert (md.parent/target).exists(),(md,target)
assert len({p['id'] for p in params})==len(params)
print(f'{len(tasks)} iş paketi; {len(params)} parametre; yerel bağlantılar ve bağımlılıklar doğrulandı.')
