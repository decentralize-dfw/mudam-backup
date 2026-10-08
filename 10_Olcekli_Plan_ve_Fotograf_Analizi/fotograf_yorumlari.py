"""Manual visual hypotheses in official level-0 diagram pixels (1108 x 960).
Points are NOT surveyed camera coordinates. 'region' means candidate area only.
Angle uncertainty is a judgement range, not a calibrated confidence interval.
"""
D={}
def put(ids,level,xy,target,quality,area,radius,evidence,pitch='yaklaşık yatay',angle=25):
    for n in ids:
        D[f'{n:03}']=dict(level=level,xy=xy,target=target,quality=quality,area=area,radius_m=radius,evidence=evidence,pitch=pitch,angle_uncertainty_deg=angle if target else None)
# Exterior points are estimates from visible architectural correspondences.
put([1],'dis',(825,890),(570,675),'estimate','Giriş meydanı',12,'Giriş saçağı, taş kütle, çan biçimli cam üst yapı ve meydan mobilyaları aynı kadrajda.',angle=30)
put([2],'dis',(190,545),(115,280),'estimate','Doğu cephesi / pavyon',8,'Sekizgen pavyon solda; taş galerinin geri çekilmiş pencereleri sağda. Tarihi hendek ön planda.',angle=20)
put([3],'dis',(175,505),(295,365),'estimate','Doğu galeri cephesi',8,'Pavyon, galeri yan duvarı ve eğimli pencere boşlukları birlikte görülüyor.',angle=20)
put([4],'dis',(150,455),(291,415),'estimate','Doğu galeri cephesi',10,'Aynı pencere dizisi ve tarihi duvar; fotoğraf 003 ile mekânsal ilişki.',angle=25)
put([5],'dis',(238,575),(291,470),'estimate','Doğu cephe köşesi',12,'Taş kütlenin köşesi ve alt seviyedeki gömülü pencere. Görüş alanı sınırlı.',angle=35)
put([6],'dis',(720,770),(575,710),'estimate','Giriş saçağı',10,'Dikdörtgen giriş açıklığı, giriş köprüsü ve avluya bakan yan açıklık.',angle=25)
put([7],'dis',(720,770),None,'region','Giriş köprüsü parapeti',15,'Yalnızca taş parapet birleşimi; camera noktası ve azimut tekil olarak çözülemiyor.',pitch='aşağı / detay')
put([8],'dis',(655,855),(575,690),'estimate','Giriş köprüsü',7,'Köprü korkuluğu, taş portal ve cam giriş kapısı aynı perspektif ekseninde.',angle=20)
put([9],'dis',(578,900),(576,680),'estimate','Giriş aksı',9,'Önden giriş portali ve köprü simetrisi, yaklaşık merkez aksı destekliyor.',angle=15)
put([10],'dis',(860,880),(580,660),'estimate','Giriş meydanı yan yaklaşım',15,'Geniş meydan, taş ön cephe, giriş kenarı ve oturma elemanları.',angle=30)
put([11],'dis',(625,755),(800,895),'estimate','Saçak altından meydana bakış',8,'Saçak kolonunun gerisinden meydana ve yüksek yapılara dış bakış.',angle=30)
put([12],'dis',(645,742),(770,890),'estimate','Saçak altı',9,'Saçak kolonunun farklı açısı; dış peyzaj görünüşü. Yaklaşık eşleşme.',angle=35)
put([13],'dis',(596,718),(575,662),'estimate','Giriş kapısı önü',4,'Taş portal içindeki cam kapı ve giriş duvarı yakın görünüşü.',angle=20)
put([14],'0',(578,660),(579,736),'estimate','Giriş vestibülü',4,'İçeriden dışarı döner kapı, köprü ve meydan görünüşü.',angle=20)
put([15,16],'0',(575,640),None,'region','Giriş vestibülü tavanı',5,'Çokgen giriş tavanındaki radyal armatür; tam yukarı bakışta plan azimutu anlamlı değil.',pitch='yukarı')
put([17],'0',(465,568),(428,535),'estimate','Grand Hall ile galeri arasındaki eşik',9,'Taş duvar, yan mekân açıklığı ve çatıdan düşen gölgeler. Eşik eşleşmesi olası.',angle=40)
put([18],'belirsiz',None,None,'unresolved','İsim plakası / iç duvar',None,'Plaka ve taş kaplama tek başına hangi duvarda çekildiğini belirlemeye yetmiyor.')
put([19],'0',(509,480),None,'region','Ana merdiven yakınındaki taş yüzey',7,'Kavisli taş yüzey ve merdiven ilişkisi; yakın kadrajda kamera yönü çözülemiyor.',pitch='yukarı / detay')
put([20],'0',(575,590),None,'region','Yönlendirme panosu / giriş-ana hol çevresi',15,'Duvara işlenmiş kat şeması görülüyor; pano konumu için bağımsız referans yok.')
put([21],'0',(632,517),(468,443),'estimate','Grand Hall / ana merdiven',6,'Ana merdivenin geniş kolu, cam korkuluğu ve çatı ilişkisi belirgin.',angle=20)
put([22],'0',(605,482),(470,436),'estimate','Ana merdiven alt sahanlığı',5,'Geniş basamaklar, taş parapet ve cam korkuluk aynı yönde.',angle=20)
put([23],'0',(514,527),(462,486),'estimate','Ana merdiven boşluğu',5,'Silindirik cam korkuluk ve büyük merdivenin kıvrımı. Zemin katta üstten bakış.',pitch='aşağı',angle=30)
put([24],'0',(494,503),None,'region','Ana merdiven küpeştesi',6,'Metal küpeşte yakın planı; camera azimutu için yeterli sabit mekân göstergesi yok.',pitch='detay')
put([25],'0',(650,383),(480,449),'estimate','Grand Hall',8,'Ana merdiven, taş üst galeri duvarı ve piramidal çatı görülüyor; birleşik panorama.',pitch='yatay ve yukarı; panorama',angle=30)
put([26],'0',(603,351),(466,451),'estimate','Grand Hall',7,'Geniş merdiven ve alt boşluk, ana holün karşı tarafından görülüyor.',angle=25)
put([27],'0',(515,490),(594,329),'estimate','Grand Hall cam yüzeyi',8,'Ana holün yüksek cam yüzeyi, köşe çizgisi ve galeri duvarı.',pitch='yukarı',angle=30)
put([28,29],'0',(574,409),None,'region','Grand Hall çatı izdüşümü',11,'Piramidal çatı ve tepe açıklığı; tavana bakıştan tekil zemindeki nokta belirlenemiyor.',pitch='yukarı')
put([30],'0',(714,358),None,'region','Cam örtü / güneş kırıcı bölgesi',13,'Üçgen çatı kenarı ve yatay güneş kırıcılar; alternatif kanat ihtimali var.',pitch='yukarı / detay')
put([31],'0',(519,469),(633,337),'estimate','Grand Hall',8,'Taş duvar, cam çatı ve ana holün ışık düzeni.',pitch='yukarı',angle=30)
put([32],'0',(557,425),(697,353),'estimate','Grand Hall yan dolaşım',9,'Basamaklar ve üçgen yan açıklık; dar perspektif.',angle=40)
put([33],'0',(506,394),(347,299),'estimate','Heykel bahçesi / doğu cam salon',7,'Ağaç dallı enstalasyon, doğu cam yüzeyi ve taş duvar aynı kadrajda.',angle=25)
put([34],'0',(489,375),(344,273),'estimate','Heykel bahçesi / doğu cam salon',7,'Düz eğimli cam örtü ve uzun taş duvar; 033 ve 041 ile aynı salon.',angle=25)
put([35,36,37,38,39,40],'0',(365,294),None,'region','Doğu cam salon çatı sistemi',13,'Kablolar ve cam çatı birleşimleri, 034/041 salonuyla ilişkili. Tekrarlı modüller nedeniyle nokta/azimut tekil değil.',pitch='yukarı / detay')
put([41],'0',(416,367),(316,328),'estimate','Doğu cam salon spiral merdiveni',5,'Tek kollu spiral merdiven, silindirik çekirdek ve tam boy cam duvar ayırt edici.',angle=20)
put([42],'0',(356,362),(316,328),'estimate','Spiral merdiven altı',5,'Spiral basamak alt yüzeyi ve taş silindir, 041 ile örtüşüyor.',pitch='yukarı',angle=30)
put([43,44],'0',(330,340),None,'region','Doğu spiral merdiven küpeştesi',5,'Silindirik çekirdeğe bağlanan küpeşte; hangi yandaki basamakta çekildiği çözülemiyor.',pitch='detay')
put([45],'0',(565,454),(638,383),'estimate','Grand Hall / aşağı inen yarım daire merdiven',7,'Öndeki ana hol döşemesi ve eserin arkasındaki cam korkuluk, aşağı iniş boşluğunu gösteriyor. Yukarı çıkan geniş merdivenden farklı sistem; 046–050 ve kullanıcının plan düzeltmesiyle yeniden eşleştirildi.',pitch='hafif aşağı',angle=30)
put([46,47],'0',(618,387),None,'region','Aşağı inen merdiven / düz korkuluk birleşimi',5,'Alt kata yönelen basamak, düz korkuluk ve duvardaki Galeries Auditorium / Mudam Café yazısı 046 içinde okunuyor. 047 aynı köşe birleşiminin detayı. Haritadaki soldaki yarım daireye taşındı; kamera noktası kesin değil.',pitch='aşağı / detay')
put([48],'0',(630,391),None,'region','Aşağı inen merdiven / eğrisel korkuluk birleşimi',5,'Düz cam panelden eğrisel korkuluğa geçiş ve üstte güneş kırıcı cam üçgen görülüyor; 049 ile aynı aşağı iniş boşluğu. Yakın kadraj tekil kamera veya azimut çözmüyor.',pitch='aşağı / detay')
put([49],'0',(632,384),None,'region','Aşağı inen merdiven / üst sahanlık',5,'0 → −1 inişi: yatay döşeme kenarından aşağı kıvrılan iki küpeşte ve güneş kırıcı üçgen birlikte görülüyor. Kullanıcının işaretlediği haritadaki soldaki yarım daire. +1’e çıkan sağdaki merdiven değil; tam kamera noktası henüz çözülmedi.',pitch='aşağı')
put([50],'0',(636,391),(655,371),'estimate','Aşağı inen merdiven / alt döşemeye bakış',6,'0 → −1 inişi: aşağıdaki döşeme ve 051’de de görülen duvar görseli, 049 ile aynı yarım daire merdiveni doğruluyor. Kullanıcı düzeltmesi sonrası iniş boşluğuna taşındı. Konum ve yatay yön hâlâ görsel tahmin.',pitch='aşağı',angle=35)
put([51],'-1',(618,399),(649,374),'estimate','Alt kat / yarım daire merdivenin altından yukarı',7,'050’de aşağı bakılan merdivenin alt görünüşü: aynı duvar görseli, eğrisel kol ve döşeme boşluğu. 0’a çıkar; +1’e çıkan geniş merdivenden ayrı. Alt kattaki kamera yeri yaklaşık.',pitch='yukarı',angle=30)
put([52,53],'-1',(639,382),None,'region','Alt kat / yarım daire merdivenin alt yüzeyi',7,'051 ile aynı basamak altı ve düşey destek ilişkisi; aşağı iniş merdiveninin izdüşümüne taşındı. Alt kat içindeki tam kamera yeri çözülemedi.',pitch='yukarı / detay')
put([54],'-1',(650,367),(513,484),'estimate','İniş merdiveninden Grand Hall ve karşıdaki çıkışa bakış',9,'Önde alt kat boşluğu, karşıda 0 kat döşemesi ve arkasında yukarı çıkan geniş merdiven okunuyor. İki merdiveni ayıran çapraz kontrol görüntüsü. Kamera 0/−1 arasındaki merdiven üzerinde olabilir; kesin kot çözülmedi.',pitch='yukarı; ara basamak olası',angle=40)
put([55],'0',(552,478),(470,448),'estimate','Grand Hall / ana merdiven altı',7,'Ana merdivenin kıvrımı ile yüksek piramidal cam çatı birlikte.',pitch='yukarı',angle=30)
put([56],'0',(438,414),(303,444),'estimate','Doğu galerisi giriş eşiği',10,'Sergi giriş yazısı, ahşap döşeme ve hendek/yeşilliğe bakan gömülü pencere. Kanat eşleşmesi olası.',angle=35)
put([57],'0',(410,426),(322,477),'estimate','Doğu galerisi',12,'Ahşap döşeme, sergi panelleri ve gömülü pencere düzeni; 056 ile seri ilişkisi.',angle=40)
put([58],'0',(362,501),(410,430),'estimate','Doğu galerisi',14,'Aynı sergi ve galeri içi ters açı; geçici paneller kamera çözümünü sınırlar.',angle=45)
put([59],'belirsiz',None,None,'unresolved','Taş duvar birleşimi',None,'Yalnızca taş yüzey ve düşey boşluk; farklı katlarda benzer detaylar var.',pitch='detay')
put([60],'0',(388,472),None,'region','Galeri tavan kenarı',20,'Galeri tavan detayı; kesin galeri kanadı ve fotoğraf noktası doğrulanamıyor.',pitch='yukarı / detay')
put([61],'0',(351,434),(293,436),'estimate','Doğu galeri penceresi',9,'Gömülü pencere ve dış meydan/hendek ilişkisi; 056/062 ile ortak pencere ailesi.',angle=35)
put([62],'0',(369,442),(290,416),'estimate','Doğu galerisi / dışarı bakış',9,'İki derin pencere boşluğu ve dıştaki tarihi duvarların perspektifi.',angle=30)
put([63],'0',(299,419),(196,492),'estimate','Doğu cephede pencere nişi',7,'Pencere nişi içinden köprü, hendek ve uzak yapılar.',angle=35)
put([64],'0',(289,320),None,'region','Pavyona yakın cam doğrama',14,'Cam doğrama ve çimenli dış alan; benzer cephe modülleri nedeniyle tekil konum belirsiz.',pitch='detay')
put([65],'0',(242,278),(240,461),'estimate','Cam geçitten tarihi duvarlara bakış',9,'Galeri yan duvarı, arkeolojik duvar izi ve meydan yönündeki yüksek yapılar.',angle=30)
put([66],'0',(178,279),(286,279),'estimate','Pavyon cam geçidi',4,'Cam koridorun uzun ekseni ve kısa basamak dizisi; çekim yönü ana binaya doğru olası.',angle=20)
put([67],'0',(175,283),(299,283),'estimate','Pavyon cam geçidi',4,'Simetrik koridor ekseni, iki yandaki cam ve taş ana bina yüzeyi.',angle=15)
put([68],'0',(220,280),None,'region','Cam geçit çatı birleşimi',7,'Cam geçit çatısı ve gerideki cam üst yapı; yukarı yakın plan.',pitch='yukarı / detay')
put([69,70],'-1',(597,454),None,'region','Alt kat fuaye / oditoryum kapıları',18,'Ahşap çift kanat kapı ve taş duvar; 071-076 serisiyle ilişkili aday bölge, kesin kapı değil.')
put([71],'-1',(618,543),(567,461),'estimate','Oditoryum arka sıralar',6,'Oturma sıraları, sunum perdesi ve ahşap akustik duvarlar.',angle=25)
put([72],'-1',(610,505),None,'region','Oditoryum yan duvarı',8,'Delikli ahşap akustik kaplama; salon belirli, duvardaki tam nokta belirsiz.')
put([73],'-1',(546,542),(581,461),'estimate','Oditoryum arka sıralar',6,'Perde ve koltuk sıralarına çapraz bakış, 071’in karşı tarafı olası.',angle=25)
put([74,75],'-1',(580,511),None,'region','Oditoryum tavanı',9,'Kaset tavan modülleri; tekrarlanan geometri tekil kamera konumu vermiyor.',pitch='yukarı')
put([76],'-1',(599,513),None,'region','Oditoryum duvar detayı',9,'Ahşap kaplama, akustik panel ve sıra korkuluğu.')
put([77],'belirsiz',None,None,'unresolved','Asansör ön holü',None,'Asansör cephesi aynı düşey çekirdeğin birden fazla katında tekrarlanabilir; katı doğrulayacak işaret yok.')
put([78],'belirsiz',None,None,'unresolved','Asansör kabini',None,'Kabinin hangi katta durduğu ve fotoğraf doğrultusu dış referans olmadan belirlenemiyor.')
put([79],'belirsiz',None,None,'unresolved','Teknik duvar / radyatör',None,'Yakın taş duvar ve teknik eleman; kat veya oda için yeterli benzersiz gösterge yok.')
put([80,81],'belirsiz',None,None,'unresolved','Tuvalet / servis',None,'Tuvalet işareti ve lavabo; resmî şemada birden fazla olası servis konumu var.')
put([86],'dis',(600,-105),(566,330),'estimate','Fort Thüngen yakınında dış yaklaşım',20,'Fort duvarı önde, Mudam cam üst yapısı geride. Tarihi duvarlar kamera bölgesini sınırlar.',angle=25)
put([87],'dis',(575,10),(575,325),'estimate','Fort tarafındaki köprü / arka yaklaşım',9,'Köprü aksından merkezi cam piramide ve iki yan cam salona simetrik bakış. Ana giriş kapısı değil.',angle=15)
put([88],'dis',(175,558),(260,370),'estimate','Doğu cephe / hendek',12,'Pavyon solda, taş galeri sağda, tarihi hendek ve duvarlar önde.',angle=25)
put([89],'dis',(85,540),(110,281),'estimate','Pavyon dış görünüşü',16,'Sekizgen pavyon cam çan üstü ve taş kaide; yukarı tele kadraj.',pitch='yukarı',angle=30)
put([90],'dis',(668,177),(572,353),'estimate','Cam çatı güneybatı görünüşü',18,'Eğimli cam kanat ile merkez çan üstü; tam mesafe fotoğraftan ölçülemiyor.',pitch='yukarı',angle=30)
put([91],'dis',(803,852),(570,357),'estimate','Taş giriş cephesi üzerinden cam kule',22,'Önde taş cephe, üstte merkez cam kule; dar kadraj ve uzaklık belirsiz.',pitch='yukarı',angle=40)
put([92],'dis',(553,-50),(574,370),'estimate','Fort tarafında cam cephe',16,'Merkez piramit, yan cam çatı ve tarihi duvar ilişkisi.',pitch='yukarı',angle=20)
put([93],'dis',(846,134),(714,312),'estimate','Batı eğrisel cam salon dışı',17,'Eğrisel cam örtü ve merkez kule bağlantısı. Kavisli kanatla eşleşiyor.',pitch='yukarı',angle=30)
put([94],'dis',(1010,555),(834,460),'estimate','Batı taş galeri cephesi',20,'Kör taş yüzey, ince cam ek ve tarihi duvar. Alternatif yan açı mümkün.',angle=40)
put([95],'dis',(691,61),(615,352),'estimate','Fort yönünden üst yapı',20,'Merkez çan, eğimli cam ve ön parapet; uzaktan dar kadraj.',pitch='yukarı',angle=35)
put([97],'dis',(224,128),(350,300),'estimate','Doğu cam salon / galeri birleşimi',20,'Yatay cam geçiş ve taş galeri köşesi; eşleşme orta güvenli.',angle=40)
put([98],'dis',(590,63),None,'region','Cam çatı çevresindeki dış duvarlar',30,'Taş parapet ve cam kule yakın planı; alternatif dış kamera noktaları elenemedi.',pitch='yukarı')
put([99],'dis',(207,461),(225,281),'estimate','Pavyon cam geçidine dışarıdan bakış',15,'Cam bağlantı koridoru, taş duvar ve gerideki üst yapı.',pitch='hafif yukarı',angle=35)
put([100],'dis',(144,541),(289,427),'estimate','Doğu galeri uzun cephesi',15,'Gömülü üçgen pencere nişleri ve merkez kule, 003/088 ile aynı cephe.',pitch='hafif yukarı',angle=30)
put([108],'dis',(570,-1280),(575,330),'estimate','Park üzerinden uzak panorama',75,'Fort üç kuleleri önde, Mudam geride ve yüksek iş yapıları arka planda. Kesin seyir noktası çözülemedi.',angle=30)
put([109],'dis',(818,857),(560,380),'estimate','Ağaçlar arasından giriş cephesi',30,'Taş giriş kütlesi ve merkez cam kule; bitkiler nedeniyle uzaklık/açı zayıf.',pitch='yukarı',angle=45)
put([110],'0',(620,452),(483,411),'estimate','Grand Hall taş duvar ve çatı',10,'Taş duvar, cam piramit köşesi ve düşen gölge; dar kadrajda nokta yaklaşık.',pitch='yukarı',angle=35)
put([114],'0',(572,475),(574,323),'estimate','Grand Hall cam üçgeni',8,'Ana cam üçgenin simetrik alt görünüşü, karşıdaki taş duvar ve parapet.',pitch='yukarı',angle=20)
put([115],'-1',(621,397),(649,374),'estimate','Alt kat / yarım daire merdiven',7,'Eğrisel döşeme boşluğu, beton merdiven ve destek 051 ile aynı 0 → −1 bağlantısı. Kullanıcı düzeltmesi sonrası doğru merdiven izdüşümüne taşındı; kamera koordinatı yaklaşık.',pitch='yukarı',angle=30)
put([116],'dis',(300,1250),(500,465),'estimate','Havadan giriş ve doğu cephe',50,'Bina üstten görülüyor; giriş, doğu cephe ve pavyon ortak referans. Yükseklik ve yatay mesafe çözülemedi.',pitch='aşağı; havadan',angle=35)
put([119],'dis',(575,8),(575,360),'estimate','Fort aksından cam üst yapı',12,'Merkez cam çan ve iki yan cam örtünün yaklaşık simetrisi.',pitch='yukarı',angle=20)
put([122],'belirsiz',None,None,'unresolved','Parc Dräi Eechelen / peyzaj yolu',None,'Bitkilendirme ve eğimli çim yol dışında konumu tekilleştirecek bina/harita referansı yok.')
put([123],'belirsiz',None,None,'unresolved','Parc Dräi Eechelen / tarihi duvar',None,'Tek tarihi duvar köşesi ve ağaçlar, arşivdeki vaziyet çizimiyle tekil eşleştirme için yeterli değil.')
put([124],'dis',(239,416),(144,810),'estimate','Doğu hendek kenarı / meydan ağaçları',30,'Uzun hendek duvarı, meydan ağaçları ve yüksek iş yapıları aynı kadrajda; uzaktan panoramik görüş.',angle=40)

# Stair identity is independent of camera position. User correction + source image audit.
for ident in ['045','046','047','048','049','050','051','052','053','054','115']:
    D[ident]['stair_system']='STAIR_GH_DOWN_0_TO_MINUS1'
    D[ident]['review_basis']='2026-10-08 user plan correction + renewed image comparison; camera remains approximate'
for ident in ['019','021','022','023','024','025','026','055']:
    D[ident]['stair_system']='STAIR_GH_UP_0_TO_PLUS1'
for ident in ['041','042','043','044']:
    D[ident]['stair_system']='STAIR_EAST_SPIRAL'

# Reviewed overrides are authoritative. Earlier hypotheses stay above and in the
# immutable pre-audit snapshot for traceability, never silently as accepted poses.
import json
from pathlib import Path
_audit=json.loads((Path(__file__).resolve().parent/'06_Tek_Tek_Denetim/fotograf_denetimi.json').read_text(encoding='utf-8'))
assert {r['id'] for r in _audit}==set(D)
for review in _audit:
    d=D[review['id']]
    d.update(review['overrides'])
    d['evidence']=review['observed_features']+' '+review['decision']
    for field in ['review_status','review_date','camera_pose_verified','metric_geometry_approved','level_status','model_use','crosscheck_ids']:
        d[field]=review[field]
    d['review_decision']=review['decision']
    d['review_basis']='2026-10-08 individual visual audit; see 06_Tek_Tek_Denetim/fotograf_denetimi.json'
