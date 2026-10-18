# Mudam - üretim durumu

[Canlı üretim panosu](URETIM_DURUMU.html) — bu kayıt dosyasını 15 saniyede bir kontrol eder.

10 Ekim 2026. Blender 4.2 / metre / EPSG:32632 yerel koordinatlar.

Yüzdeler yaklaşık iş kapsamı ilerlemesidir: her pakette beş eşit adım, tamamlanan adım 20 ve kısmi adım 10 puan. Modelin ölçü doğruluğu ya da harcanan süre oranı değildir. [İlerleme adımları](config/production_progress.json).

## Güncel teslim

[MUDAM_R149_UST_DOLASIM_TAS_DOSEME_v001.blend](scenes/MUDAM_R149_UST_DOLASIM_TAS_DOSEME_v001.blend) giriş, çatı ve merdiven çalışmalarını birlikte içerir. [Görsel inceleme](URETIM.html) · [Üretim raporu](reports/P07_P09_URETIM_RAPORU.md).

| Paket | Durum | İlerleme | Somut çıktı / açık konu |
| --- | --- | --- | --- |
| P00 — Ortam ve kaynak manifesti | Tamam | %100 | Kaynakların tamamı dosyaya çözülür; orijinaller korunur |
| P01 — Üst kat referans araştırması | Eksikler belgeli | %80 | Açık: UG02/UG03 üst galeri iç ışıklık biçimini destekliyor; çözünürlükleri 150x100. UC01/UC02 yapım kesit biçimini destekliyor. Kesin kanat/kamera ve panel ölçüleri açık. |
| P02 — Kesit tarihi ve izi | Sürüyor | %30 | Açık: 101 kesitinin tarihi ve plan kesit izi çözülmedi. |
| P03 — Yatay referans aktarımı | Tamam | %100 | İki nokta ve yön testi; atlas Y işareti doğru |
| P04 — Düşey ölçü çözümü | Sürüyor | %70 | Üretilen: Ana/alt merdiven, doğu spiral, batı ve pavyon merdivenlerinin koşullu kot zincirleri kuruldu; bölgesel destek ve baş mesafesi kontrolleri mevcut.. Açık: 101 kesit tarihi/izi açık; kat kotları ve gerçek rıht adetleri ölçülmüş değildir. |
| P05 — Tüm bina sade geometrisi | Sürüyor | %70 | Üretilen: Ana hacimler, üst galerilerin 6+4 ışıklık adayı, yan örtüler ve pavyon kuruldu. Batı zemin galerisinde mevcut duvar ile döşeme/tavan arasındaki yaklaşık 20 cm açıklık giderildi. Yalnız iki mevcut nesne genişletildi; 1.030 temas ve 108 giriş/güzergâh kontrolü geçti. Önce/sonra görüntüleri karşılaştırıldı. Okuma odasının eski döşeme kenarı mevcut PDF2016 duvar konturuyla uzlaştırıldı; duvar dibindeki açık şerit giderildi. Merkez boşluk ve üç geçit korundu. 1.313 döşeme/boşluk ve 36 geçiş kontrolü geçti; önce/sonra görüntüleri incelendi. Kafe–batı galeri geçidinde eksik üst örtü oluşturuldu. Aynı kamera karşılaştırmasında yatay yarık kapandı; zemindeki açık geçit korunuyor. Yeniden açılan sahnede önceki 132 örtüsüz örnek kapandı; genel geometri ve galeri geçiş kontrolleri geçti. Doğu galeri girişinin eksik üst örtüsü oluşturuldu. Önceki 81 örtüsüz örnek kapandı; geçitler ve yüksek atrium açıklığı korundu. Aynı kamera görsel karşılaştırması, sahne farkı, geometri ve geçiş kontrolleri geçti; altı merdiven ailesi taramasında yeni baş mesafesi engeli bulunmadı. Zemin katın iki galerisinde servis alanına bakan eksik uzun duvarlar kaynak plan konturunda oluşturuldu. Önceki 360 eksik yüzey örneği kapandı. Galeri ve servis geçişleri, genel geometri ve sahne farkı kontrolleri geçti; iki aynı kamera önce/sonra görüntüsü incelendi. 051 ve 052 fotoğraflarında görülen alt merdiven üst sahanlığı yanındaki eksik düşey taş perde eklendi. Aynı kamera önce/sonra görüntüsü incelendi. Yeni elemanın döşeme ve tavan temasları, alt kat geçişleri, alt merdiven regresyonu ve altı merdivenin baş mesafesi kontrol edildi. Küçük odanın yanlış iç bölmeleri kaldırıldı; dış sınırı ve köprü duvarları üst örtüye bağlandı. Cephe/döşeme kesişimleri, galeri/merdiven duvar birleşimi ve alt katın açık yan hacimleri düzeltildi. Önce/sonra görüntüleri ve yeniden açılan sahne kontrolleri kaydedildi. Cephe köşesi altındaki dönüş tamamlandı; beş pencere, girintileri ve tarihî duvar açıklıkları birlikte köşe içine taşındı. Üst köprünün iki galeriyle döşeme bağlantısı ve doğu duvar ucu üretildi.. Açık: Çevre arazi kolları, eksik cephe açıklıkları ve bütün yapı birleşimlerinin kaynak karşılaştırması sürüyor. Bütün bina tamamlanmadı. Diğer dar duvar–döşeme–tavan temasları kaynaklarla karşılaştırılıyor; mevcut kotlar ve kalınlıklar ölçülmemiş adaylardır. Bütün bina tamamlanmadı. Diğer küçük odaların üst örtüleri, kalan çelik/cam birleşimleri ve bina son kontrolü açık; kesin kot ve malzeme ölçüleri hâlâ aday. Öncelik büyük kabuk sorunları. Doğu merdiveni–duvar birleşimi ve kalan büyük açıklıklar bitmeden köşe veya malzeme detayına geçilmez. Örtü kotu mevcut 4,35 m galeri tavanı adayıdır; ölçülmüş uygulama detayı değildir. Öncelik büyük kabuk sorunları. Kalan büyük duvar/zemin/çatı açıklıkları bitmeden köşe veya malzeme detayına geçilmez. Örtü kotu mevcut 4,35 m galeri tavanı adayıdır; ölçülmüş uygulama detayı değildir. Bütün bina ve kullanıcının tüm ekran görüntüleri henüz kabul edilmedi. Duvar kalınlığı mevcut kaynak konturları arasında uzlaştırılmış adaydır; kotlar ölçülmüş değildir. Öncelik kalan büyük kabuk sorunlarıdır. Elemanın varlığı fotoğrafta görülüyor; yerleşimi mevcut merdiven üst kiriş hattına hizalı adaydır. 0,28 m kalınlık ve mevcut kol genişliği ölçülmüş değildir. Plan 104 bu ayrıntıyı göstermiyor. Bu paket yalnız bir temsilî mimari elemandır; bütün bina veya taşıyıcı sistem kabulü değildir. Büyük kabuk sorunları ve açık üretim işleri önceliğini korur. Bina bütünü ve bütün ölçüler kabul edilmiş değildir. Alt cephe ilk pencere/köşe kayıt uyumu ve ölçülmemiş kalınlıklar açıktır; kapı temsilleri ürün doğrulaması değildir. Fotoğraf 004/116 ve plan 103 esas alındı. Pencere dizisinin 2,459 m kaydırılması mevcut model köşesine göre türetilmiştir; 0,12 m kenar payı ve diğer miras boyutları ölçülü rölöve değildir. Bütün bina kabulü ve kalan üretim işleri açıktır. |
| P06 — Kamera eşleştirme pilotu | Sürüyor | %70 | Açık: 087/119/116 için üç koşullu kamera. 116 karşı görünüşte kontrol RMS 10,05 px. İç kamera ve tam metrik doğrulama açık. |
| P07 — Beton duvar ve döşemeler | Sürüyor | %70 | Üretilen: Duvar/döşeme bölgesel kabukları kapalı; merdiven nişi ve galeri camlarıyla yerel kesimler koordine edildi. 20 nesne ve175 yüzün malzeme/UV adayı;7.942 nesnenin hesaplanan geometrisi değişmedi. Altı yuva ve24 kapalı parça;102 ışın ve7235 görünür mesh kontrolü geçti. 067/068 ile16 çapraz,240 parça;32 destek ve96 uç bağlantısı kontrolü geçti. 067/068 ile 130 yeni parça; 146 bağlantı ve 32 lens açıklığı kontrolü geçti. 7.634 görünür mesh. 54 duvarda 48 ortak köşe; 96 önce/sonra boşluk kontrolü geçti. Alt cephe boşluğu ve iki üst duvar bağlantısı; 561 yüzey, 20 birleşim ve 210 çatı taşma kontrolü. İki kesintisiz duvar gövdesi; 576 yüzey/sınır ve 90 geçiş testi. Beş duvar, dört köşe ve sekiz önce/sonra boşluk kontrolü. Yedi duvarın altı köşesi düzeltildi; 12 önce/sonra ışını, kapalı hacim ve bütün sahne denetimi geçti. İki duvar ucu komşu kaynak sınırına bağlandı; iki temas, 15 açık geçiş ışını ve bütün sahne denetimi geçti. İki mevcut duvarın ortak ucu bağlandı; on iç yüzey örneği, sabit kot ve bütün sahne kontrolü geçti. Doğu düz iç yüzü ve batı kademeli cephe gövdesi; 126 sınır, 1226 oda içi ve 102 merdiven boşluk kontrolü geçti. Eski kare kesicinin sildiği iki çatı köşesi geri getirildi; 342 örtü ve 112 kuzey koruma örneği geçti. 087/119 cephe fotoğraflarına göre alt cam sınırı zemine indirildi; 536 yatay kapanış örneği geçti. 104 planındaki yan hacimlere 31 duvar/döşeme/tavan bileşeni; 405 sınır ve altı geçiş kontrolü geçti. Mevcut zeminin eksik yan camı, üst örtüsü ve iç duvarı eklendi; 312 alt/üst ve 156 yan kapanış örneği geçti. Kafe arkasındaki taş duvar ve iki üçgen cam geçiş tamamlandı; önceki 81 yanal kaçak kapandı. Zeminden18–25cm yukarıda kalan sabit cam ve kayıtlar zemine bağlandı; 18 eski kaçak kapandı. Eski düz uzantı kaldırıldı; PDF kapısına dönen mevcut koridorun duvar ve örtüsü eklendi. 571 sık örnek ve dolaşım denetimi geçti. Orana bağlı küçültme yerine sabit kenar payı; dört örtü kaçağı kapandı. 26 bölgenin sık ve çok kotlu taraması temiz. Eksik alt/üst döşeme ve çatı eklendi; PDF oda sınırı ve açık bağlantısı kuruldu. 29 bölge, 97.080 sık örnek ve 218.136 çok kotlu ışın kontrol edildi. Merdiven basamaklarından bulunan sekiz cam kenarı kaçağı kapatıldı; 170 konum ve 12.240 yanal ışın taraması temiz. Tavanda biten 37 çevre duvarı, zemin kat döşemesinin altına bağlandı. 296 önce/sonra ışın ve iki bina görünüşü kontrol edildi. Eski çatı kotlarında kalan batı uç duvarının üst eğimi ve yüksek plan ucu mevcut cam çatıya bağlandı. 597 yerel birleşim kontrolü geçti. Kullanıcının işaretlediği batı diyagonal bölmesi ve aynı yorumla eklenen doğu eşi kaldırıldı. 54 geçiş doğrultusu açık; zemin, tavan ve dış kabuk korundu. İki eski mavi iç yüzey kaldırıldı; batı üst cam geçişi çerçevelendi, ara çatı örtüsü ve doğu üst duvar bağlantısı üretildi. Doğu merdiven yan duvarı bitişik cam örtü kotunda sonlandırıldı. Sağ cam birleşimi ve dış uç kapatıldı; kafe zemin katındaki yanlış duvar kaldırıldı; doğu galeri giriş duvarı geri kuruldu. Önceki sahnedeki 75 başarısız yerel kontrol yeni sahnede geçti. R96: Küçük batı galerisini kesen iki eski zemin kat duvarı üst döşeme altında sonlandırıldı. 2016 iç oda ile 103 merdiven kabuğunun farklı ölçekleri uzlaştırıldı; iki iç duvar kopyası kaldırıldı, kafe üzerine taşan +1 döşemesi daraltıldı. Okuma alanının doğusundaki eksik oda, servis merdiveni sınırı ve üst asansör kuyusu yüzleri kaynak planıyla üretildi. Kafe çatısına fotoğrafta görünen alt çubuk sistemi aday ölçülerle eklendi. Servis merdivenine 24 basamak/sahanlık parçası eklendi; yolu kesen alt kat tavanı ve giriş duvarı yerel olarak açıldı. Yedi kuyu duvarı iki kat arasında devam ettirildi. 110 yerel kontrol ve önceki duvar/cam düzeltmelerinin gerileme kontrolü geçti. +1 kat köprüsüne taşan merdiven arka duvarı, üst başlık ve lento üç parçada kaynak plan sınırına çekildi. Aynı 118 yerel karşılaştırmada önceki 116 taşma yeni sahnede sıfır. Diğer işaretli bölgeler henüz tamamlanmadı. Batı galerinin planda çizili kısa giriş duvarı eklendi. Kuzey geçidini kapatan, üst odadan yanlış devam ettirilmiş R87 alt duvarı kaldırıldı. 15 duvar noktası ve iki girişte altı geçiş kontrolü geçti. İki galeri tavanının dokuz plan noktası mevcut giriş duvarlarının iç yüzüne bağlandı. En büyük yerel uyumsuzluk 0,337 m idi; kontrol edilen 18 alt/üst köşe artık aynı sınırda. Batı galeri duvarı ve iki girişin geçiş kontrolleri yeniden geçti. Okuma odası–doğu servis odası bağlantısının planda çizili fakat eksik bırakılmış iki yan duvarı eklendi. 15 eksik duvar probu düzeldi; dokuz geçiş ve sekiz zemin/tavan kontrolü geçti. Diğer mevcut geometri değişmedi. Üst servis odası ve merdiven kuyusunda 14 duvarın 12 dış köşesi birleştirildi. Önceden açık olan 10 köşe probu kapandı; iç plan çizgileri ve açıklıklar korundu. Servis merdiveninin 110 kontrolü yeniden geçti. Batı üst galeriye taşan dört duvar/tavan parçası mevcut plan sınırına kırpıldı. Servis odası birleşimindeki çıkıntı ve merdiven dönüşündeki yanlış tavan uzantısı kaldırıldı. Kapı ve koridor geçişleri korundu. Alt batı galeri girişindeki kısa duvarın 5 cm geride kalan arka yüzü, komşu merdiven duvarıyla hizalandı. Ön yüz, giriş ucu ve kotlar korundu; alt galeri geçiş kontrolleri geçti. Batı zemin galerisinde mevcut duvar ile döşeme/tavan arasındaki yaklaşık 20 cm açıklık giderildi. Yalnız iki mevcut nesne genişletildi; 1.030 temas ve 108 giriş/güzergâh kontrolü geçti. Önce/sonra görüntüleri karşılaştırıldı. WC, vestiyer ve dükkânda 15 mevcut duvarın 11 ortak köşesi birleştirildi. Önceki 22 boşluk örneği kapandı; kaynak eksenleri, kalınlık, kotlar ve kapı uçları korundu. 44 köşe ve 96 servis geçiş/destek kontrolü geçti; yakın önce/sonra görüntüleri incelendi. Servis merdiveni altındaki üç mevcut duvarın iki köşesi birleştirildi. Önceki dört boşluk örneği kapandı; mevcut kapı kesisi ve merdiven korundu. Sekiz köşe örneği, genel geometri ve merdiven geçiş kontrolleri geçti; önce/sonra görüntüleri incelendi. Kafe–batı galeri geçidinde eksik üst örtü oluşturuldu. Aynı kamera karşılaştırmasında yatay yarık kapandı; zemindeki açık geçit korunuyor. Yeniden açılan sahnede önceki 132 örtüsüz örnek kapandı; genel geometri ve galeri geçiş kontrolleri geçti. Doğu galeri girişinin eksik üst örtüsü oluşturuldu. Önceki 81 örtüsüz örnek kapandı; geçitler ve yüksek atrium açıklığı korundu. Aynı kamera görsel karşılaştırması, sahne farkı, geometri ve geçiş kontrolleri geçti; altı merdiven ailesi taramasında yeni baş mesafesi engeli bulunmadı. Zemin katın iki galerisinde servis alanına bakan eksik uzun duvarlar kaynak plan konturunda oluşturuldu. Önceki 360 eksik yüzey örneği kapandı. Galeri ve servis geçişleri, genel geometri ve sahne farkı kontrolleri geçti; iki aynı kamera önce/sonra görüntüsü incelendi. 051 ve 052 fotoğraflarında görülen alt merdiven üst sahanlığı yanındaki eksik düşey taş perde eklendi. Aynı kamera önce/sonra görüntüsü incelendi. Yeni elemanın döşeme ve tavan temasları, alt kat geçişleri, alt merdiven regresyonu ve altı merdivenin baş mesafesi kontrol edildi. Küçük odanın yanlış iç bölmeleri kaldırıldı; dış sınırı ve köprü duvarları üst örtüye bağlandı. Cephe/döşeme kesişimleri, galeri/merdiven duvar birleşimi ve alt katın açık yan hacimleri düzeltildi. Önce/sonra görüntüleri ve yeniden açılan sahne kontrolleri kaydedildi. Cephe köşesi altındaki dönüş tamamlandı; beş pencere, girintileri ve tarihî duvar açıklıkları birlikte köşe içine taşındı. Üst köprünün iki galeriyle döşeme bağlantısı ve doğu duvar ucu üretildi. İki köprü bağlantı döşemesinin mevcut galeri eşikleriyle çakışan hacimleri çıkarıldı. Yeni parçalar yalnız eksik yan şeritlerde kalıyor; eski eşik ve zemin yüzeyi korunuyor. Üst galerilerin dört eşiğinde ve batı dönüş döşemesinde yinelenen yüzeyler ayrıldı. Tamamen diğer döşemenin içinde kalan bir dönüş parçası gizlendi; açıklıklar ve bitmiş zemin kotu korundu. Alt fuaye ile oditoryum döşemesinin çakışan ön şeridi ayrıldı. Fuaye döşemesiyle bütünüyle örtüşen iki giriş döşemesi gizlendi; özgün nesneler ve girişlerin zemin kapanışı korundu. Zemin katta doğu dolaşım alanı, batı kafe ve küçük oda birleşimindeki üst üste binen döşeme hacimleri ayrıldı. Tamamen yinelenen bağlantı eşiği gizlendi; döşeme kapsamı korundu. Batı üst kat dönüş tavanındaki yinelenen örtü gizlendi; kafe tavanı ile ön servis örtüsünün örtüşen hacmi ayrıldı. Doğu yüksek duvarı, giriş başlığı, kafe sınırı, batı iç duvar ve köprü ucundaki yinelenen duvar hacimleri ayrıldı. Alt oditoryum giriş duvarları, üst servis geçitleri ve batı cam/galeri duvar sınırlarında yedi hacim örtüşmesi ayrıldı. Üst köprü, sahanlık, okuma odası, Studio ve doğu oda döşemelerinin altı örtüşmesi ayrıldı. Alt fuaye örtüsü ile oditoryumun iki yan örtüsü ve iki alt galeri örtüsünün dört hacim çakışması ayrıldı. Okuma odasının eğimli örtüsü ile doğu odasının düz örtüsü arasındaki yinelenen hacim ayrıldı.. Açık: Kalınlıklar ve gizli taşıyıcı sistem koşullu; bütün bina için yapı fiziği/çakışma kabulü yapılmadı. Renk, derz, malzeme bileşimi ve çizgisel yüzey derinliği ölçülmedi; saçak kotu koşullu. Fotoğraf homografisi düşük güvenli: dışarıda bırakma hatası188,89px. Çap, profil, kot ve tam armatür sayısı doğrulanmadı. Sekiz göz devralındı; çap,kot,çatal ve ankraj ölçülmedi. Yapısal hesap değildir. 32 adet sekiz göze uygulanan tekrar adayı; çap, kot, ürün ve fotometri doğrulanmadı. Duvar ölçüleri koşullu; diğer duvarlar ve yan salon birleşimleri açık. Mevcut kaynak sınırları korundu; kalınlık/kotlar koşullu. Genel duvar kabulü açık. Kaynak planlara bağlı yerel düzeltme; kesin kalınlık ve kotlar koşullu. Genel duvar kabulü açık. Plan eşlemesindeki uç farkı giderildi. Üst kot ve cam/çatı ilişkisi ayrı açık kontroldür. İç ve dış kaynak sınırları arasındaki gövde koşullu; ölçülmüş duvar kalınlığı değildir. Genel duvar kontrolü sürüyor. Mevcut kotlar korundu; genel duvar–zemin–çatı kapanışı sürüyor. Gerçek okuma boşluğu korundu. Üst camlar ve mevcut yatay kayıt korundu. Alt panel bölüntüsü ve profil ölçüleri kesin değil; genel kabuk kontrolü açık. Şematik plan çizgileri, mevcut aday kalınlık ve fuaye kotları kullanıldı. Asansör donanımı ve kapı detayları yapılmadı. 102/066/097 kaynakları; mevcut 3,2 m başlık yüksekliği aday olarak korundu. Cam bölüntü ve ürün ayrıntıları ertelendi. 093/102/026/116 ile mevcut sınırlar kullanıldı; kotlar ve cam detayları aday. Çok kotlu taramada giriş alt cam birleşimi hâlâ açık. 013/014 ile zemine kapanış; hareketli kanatlar değişmedi. Kesin montaj payları ve profil ölçüleri aday. PDF ile ziyaretçi şeması arasındaki iç sınır farkı kayıtlı; kesin yeniden ölçüm değildir. Malzeme ve ayrıntı ölçüleri aday. Cam kenar payı görselleştirme parametresidir; plan, kesit ve imalat ölçüsü doğruluğu ayrı değerlendirilir. PDF ve ziyaretçi şeması farklı; kot, kalınlık ve yerel çatı eğimi kesinleşmedi. Bütün bina kabulü açık. Yalnız panel kenar payı değişti. Merdiven ölçüsü, eğimi ve profil düzeni yeniden ölçülmüş sayılmaz. İç tavan kotu değişmedi; duvar/döşeme kesin kesiti ve kat planları arasındaki yerel farklar koşullu. 200 mm taş üst payı adaydır. Kesin imalat kesiti ve tüm bina kabulü açık. Kalıcı duvar olduğu doğrulanmayan iki aday kaldırıldı. İdari/teknik hacimler ve kesin çatı biçimi kabulü açık. Çatı ara örtüsü ve profil ölçüleri aday. Köşe profilleri, batı küçük çatı uç birleşimi ve ayrıntılı kaynak eşleştirmesi açık; tüm bina tamamlanmadı. Sabit mimari geometri düzeltmesi. Kesin ölçüler, çatı imalat kesiti, profil ve malzeme kabulü açık; tüm bina tamamlandı sayılmadı. Yerel plan kaydı ve çelik çubuk ölçüleri adaydır. Servis merdiveni basamakları, bütün katlar arasında devamlılık ve kesin imalat ölçüleri açık. Bina tamamlanmış sayılmadı. Plan sembolündeki 24 bölme ölçülmüş rıht sayısı değildir. Dönüş yönü, rıht yüksekliği ve sahanlık aday; korkuluk ve alt kata devam ilişkisi açık. Bütün bina kabulü yapılmadı. Asansör çevresi, Studio/servis odası dışındaki kat ilişkileri ve son iki galeri duvar–döşeme işareti açık. Bu paket yalnız köprüye taşan duvarı düzeltir. Merdiven yanı ikinci galeri işareti ile +1 Studio/servis/asansör çevresinin bütün kat ilişkileri açık; tüm ekran görüntüleri çözüldü denmedi. Bu yerel çizim uzlaştırması ölçülmüş imalat geometrisi değildir. Gerçek giriş boşlukları ve fotoğraf 026’daki yüksek merdiven yanı geçidi korunur. +1 Studio/servis/asansör çevresinin bütün kat ilişkileri ve diğer kabuk birleşimleri açık. +1 Studio, asansör ve diğer katlar arası kabuk ilişkileri hâlâ inceleniyor. Geçit duvarının yüksekliği ve kalınlığı aday; bütün bina kabulü yok. Bütün bina kabulü yok. Diğer üst kat duvar/örtü birleşimleri ve katlar arası devamlılık kontrolü sürüyor; ölçülmemiş kalınlık ve kotlar aday. Bütün bina kabulü yok. Diğer kabuk birleşimleri ve kat ilişkileri kaynaklarla karşılaştırılmaya devam ediyor; ölçülmemiş kotlar ve kalınlıklar aday. Bütün bina kabulü yok. Diğer kabuk birleşimleri ve kat ilişkileri kaynaklarla karşılaştırılıyor; komşudan devralınan kalınlık ve kotlar ölçülmemiş adaylardır. Bütün bina tamamlanmadı. Diğer dar duvar–döşeme–tavan temasları kaynaklarla karşılaştırılıyor; mevcut kotlar ve kalınlıklar ölçülmemiş adaylardır. Bütün bina tamamlanmadı. Diğer kabuk birleşimleri, merdiven/kapı detayları ve bütünleşik kaynak kontrolü açık; ölçülmemiş kalınlık ve kotlar aday. Öncelik büyük kabuk sorunları. Doğu merdiveni–duvar birleşimi ve kalan büyük açıklıklar bitmeden köşe veya malzeme detayına geçilmez. Örtü kotu mevcut 4,35 m galeri tavanı adayıdır; ölçülmüş uygulama detayı değildir. Öncelik büyük kabuk sorunları. Kalan büyük duvar/zemin/çatı açıklıkları bitmeden köşe veya malzeme detayına geçilmez. Örtü kotu mevcut 4,35 m galeri tavanı adayıdır; ölçülmüş uygulama detayı değildir. Bütün bina ve kullanıcının tüm ekran görüntüleri henüz kabul edilmedi. Duvar kalınlığı mevcut kaynak konturları arasında uzlaştırılmış adaydır; kotlar ölçülmüş değildir. Öncelik kalan büyük kabuk sorunlarıdır. Elemanın varlığı fotoğrafta görülüyor; yerleşimi mevcut merdiven üst kiriş hattına hizalı adaydır. 0,28 m kalınlık ve mevcut kol genişliği ölçülmüş değildir. Plan 104 bu ayrıntıyı göstermiyor. Bu paket yalnız bir temsilî mimari elemandır; bütün bina veya taşıyıcı sistem kabulü değildir. Büyük kabuk sorunları ve açık üretim işleri önceliğini korur. Bina bütünü ve bütün ölçüler kabul edilmiş değildir. Alt cephe ilk pencere/köşe kayıt uyumu ve ölçülmemiş kalınlıklar açıktır; kapı temsilleri ürün doğrulaması değildir. Fotoğraf 004/116 ve plan 103 esas alındı. Pencere dizisinin 2,459 m kaydırılması mevcut model köşesine göre türetilmiştir; 0,12 m kenar payı ve diğer miras boyutları ölçülü rölöve değildir. Bütün bina kabulü ve kalan üretim işleri açıktır. R117 bağlantılarına ait düzeltmedir; 62 önceki çift yüzey örneği giderildi, 78 son örnekte tek zemin yüzeyi var. Yeni mimari ölçü eklenmedi. Bütün bina kabulü değildir. 1.364 yerel örneğin 716sında önce çift/üçlü yüzey vardı; sonra tüm örneklerde tek yüzey var. Beş mevcut nesne değişti, yeni nesne ve ölçü eklenmedi. Bütün bina kabulü değildir. 15.436 örneğin 306sında önce çift üst yüzey vardı; sonra tüm örneklerde tek yüzey var. Üç mevcut nesne değişti, yeni nesne veya ölçü yok. Bütün bina kabulü değildir. Altı mevcut nesne değişti; yeni nesne veya mimari ölçü yok. 47.667 konumun 1.569unda önce çift yüzey vardı; sonra tüm örneklerde tek üst yüzey var. Bütün bina kabulü değildir. İki mevcut nesne değişti. 7.178 konumun 152sinde önce çift üst yüzey vardı; sonra tamamında tek yüzey var. Örtü kapsamı korundu; bütün bina kabulü değildir. Beş mevcut nesne değişti, yeni nesne veya mimari boyut yok. Altı yönden 88.912 örnekte birleşik dış sınır ve açıklıklar korundu. Bütün bina kabulü değildir. Yedi mevcut nesne değişti; yeni nesne veya mimari boyut yok. 24.036 ışında birleşik dış sınır ve açıklık kapsamı korundu. Bütün bina kabulü değildir. Beş mevcut nesne değişti; yeni nesne veya mimari boyut yok. 6.336 örnekte zemin kapsamı korundu, önceki 304 çift üst yüzey giderildi. Bütün bina kabulü değildir. Dört mevcut nesne değişti; yeni nesne veya mimari boyut yok. Altı yönden 250.156 örnekte birleşik dış sınır korundu. Bütün bina kabulü değildir. Bir mevcut örtü değişti; yeni nesne veya mimari boyut yok. Birleşik dış sınır korunumu örneklendi; bütün bina kabulü değildir. |
| P08 — Kapı pencere ve mekân listesi | Sürüyor | %70 | Üretilen: Giriş kanatları, galeri geçişleri, oditoryum ve pavyon kapıları, asansör sahanlığı, galeri ve alt cephe cam adayları üretildi. 18–25cm yüksekteki hatalı tam boy profil kaldırıldı;2m statik geçişte189 ışın ve63 döşeme örneği geçti. Zeminden18–25cm yukarıda kalan sabit cam ve kayıtlar zemine bağlandı; 18 eski kaçak kapandı.. Açık: Bütün kapı/pencere listesi ve kaynak eşlemesi tamamlanmadı; servis alanları ve donanım kimlikleri açık. Geniş2,2m tarama sağ panele çarpar; hareketli kanatlar bu statik testten ayrı. Gerçek kapı mekanizması ve eşik ölçüsü açık. 013/014 ile zemine kapanış; hareketli kanatlar değişmedi. Kesin montaj payları ve profil ölçüleri aday. |
| P09 — Merdiven ve sahanlıklar | Sürüyor | %80 | Üretilen: İki Grand Hall merdiveni, doğu spiral, batı kol ve pavyon merdiveni adayları; alt küpeşte sürekliliği işlendi. Servis merdivenine 24 basamak/sahanlık parçası eklendi; yolu kesen alt kat tavanı ve giriş duvarı yerel olarak açıldı. Yedi kuyu duvarı iki kat arasında devam ettirildi. 110 yerel kontrol ve önceki duvar/cam düzeltmelerinin gerileme kontrolü geçti. +1 kat köprüsüne taşan merdiven arka duvarı, üst başlık ve lento üç parçada kaynak plan sınırına çekildi. Aynı 118 yerel karşılaştırmada önceki 116 taşma yeni sahnede sıfır. Diğer işaretli bölgeler henüz tamamlanmadı.. Açık: Gerçek rıht adetleri/kesitler koşullu; pavyon alt bağlantı ve merkez çekirdek kaynakları yetersiz. Plan sembolündeki 24 bölme ölçülmüş rıht sayısı değildir. Dönüş yönü, rıht yüksekliği ve sahanlık aday; korkuluk ve alt kata devam ilişkisi açık. Bütün bina kabulü yapılmadı. Asansör çevresi, Studio/servis odası dışındaki kat ilişkileri ve son iki galeri duvar–döşeme işareti açık. Bu paket yalnız köprüye taşan duvarı düzeltir. |
| P10 — Ana cam örtü | Sürüyor | %80 | Üretilen: Ana çatı panel/metal ağı, dört geniş yüzde 3816 gölgelik lameli, okuma fenerinin kare gövdesi üretildi. 067/068 ile16 çapraz,240 parça;32 destek ve96 uç bağlantısı kontrolü geçti. Ana cam çatının dördüncü yüzünde aynı yerde iki kez üretilmiş iki çelik profil gizlendi; mevcut karşılıkları korundu.. Açık: Cam/profil kesitleri ve bağlantılar ölçülmedi; gizli gölgelik mekanizması doğrulanmadı. Sekiz göz devralındı; çap,kot,çatal ve ankraj ölçülmedi. Yapısal hesap değildir. İki nesne değişti. Eşleşen profillerin en büyük köşe farkı 0,0027 mm; yüzler ve malzemeler aynı. Yeni mimari boyut yok; bütün bina kabulü değildir. |
| P11 — Yan salon ve pavyon örtüleri | Sürüyor | %90 | Üretilen: Batı 108 düz cam, pavyon 108 cam/216 profil, doğu cam şeridi ve üst galerilerin 10 ışıklık adayı kuruldu. Eski kare kesicinin sildiği iki çatı köşesi geri getirildi; 342 örtü ve 112 kuzey koruma örneği geçti. Mevcut zeminin eksik yan camı, üst örtüsü ve iç duvarı eklendi; 312 alt/üst ve 156 yan kapanış örneği geçti. Kafe arkasındaki taş duvar ve iki üçgen cam geçiş tamamlandı; önceki 81 yanal kaçak kapandı. Orana bağlı küçültme yerine sabit kenar payı; dört örtü kaçağı kapandı. 26 bölgenin sık ve çok kotlu taraması temiz. Merdiven basamaklarından bulunan sekiz cam kenarı kaçağı kapatıldı; 170 konum ve 12.240 yanal ışın taraması temiz. Çerçevesiz tek cam temsilinin yerine 12 cam panel ve 9 metal çerçeve parçası üretildi. 51.914 yerel yüzey örneği ve yeniden açılan sahne kontrolleri geçti. Eski çatı kotlarında kalan batı uç duvarının üst eğimi ve yüksek plan ucu mevcut cam çatıya bağlandı. 597 yerel birleşim kontrolü geçti. Merkez düşey cam şeridi yeniden üretildi: yan banttaki dört yatay kayıt kotu ortak, alt modüller aynı aralığı sürdürüyor. 30 cam panel ve 15 profil; 140.794 yüzey örneği açık vermedi. İki eski mavi iç yüzey kaldırıldı; batı üst cam geçişi çerçevelendi, ara çatı örtüsü ve doğu üst duvar bağlantısı üretildi. Doğu merdiven yan duvarı bitişik cam örtü kotunda sonlandırıldı. Sağ cam birleşimi ve dış uç kapatıldı; kafe zemin katındaki yanlış duvar kaldırıldı; doğu galeri giriş duvarı geri kuruldu. Önceki sahnedeki 75 başarısız yerel kontrol yeni sahnede geçti. R96: Küçük batı galerisini kesen iki eski zemin kat duvarı üst döşeme altında sonlandırıldı. 2016 iç oda ile 103 merdiven kabuğunun farklı ölçekleri uzlaştırıldı; iki iç duvar kopyası kaldırıldı, kafe üzerine taşan +1 döşemesi daraltıldı. Okuma alanının doğusundaki eksik oda, servis merdiveni sınırı ve üst asansör kuyusu yüzleri kaynak planıyla üretildi. Kafe çatısına fotoğrafta görünen alt çubuk sistemi aday ölçülerle eklendi.. Açık: Panel bölünmesi, tekrarlanan kabuk adedi, kesin başlık/kenar detayları koşullu. Mevcut kotlar korundu; genel duvar–zemin–çatı kapanışı sürüyor. Gerçek okuma boşluğu korundu. 102/066/097 kaynakları; mevcut 3,2 m başlık yüksekliği aday olarak korundu. Cam bölüntü ve ürün ayrıntıları ertelendi. 093/102/026/116 ile mevcut sınırlar kullanıldı; kotlar ve cam detayları aday. Çok kotlu taramada giriş alt cam birleşimi hâlâ açık. Cam kenar payı görselleştirme parametresidir; plan, kesit ve imalat ölçüsü doğruluğu ayrı değerlendirilir. Yalnız panel kenar payı değişti. Merdiven ölçüsü, eğimi ve profil düzeni yeniden ölçülmüş sayılmaz. Açıklık sınırları korundu. Sıra sayısı, profil ve cam kalınlıkları ölçülmemiş aday; bütün bina ve birleşim detayları kabulü açık. 200 mm taş üst payı adaydır. Kesin imalat kesiti ve tüm bina kabulü açık. Profil boyutları ve alt sıra sayısı ölçülmemiş aday. Önceki duvar–çatı birleşimi işaretleri açık; tüm bina kabulü yapılmadı. Çatı ara örtüsü ve profil ölçüleri aday. Köşe profilleri, batı küçük çatı uç birleşimi ve ayrıntılı kaynak eşleştirmesi açık; tüm bina tamamlanmadı. Sabit mimari geometri düzeltmesi. Kesin ölçüler, çatı imalat kesiti, profil ve malzeme kabulü açık; tüm bina tamamlandı sayılmadı. Yerel plan kaydı ve çelik çubuk ölçüleri adaydır. Servis merdiveni basamakları, bütün katlar arasında devamlılık ve kesin imalat ölçüleri açık. Bina tamamlanmış sayılmadı. |
| P12 — Üç örnek detay bölgesi | Sürüyor | %80 | Üretilen: Girişte dört düz cam kanat; kıvrımlı cam/küpeşte; galeri camının plan sınırı ve taş nişi örnekleri üretildi. 60 yeni parça ve iki döşemede sıfır kotuyla aynı biten yuva;441 destek örneği,52 kapı açısı ve204 yaklaşım kontrolü geçti. 014 ile28 parça,4 destek ve mevcut kapı pozu kontrolü;7263 görünür mesh denetlendi. 18–25cm yüksekteki hatalı tam boy profil kaldırıldı;2m statik geçişte189 ışın ve63 döşeme örneği geçti. 067/068 ile16 çapraz,240 parça;32 destek ve96 uç bağlantısı kontrolü geçti. 067/068 ile 130 yeni parça; 146 bağlantı ve 32 lens açıklığı kontrolü geçti. 7.634 görünür mesh. 087/119 cephe fotoğraflarına göre alt cam sınırı zemine indirildi; 536 yatay kapanış örneği geçti. Küçük odanın yanlış iç bölmeleri kaldırıldı; dış sınırı ve köprü duvarları üst örtüye bağlandı. Cephe/döşeme kesişimleri, galeri/merdiven duvar birleşimi ve alt katın açık yan hacimleri düzeltildi. Önce/sonra görüntüleri ve yeniden açılan sahne kontrolleri kaydedildi. Cephe köşesi altındaki dönüş tamamlandı; beş pencere, girintileri ve tarihî duvar açıklıkları birlikte köşe içine taşındı. Üst köprünün iki galeriyle döşeme bağlantısı ve doğu duvar ucu üretildi.. Açık: Kapı mekanizması, doğrama ürünü ve bağlayıcı kesitlerin gerçek ölçüleri yok; yakın detay kaynak karşılaştırması sürüyor. Bölünme, yuva derinliği, malzeme ve ızgara adımı aday; gerçek kapı mekanizması doğrulanmadı. Boyut,ürün,işlev,delik deseni ve tam hareket mekanizması açık. Eski sabit alt profil hatası R64 kapsamına alındı. Geniş2,2m tarama sağ panele çarpar; hareketli kanatlar bu statik testten ayrı. Gerçek kapı mekanizması ve eşik ölçüsü açık. Sekiz göz devralındı; çap,kot,çatal ve ankraj ölçülmedi. Yapısal hesap değildir. 32 adet sekiz göze uygulanan tekrar adayı; çap, kot, ürün ve fotometri doğrulanmadı. Üst camlar ve mevcut yatay kayıt korundu. Alt panel bölüntüsü ve profil ölçüleri kesin değil; genel kabuk kontrolü açık. Bina bütünü ve bütün ölçüler kabul edilmiş değildir. Alt cephe ilk pencere/köşe kayıt uyumu ve ölçülmemiş kalınlıklar açıktır; kapı temsilleri ürün doğrulaması değildir. Fotoğraf 004/116 ve plan 103 esas alındı. Pencere dizisinin 2,459 m kaydırılması mevcut model köşesine göre türetilmiştir; 0,12 m kenar payı ve diğer miras boyutları ölçülü rölöve değildir. Bütün bina kabulü ve kalan üretim işleri açıktır. |
| P13 — Taş yüzeyler ve derzler | Sürüyor | %80 | Üretilen: Taş cephe/zemin, iki ana merdiven mineral yüzeyleri, galeri nişi ve tarihî örgü UV adayları işlendi. Mevcut döşemede50 yüz: koyu taş ve açık kenar bandı. Yüzey/hacim karşılaştırması ve204 yaklaşım örneği geçti. 20 nesne ve175 yüzün malzeme/UV adayı;7.942 nesnenin hesaplanan geometrisi değişmedi. 013 yakın çekimiyle R59 şaşırtmalı örgüsü değiştirildi;17 yüz ve bütün sahnede geometri eşitliği kontrolü geçti. 067 ile iki üst yüzün taş görünümü işlendi. Bütün sahnede hesaplanan geometri aynı; UV ve doku kontrolleri geçti. 28 mevcut çevre parçasında tarihî taş ve hendek çimi için renk, normal ve pürüzlülük dokuları yenilendi. Sonradan üretilen 12 kabuk parçasındaki 115 yüz mevcut taş duvar ve taş döşeme ailelerine bağlandı. Sekiz duvarın düşey yüzleri ve dört döşeme bağlantısının üst yüzleri metrik UV aldı. Üç arşiv yol güzergâhı mevcut park zemininin koordinatlı kaplama dokusuna işlendi: 83345393 ve 49910981 taş döşeme, 50643005 küçük taş kaplama sınıfını taşır. İki gömülü 4096px doku ve tek malzeme kullanılır. Okuma alanının sekiz eğimli tavanı ve doğu spiral merdiveninin basamak, çekirdek, kenar ve komşu taş yüzeylerinde 50 mevcut nesnenin 3484 yüzüne taş malzemesi ve metrik UV uygulandı. Oditoryumun 230 mevcut ahşap panel, kapı ve çevre parçasına düşey damar dokusu ve yüz yönüne göre UV uygulandı. Akustik delikler, derzler ve açıklıklar değişmedi. Oditoryum zemin, sahne, geçiş basamakları ve taş ayaklarda 51 mevcut nesnenin 318 nötr yüzüne taş tane malzemesi ve metrik UV uygulandı. Batı cam merdiveninin iki kolu, sahanlıkları ve taş iç duvarlarında 41 mevcut nesnenin 249 yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. Giriş ile doğu/batı galeri dolaşımının üç mevcut döşemesinde yaklaşık 580m² üst yüzey, ortak taş plak ailesine ve metrik UV düzenine bağlandı. Grand Hall ana duvarları ve galeri dış yüzlerinde dokuz mevcut nesnenin 58 nötr yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. Doğu bahçe galerisinin yaklaşık 334m² mevcut zemininin üst yüzü taş plak malzemesine ve metrik UV düzenine bağlandı. Batı merdiven giriş iç duvarı ve kafe arka duvarı/başlığındaki üç mevcut nesnenin 18 nötr yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. Alt fuaye kuzey duvarının yaklaşık 169m² düşey yüzeyine taş derzi ve metrik UV uygulandı; yatay kenarlarda taş tane ailesi kullanıldı. Alt fuayenin yaklaşık 321m² tavan altı ve kavisli alın yüzeyinde 155 yüze taş tane malzemesi ve metrik UV uygulandı. Kuzey cam çatı doğu taş alın/alt duvarı ve batı uç duvarındaki üç mevcut nesnenin 19 nötr yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. Batı kavisli cam cephenin altındaki 18 mevcut taş duvar parçasının 144 yüzüne taş malzemesi ve kavis boyunca sürekli metrik UV uygulandı. Batı dönüşündeki beş mevcut taş duvar ve alt fuaye merdiven perdesinin toplam 36 nötr yüzüne taş malzemesi ve metrik UV uygulandı. Batı kafenin yaklaşık 288m² mevcut döşemesindeki 33 üst yüze taş malzemesi ve metrik UV uygulandı. Üst köprünün mevcut döşemesindeki iki üst yüze komşu taş ailesi ve metrik UV uygulandı; yalnız P05_FLOOR_LP1_BRIDGE değişti.. Açık: Blok/derz modülleri, numune renkleri ve gerçek taş dizimi bilinmiyor; bazı yüzeyler hâlâ düz malzeme. Taş modülü, derz, renk, yön ve0,65m bant genişliği ölçülmemiş görünüm adayları. Renk, derz, malzeme bileşimi ve çizgisel yüzey derinliği ölçülmedi; saçak kotu koşullu. Örgü tipi fotoğraftan;200×50mm modül,derz,renk ve yön aday. 900mm hücre,1,2mm derz,yön ve desen aday; fotoğraf dizimi birebir izlenmedi. Geometri ve UV değişmedi. 4x3m tekrar önceki aday ölçüdür; tekil taş, bitki türü ve fiziksel renk doğrulaması yok. Bina veya tüm çevre tamamlanmış değildir. Geometri, açıklıklar ve kotlar değişmedi. 3.2x2.4m duvar ve 3.6x3.6m döşeme tekrarları önceki görünüm adaylarıdır; ölçülmüş derz veya fiziksel renk kabulü değildir. Ara push yok; kapsam puanı değiştirilmedi. Mevcut zemin geometrisi birebir korundu. Yol genişliği 4m aday; 600x300mm ve160x120mm görsel modüller, renk/derz düzeni ölçülmedi. V001–v003 yüz bölme adayları geometri/UV hatası nedeniyle reddedildi; v004 kabul edildi. Ara push yok. 015/016 ve 041/043 fotoğrafları taş yüzey sınıfını destekler. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; ölçülmüş panel, renk veya fiziksel kalibrasyon değildir. Geometri birebir korundu. Ara push yok. 073 fotoğrafı ahşap sınıfı ve düşey damar yönünü destekler. 1.2x2.4m doku tekrarı, ağaç türü, damar şekli ve renk ölçülmüş değildir. İnceleme ışıkları yalnız render için eklendi; sahneye kaydedilmedi. Ara push yok. 071/073 fotoğrafları açık taş yüzey ailesini destekler. 2m doku tekrarı, renk ve taş türü ölçülmüş değildir; yeni derz çizelgesi üretilmedi. Tane etkisi oda uzaklığında hafiftir. Geometri, basamak kenarları ve açıklıklar birebir korundu. Ara push yok. 066 fotoğrafı taş basamak ve derzli taş duvar ailesini destekler. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; kesin taş modülü, renk ve metrik kamera çözülmedi. Geometri ve açıklıklar birebir korundu. Ara push yok. 017/026/070/077 taş yüzey sınıfını destekler; 0.9m plak, 3.6m tekrar ve kanonik yön mevcut R43 görünüm adayıdır, ölçülmüş derz dizimi değildir. Geometri ve açıklıklar birebir korundu. Ara push yok. 026/034/087/119 kaynakları taş yüzey sınıfını destekler. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; ölçülmüş panel çizelgesi ve renk kalibrasyonu değildir. Galeri iç beyaz yüzleri, geometri ve gerçek açıklıklar korundu. Ara push yok. 041/043 taş yüzey ailesini destekler. 0.9m plak ve 3.6m tekrar mevcut R43 görünüm adayıdır; ölçülmüş derz çizelgesi değildir. Geometri ve açıklıklar birebir korundu. Ara push yok. 066/097 giriş taş duvarını, 093 kafe arkasındaki taş sınırı destekler. Mevcut R82/R83 kabuk adaylarının ölçü ve konum belirsizliği sürer. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; ölçülmüş panel çizelgesi veya renk değildir. Geometri ve giriş açıklığı korundu. Ara push yok. 051/055 alt fuayenin taş yüzey ailesini destekler. R72 sınır/kot adayları değişmedi. 2m tane ve 3.2x2.4m derz tekrarları ölçülmüş panel çizelgesi değildir. Geometri birebir korundu. Ara push yok. 051/055 taş tavan ailesini destekler. 2m tane tekrarı görsel adaydır; fotoğraftaki tekil plak derzleri yeniden kurulmadı. R06 mevcut geometri, açıklık ve kotları birebir korundu. Ara push yok. 087/119 kuzey alın taşını, 093/097 batı uç taşını destekler. 2m tane ve 3.2x2.4m derz tekrarları mevcut görünüm adayıdır; ölçülmüş plak çizelgesi veya fiziksel renk değildir. Geometri ve açıklıklar birebir korundu. Ara push yok. 093 fotoğrafı taş bandı destekler. 2m tane ve 3.2x2.4m derz tekrarı görünüm adayıdır; ölçülmüş taş modülü değildir. 34 ortak kenarda UV farkı en fazla 0.000000954. Geometri ve açıklıklar aynı; gün ışığında doku kontrastı düşük, fiziksel renk/ışık kalibrasyonu açık. Ara push yok. 051/052 merdiven perdesini, 097 batı taş kabuğunu destekler. 2m tane ve 3.2x2.4m derz tekrarı görsel aday; ölçülmüş plak çizelgesi değildir. Geometri ve açıklıklar aynı. Perde dokusu mevcut ışıkta düşük kontrastlı; fiziksel renk/ışık kabulü açık. Ara push yok. Resmî Mudam kafe fotoğrafları CF01/CF02 eklendi; CF01 açık taş zemini ve derzleri gösterir. 3.6m doku tekrarı ve yaklaşık 0.9m modül mevcut görsel adaydır, rölöve değildir. Mobilya/eser üretilmedi; geometri ve açıklıklar birebir aynı. 045 üst dolaşım taşı ve 103 planıyla koşullu malzeme sürekliliği adayıdır. 017/077 taş ailesini destekler; kesin köprü derz çizelgesini kanıtlamaz. 3.6m tekrar/0.9m modül ölçülmüş değildir. Kayıtlı ışıkta kontrast düşük; fiziksel renk kabulü açık. Geometri ve açıklıklar aynı. |
| P14 — Bütün kapı ve pencereler | Sürüyor | %40 | Üretilen: Giriş ve bölgesel iç kapılar, üst galeri geçişleri, iki plan bağlı galeri camı ve beş tarihî duvar alt penceresi mevcut. İki hareketli kanat, iki yan cam ve iki üst camın iki yüzüne toplam 48 cam tutucu profil ve 48 conta eklendi. Mevcut 9.234 mesh/curve değişmedi. Aynı kamera önce/sonra görseli ve 96 cam temas örneği incelendi.. Açık: 065 yan cephedeki iki alt pencerenin bina kenarı kaydı; diğer cephe açıklıkları, servis kapıları ve bütün donanımlar açık. A06 ilk iki pencere çevresinde kayıt çelişkisi sürüyor. 067 fotoğrafındaki cam–çerçeve çevresi esas alındı; kesit ve conta boyutları ölçülmemiş temsilî detaydır. Mekanizma ve bütün kapı/pencere paketi henüz tamamlanmadı. |
| P15 — Korkuluk ve metal birleşimler | Sürüyor | %90 | Üretilen: Okuma boşluğu, iki Grand Hall kolu, doğu spiral, batı/pavyon ve yaklaşım köprüleri korkuluk adayları kuruldu. 008/011/012 ile ince üç çubuk adayı değiştirildi:62 kapalı boru/levha/cam/kanal;160 taban desteği ve204 yaklaşım örneği geçti.. Açık: Gerçek cam ve metal kesitleri, sabitleme, ankraj ve montaj birleşimleri ölçülmedi. İç uçlar kolon yüzüne bağlı yerel aday;1,055/1,534m OSM farkı kaydedildi. Çap, aralık, kalınlık ve montaj ölçülmedi. |
| P16 — Zemin ve alt kat iç bitişleri | Sürüyor | %80 | Üretilen: Giriş/vestiyer bölgesi, alt galeri/fuaye, oditoryum ve galeri taş/ahşap yüzey adayları üretildi. 60 yeni parça ve iki döşemede sıfır kotuyla aynı biten yuva;441 destek örneği,52 kapı açısı ve204 yaklaşım kontrolü geçti. 014 ile28 parça,4 destek ve mevcut kapı pozu kontrolü;7263 görünür mesh denetlendi. 18–25cm yüksekteki hatalı tam boy profil kaldırıldı;2m statik geçişte189 ışın ve63 döşeme örneği geçti. 067 ile iki üst yüzün taş görünümü işlendi. Bütün sahnede hesaplanan geometri aynı; UV ve doku kontrolleri geçti. 28 yeni parça ve yedi yuva;29 hacim,119 ışın ve genel geometri kontrolü geçti. İki ray, sekiz başlık ve86 kapalı parça;194 ışın/80 bağlantı ve genel geometri kontrolü geçti. 54 duvarda 48 ortak köşe; 96 önce/sonra boşluk kontrolü geçti. Alt cephe boşluğu ve iki üst duvar bağlantısı; 561 yüzey, 20 birleşim ve 210 çatı taşma kontrolü. Yedi duvarın altı köşesi düzeltildi; 12 önce/sonra ışını, kapalı hacim ve bütün sahne denetimi geçti. İki duvar ucu komşu kaynak sınırına bağlandı; iki temas, 15 açık geçiş ışını ve bütün sahne denetimi geçti. Tavanda biten 37 çevre duvarı, zemin kat döşemesinin altına bağlandı. 296 önce/sonra ışın ve iki bina görünüşü kontrol edildi. Kullanıcının işaretlediği batı diyagonal bölmesi ve aynı yorumla eklenen doğu eşi kaldırıldı. 54 geçiş doğrultusu açık; zemin, tavan ve dış kabuk korundu. Batı galerinin planda çizili kısa giriş duvarı eklendi. Kuzey geçidini kapatan, üst odadan yanlış devam ettirilmiş R87 alt duvarı kaldırıldı. 15 duvar noktası ve iki girişte altı geçiş kontrolü geçti. İki galeri tavanının dokuz plan noktası mevcut giriş duvarlarının iç yüzüne bağlandı. En büyük yerel uyumsuzluk 0,337 m idi; kontrol edilen 18 alt/üst köşe artık aynı sınırda. Batı galeri duvarı ve iki girişin geçiş kontrolleri yeniden geçti. Alt batı galeri girişindeki kısa duvarın 5 cm geride kalan arka yüzü, komşu merdiven duvarıyla hizalandı. Ön yüz, giriş ucu ve kotlar korundu; alt galeri geçiş kontrolleri geçti. Batı zemin galerisinde mevcut duvar ile döşeme/tavan arasındaki yaklaşık 20 cm açıklık giderildi. Yalnız iki mevcut nesne genişletildi; 1.030 temas ve 108 giriş/güzergâh kontrolü geçti. Önce/sonra görüntüleri karşılaştırıldı. WC, vestiyer ve dükkânda 15 mevcut duvarın 11 ortak köşesi birleştirildi. Önceki 22 boşluk örneği kapandı; kaynak eksenleri, kalınlık, kotlar ve kapı uçları korundu. 44 köşe ve 96 servis geçiş/destek kontrolü geçti; yakın önce/sonra görüntüleri incelendi. Servis merdiveni altındaki üç mevcut duvarın iki köşesi birleştirildi. Önceki dört boşluk örneği kapandı; mevcut kapı kesisi ve merdiven korundu. Sekiz köşe örneği, genel geometri ve merdiven geçiş kontrolleri geçti; önce/sonra görüntüleri incelendi. Kafe–batı galeri geçidinde eksik üst örtü oluşturuldu. Aynı kamera karşılaştırmasında yatay yarık kapandı; zemindeki açık geçit korunuyor. Yeniden açılan sahnede önceki 132 örtüsüz örnek kapandı; genel geometri ve galeri geçiş kontrolleri geçti. Doğu galeri girişinin eksik üst örtüsü oluşturuldu. Önceki 81 örtüsüz örnek kapandı; geçitler ve yüksek atrium açıklığı korundu. Aynı kamera görsel karşılaştırması, sahne farkı, geometri ve geçiş kontrolleri geçti; altı merdiven ailesi taramasında yeni baş mesafesi engeli bulunmadı. Zemin katın iki galerisinde servis alanına bakan eksik uzun duvarlar kaynak plan konturunda oluşturuldu. Önceki 360 eksik yüzey örneği kapandı. Galeri ve servis geçişleri, genel geometri ve sahne farkı kontrolleri geçti; iki aynı kamera önce/sonra görüntüsü incelendi. 051 ve 052 fotoğraflarında görülen alt merdiven üst sahanlığı yanındaki eksik düşey taş perde eklendi. Aynı kamera önce/sonra görüntüsü incelendi. Yeni elemanın döşeme ve tavan temasları, alt kat geçişleri, alt merdiven regresyonu ve altı merdivenin baş mesafesi kontrol edildi. Küçük odanın yanlış iç bölmeleri kaldırıldı; dış sınırı ve köprü duvarları üst örtüye bağlandı. Cephe/döşeme kesişimleri, galeri/merdiven duvar birleşimi ve alt katın açık yan hacimleri düzeltildi. Önce/sonra görüntüleri ve yeniden açılan sahne kontrolleri kaydedildi. Cephe köşesi altındaki dönüş tamamlandı; beş pencere, girintileri ve tarihî duvar açıklıkları birlikte köşe içine taşındı. Üst köprünün iki galeriyle döşeme bağlantısı ve doğu duvar ucu üretildi. Alt fuaye ile oditoryum döşemesinin çakışan ön şeridi ayrıldı. Fuaye döşemesiyle bütünüyle örtüşen iki giriş döşemesi gizlendi; özgün nesneler ve girişlerin zemin kapanışı korundu. Zemin katta doğu dolaşım alanı, batı kafe ve küçük oda birleşimindeki üst üste binen döşeme hacimleri ayrıldı. Tamamen yinelenen bağlantı eşiği gizlendi; döşeme kapsamı korundu. Batı üst kat dönüş tavanındaki yinelenen örtü gizlendi; kafe tavanı ile ön servis örtüsünün örtüşen hacmi ayrıldı. Oditoryumun 230 mevcut ahşap panel, kapı ve çevre parçasına düşey damar dokusu ve yüz yönüne göre UV uygulandı. Akustik delikler, derzler ve açıklıklar değişmedi. Oditoryum zemin, sahne, geçiş basamakları ve taş ayaklarda 51 mevcut nesnenin 318 nötr yüzüne taş tane malzemesi ve metrik UV uygulandı.. Açık: Oditoryum128 koltuk adayı mimar/LCB tablosu ve fotoğraf arka sırasıyla destekli; Kamu Yapıları120 ve LCB metni130 değerlerinin kapsam/tarih farkı açık. Eksik sabit donatılar, alt kat aydınlatması ve tam yüzey kaynak listesi gerekiyor. Bölünme, yuva derinliği, malzeme ve ızgara adımı aday; gerçek kapı mekanizması doğrulanmadı. Boyut,ürün,işlev,delik deseni ve tam hareket mekanizması açık. Eski sabit alt profil hatası R64 kapsamına alındı. Geniş2,2m tarama sağ panele çarpar; hareketli kanatlar bu statik testten ayrı. Gerçek kapı mekanizması ve eşik ölçüsü açık. 900mm hücre,1,2mm derz,yön ve desen aday; fotoğraf dizimi birebir izlenmedi. Yedi konum ve180mm çap kısmi aday; tam yerleşim,ürün ve fotometri doğrulanmadı. Sayı, konum, ürün kesiti ve20 derece yönlenme kısmi aday; tam aydınlatma planı ve fotometri açık. Duvar ölçüleri koşullu; diğer duvarlar ve yan salon birleşimleri açık. Kaynak planlara bağlı yerel düzeltme; kesin kalınlık ve kotlar koşullu. Genel duvar kabulü açık. İç tavan kotu değişmedi; duvar/döşeme kesin kesiti ve kat planları arasındaki yerel farklar koşullu. Kalıcı duvar olduğu doğrulanmayan iki aday kaldırıldı. İdari/teknik hacimler ve kesin çatı biçimi kabulü açık. Merdiven yanı ikinci galeri işareti ile +1 Studio/servis/asansör çevresinin bütün kat ilişkileri açık; tüm ekran görüntüleri çözüldü denmedi. Bu yerel çizim uzlaştırması ölçülmüş imalat geometrisi değildir. Gerçek giriş boşlukları ve fotoğraf 026’daki yüksek merdiven yanı geçidi korunur. +1 Studio/servis/asansör çevresinin bütün kat ilişkileri ve diğer kabuk birleşimleri açık. Bütün bina kabulü yok. Diğer kabuk birleşimleri ve kat ilişkileri kaynaklarla karşılaştırılıyor; komşudan devralınan kalınlık ve kotlar ölçülmemiş adaylardır. Bütün bina tamamlanmadı. Diğer dar duvar–döşeme–tavan temasları kaynaklarla karşılaştırılıyor; mevcut kotlar ve kalınlıklar ölçülmemiş adaylardır. Bütün bina tamamlanmadı. Diğer kabuk birleşimleri, merdiven/kapı detayları ve bütünleşik kaynak kontrolü açık; ölçülmemiş kalınlık ve kotlar aday. Öncelik büyük kabuk sorunları. Doğu merdiveni–duvar birleşimi ve kalan büyük açıklıklar bitmeden köşe veya malzeme detayına geçilmez. Örtü kotu mevcut 4,35 m galeri tavanı adayıdır; ölçülmüş uygulama detayı değildir. Öncelik büyük kabuk sorunları. Kalan büyük duvar/zemin/çatı açıklıkları bitmeden köşe veya malzeme detayına geçilmez. Örtü kotu mevcut 4,35 m galeri tavanı adayıdır; ölçülmüş uygulama detayı değildir. Bütün bina ve kullanıcının tüm ekran görüntüleri henüz kabul edilmedi. Duvar kalınlığı mevcut kaynak konturları arasında uzlaştırılmış adaydır; kotlar ölçülmüş değildir. Öncelik kalan büyük kabuk sorunlarıdır. Elemanın varlığı fotoğrafta görülüyor; yerleşimi mevcut merdiven üst kiriş hattına hizalı adaydır. 0,28 m kalınlık ve mevcut kol genişliği ölçülmüş değildir. Plan 104 bu ayrıntıyı göstermiyor. Bu paket yalnız bir temsilî mimari elemandır; bütün bina veya taşıyıcı sistem kabulü değildir. Büyük kabuk sorunları ve açık üretim işleri önceliğini korur. Bina bütünü ve bütün ölçüler kabul edilmiş değildir. Alt cephe ilk pencere/köşe kayıt uyumu ve ölçülmemiş kalınlıklar açıktır; kapı temsilleri ürün doğrulaması değildir. Fotoğraf 004/116 ve plan 103 esas alındı. Pencere dizisinin 2,459 m kaydırılması mevcut model köşesine göre türetilmiştir; 0,12 m kenar payı ve diğer miras boyutları ölçülü rölöve değildir. Bütün bina kabulü ve kalan üretim işleri açıktır. 15.436 örneğin 306sında önce çift üst yüzey vardı; sonra tüm örneklerde tek yüzey var. Üç mevcut nesne değişti, yeni nesne veya ölçü yok. Bütün bina kabulü değildir. Altı mevcut nesne değişti; yeni nesne veya mimari ölçü yok. 47.667 konumun 1.569unda önce çift yüzey vardı; sonra tüm örneklerde tek üst yüzey var. Bütün bina kabulü değildir. İki mevcut nesne değişti. 7.178 konumun 152sinde önce çift üst yüzey vardı; sonra tamamında tek yüzey var. Örtü kapsamı korundu; bütün bina kabulü değildir. 073 fotoğrafı ahşap sınıfı ve düşey damar yönünü destekler. 1.2x2.4m doku tekrarı, ağaç türü, damar şekli ve renk ölçülmüş değildir. İnceleme ışıkları yalnız render için eklendi; sahneye kaydedilmedi. Ara push yok. 071/073 fotoğrafları açık taş yüzey ailesini destekler. 2m doku tekrarı, renk ve taş türü ölçülmüş değildir; yeni derz çizelgesi üretilmedi. Tane etkisi oda uzaklığında hafiftir. Geometri, basamak kenarları ve açıklıklar birebir korundu. Ara push yok. |
| P17 — Üst kat iç bitişleri | Sürüyor | %70 | Üretilen: Okuma odası, eğimli tavan ve24 kollu ışık; iki üst galeri, Studio, asansör sahanlığı; Grand Hall20 silindir ışık işlendi. 54 duvarda 48 ortak köşe; 96 önce/sonra boşluk kontrolü geçti. Alt cephe boşluğu ve iki üst duvar bağlantısı; 561 yüzey, 20 birleşim ve 210 çatı taşma kontrolü. İki kesintisiz duvar gövdesi; 576 yüzey/sınır ve 90 geçiş testi. Beş duvar, dört köşe ve sekiz önce/sonra boşluk kontrolü. İki duvar ucu komşu kaynak sınırına bağlandı; iki temas, 15 açık geçiş ışını ve bütün sahne denetimi geçti. Eski kare kesicinin sildiği iki çatı köşesi geri getirildi; 342 örtü ve 112 kuzey koruma örneği geçti. 104 planındaki yan hacimlere 31 duvar/döşeme/tavan bileşeni; 405 sınır ve altı geçiş kontrolü geçti. Mevcut zeminin eksik yan camı, üst örtüsü ve iç duvarı eklendi; 312 alt/üst ve 156 yan kapanış örneği geçti. Eski düz uzantı kaldırıldı; PDF kapısına dönen mevcut koridorun duvar ve örtüsü eklendi. 571 sık örnek ve dolaşım denetimi geçti. Eksik alt/üst döşeme ve çatı eklendi; PDF oda sınırı ve açık bağlantısı kuruldu. 29 bölge, 97.080 sık örnek ve 218.136 çok kotlu ışın kontrol edildi. R96: Küçük batı galerisini kesen iki eski zemin kat duvarı üst döşeme altında sonlandırıldı. 2016 iç oda ile 103 merdiven kabuğunun farklı ölçekleri uzlaştırıldı; iki iç duvar kopyası kaldırıldı, kafe üzerine taşan +1 döşemesi daraltıldı. Okuma alanının doğusundaki eksik oda, servis merdiveni sınırı ve üst asansör kuyusu yüzleri kaynak planıyla üretildi. Kafe çatısına fotoğrafta görünen alt çubuk sistemi aday ölçülerle eklendi. Servis merdivenine 24 basamak/sahanlık parçası eklendi; yolu kesen alt kat tavanı ve giriş duvarı yerel olarak açıldı. Yedi kuyu duvarı iki kat arasında devam ettirildi. 110 yerel kontrol ve önceki duvar/cam düzeltmelerinin gerileme kontrolü geçti. Okuma odası–doğu servis odası bağlantısının planda çizili fakat eksik bırakılmış iki yan duvarı eklendi. 15 eksik duvar probu düzeldi; dokuz geçiş ve sekiz zemin/tavan kontrolü geçti. Diğer mevcut geometri değişmedi. Üst servis odası ve merdiven kuyusunda 14 duvarın 12 dış köşesi birleştirildi. Önceden açık olan 10 köşe probu kapandı; iç plan çizgileri ve açıklıklar korundu. Servis merdiveninin 110 kontrolü yeniden geçti. Batı üst galeriye taşan dört duvar/tavan parçası mevcut plan sınırına kırpıldı. Servis odası birleşimindeki çıkıntı ve merdiven dönüşündeki yanlış tavan uzantısı kaldırıldı. Kapı ve koridor geçişleri korundu. Okuma odasının eski döşeme kenarı mevcut PDF2016 duvar konturuyla uzlaştırıldı; duvar dibindeki açık şerit giderildi. Merkez boşluk ve üç geçit korundu. 1.313 döşeme/boşluk ve 36 geçiş kontrolü geçti; önce/sonra görüntüleri incelendi. İki köprü bağlantı döşemesinin mevcut galeri eşikleriyle çakışan hacimleri çıkarıldı. Yeni parçalar yalnız eksik yan şeritlerde kalıyor; eski eşik ve zemin yüzeyi korunuyor. Üst galerilerin dört eşiğinde ve batı dönüş döşemesinde yinelenen yüzeyler ayrıldı. Tamamen diğer döşemenin içinde kalan bir dönüş parçası gizlendi; açıklıklar ve bitmiş zemin kotu korundu.. Açık: Üst kat fotoğraflarının kanat kimlikleri, kesin ölçüler, sabit donatılar ve galeri aydınlatma detayları açık. Duvar ölçüleri koşullu; diğer duvarlar ve yan salon birleşimleri açık. Mevcut kaynak sınırları korundu; kalınlık/kotlar koşullu. Genel duvar kabulü açık. Kaynak planlara bağlı yerel düzeltme; kesin kalınlık ve kotlar koşullu. Genel duvar kabulü açık. Mevcut kotlar korundu; genel duvar–zemin–çatı kapanışı sürüyor. Gerçek okuma boşluğu korundu. Şematik plan çizgileri, mevcut aday kalınlık ve fuaye kotları kullanıldı. Asansör donanımı ve kapı detayları yapılmadı. 102/066/097 kaynakları; mevcut 3,2 m başlık yüksekliği aday olarak korundu. Cam bölüntü ve ürün ayrıntıları ertelendi. PDF ile ziyaretçi şeması arasındaki iç sınır farkı kayıtlı; kesin yeniden ölçüm değildir. Malzeme ve ayrıntı ölçüleri aday. PDF ve ziyaretçi şeması farklı; kot, kalınlık ve yerel çatı eğimi kesinleşmedi. Bütün bina kabulü açık. Yerel plan kaydı ve çelik çubuk ölçüleri adaydır. Servis merdiveni basamakları, bütün katlar arasında devamlılık ve kesin imalat ölçüleri açık. Bina tamamlanmış sayılmadı. Plan sembolündeki 24 bölme ölçülmüş rıht sayısı değildir. Dönüş yönü, rıht yüksekliği ve sahanlık aday; korkuluk ve alt kata devam ilişkisi açık. Bütün bina kabulü yapılmadı. +1 Studio, asansör ve diğer katlar arası kabuk ilişkileri hâlâ inceleniyor. Geçit duvarının yüksekliği ve kalınlığı aday; bütün bina kabulü yok. Bütün bina kabulü yok. Diğer üst kat duvar/örtü birleşimleri ve katlar arası devamlılık kontrolü sürüyor; ölçülmemiş kalınlık ve kotlar aday. Bütün bina kabulü yok. Diğer kabuk birleşimleri ve kat ilişkileri kaynaklarla karşılaştırılmaya devam ediyor; ölçülmemiş kotlar ve kalınlıklar aday. Bütün bina tamamlanmadı. Diğer küçük odaların üst örtüleri, kalan çelik/cam birleşimleri ve bina son kontrolü açık; kesin kot ve malzeme ölçüleri hâlâ aday. R117 bağlantılarına ait düzeltmedir; 62 önceki çift yüzey örneği giderildi, 78 son örnekte tek zemin yüzeyi var. Yeni mimari ölçü eklenmedi. Bütün bina kabulü değildir. 1.364 yerel örneğin 716sında önce çift/üçlü yüzey vardı; sonra tüm örneklerde tek yüzey var. Beş mevcut nesne değişti, yeni nesne ve ölçü eklenmedi. Bütün bina kabulü değildir. |
| P18 — Arazi tarihî duvar ve peyzaj | Sürüyor | %80 | Üretilen: İlk hendek/tarihî duvar sınırları, köprü/yaklaşım yolları,19 OSM ağaç konumu ve tarihî taş/çim görünümü mevcut. 19 OSM konumu korunarak 38 dal/yaprak mesh’i üretildi;204 yaklaşım kontrolü geçti. 008/011/012 ile ince üç çubuk adayı değiştirildi:62 kapalı boru/levha/cam/kanal;160 taban desteği ve204 yaklaşım örneği geçti. Mevcut döşemede50 yüz: koyu taş ve açık kenar bandı. Yüzey/hacim karşılaştırması ve204 yaklaşım örneği geçti. 013 yakın çekimiyle R59 şaşırtmalı örgüsü değiştirildi;17 yüz ve bütün sahnede geometri eşitliği kontrolü geçti. İki OSM duvar zinciri: altı duvar ve zemin.30 duvar/440 zemin ışını ve pavyon kesişim kontrolü geçti. 28 mevcut çevre parçasında tarihî taş ve hendek çimi için renk, normal ve pürüzlülük dokuları yenilendi. Arşiv OSM verisinde iğne yapraklı olarak kayıtlı yedi ağacın geniş yapraklı taçları değiştirildi. Yedi dal ve yedi iğne yaprak ağı üretildi; eski 14 taç parçası gizlendi, gövdeler ve konumlar korundu. Arşiv OSM 759811369 karma ağaçlık sınırı mevcut park zeminine işlendi. 421.08m² bitkili zemin sert kaplamadan ayrıldı; mevcut 4m aday yol koridorları korundu. Bir zemin değişti, bir kapalı zemin nesnesi eklendi. Üç arşiv yol güzergâhı mevcut park zemininin koordinatlı kaplama dokusuna işlendi: 83345393 ve 49910981 taş döşeme, 50643005 küçük taş kaplama sınıfını taşır. İki gömülü 4096px doku ve tek malzeme kullanılır.. Açık: Diğer hendek kolları, değişen kotlar, tarihî açıklıklar, destekler ve bitki/yol sınırlarının tamamı çözülmedi. Arazi düz kot ve OSM çizgilerinden türetilmiş aday. Tür, yükseklik, yaprak ve dallanma düzeni temsilî; tekil fotoğraf ağacı eşlemesi yok. İç uçlar kolon yüzüne bağlı yerel aday;1,055/1,534m OSM farkı kaydedildi. Çap, aralık, kalınlık ve montaj ölçülmedi. Taş modülü, derz, renk, yön ve0,65m bant genişliği ölçülmemiş görünüm adayları. Örgü tipi fotoğraftan;200×50mm modül,derz,renk ve yön aday. Genişlik ve düz kotlar R35 adayı; arazi ölçümü değil. Diğer kollar ve tarihî ayrıntılar açık. Geometri ve UV değişmedi. 4x3m tekrar önceki aday ölçüdür; tekil taş, bitki türü ve fiziksel renk doğrulaması yok. Bina veya tüm çevre tamamlanmış değildir. Ağaç türü, 8m yükseklik, 2.2m taç yarıçapı, dallanma ve renk ölçülmüş değildir. Bu yedi ağacın sınıf düzeltmesi bütün çevrenin kabulü değildir. Ara push yapılmayacak; doğrulanmış toplam kapsam %90 hedefine kadar yerel üretim sürecek. OSM sınırı rölöve değildir. Düz arazi kotu, yol genişliği ve çim görünümü temsilîdir; diğer peyzaj sınırları, bitki dağılımı ve tarihî ayrıntılar açık. V001/v002 ortak köşe ağ bağlantısı nedeniyle reddedildi; v003 ayrı kapalı adalar kullanır. Ara push yok. Mevcut zemin geometrisi birebir korundu. Yol genişliği 4m aday; 600x300mm ve160x120mm görsel modüller, renk/derz düzeni ölçülmedi. V001–v003 yüz bölme adayları geometri/UV hatası nedeniyle reddedildi; v004 kabul edildi. Ara push yok. |
| P19 — Malzeme ve ışık | Sürüyor | %70 | Üretilen: Taş/ahşap/mineral, metal, cam ve çevre yüzey adayları; genel gün ışığı ve bölgesel aydınlatma geometrisi mevcut. 19 OSM konumu korunarak 38 dal/yaprak mesh’i üretildi;204 yaklaşım kontrolü geçti. Mevcut döşemede50 yüz: koyu taş ve açık kenar bandı. Yüzey/hacim karşılaştırması ve204 yaklaşım örneği geçti. 20 nesne ve175 yüzün malzeme/UV adayı;7.942 nesnenin hesaplanan geometrisi değişmedi. Altı yuva ve24 kapalı parça;102 ışın ve7235 görünür mesh kontrolü geçti. 013 yakın çekimiyle R59 şaşırtmalı örgüsü değiştirildi;17 yüz ve bütün sahnede geometri eşitliği kontrolü geçti. 067/068 ile 130 yeni parça; 146 bağlantı ve 32 lens açıklığı kontrolü geçti. 7.634 görünür mesh. 067 ile iki üst yüzün taş görünümü işlendi. Bütün sahnede hesaplanan geometri aynı; UV ve doku kontrolleri geçti. 28 yeni parça ve yedi yuva;29 hacim,119 ışın ve genel geometri kontrolü geçti. İki ray, sekiz başlık ve86 kapalı parça;194 ışın/80 bağlantı ve genel geometri kontrolü geçti. 28 mevcut çevre parçasında tarihî taş ve hendek çimi için renk, normal ve pürüzlülük dokuları yenilendi. Sonradan üretilen 12 kabuk parçasındaki 115 yüz mevcut taş duvar ve taş döşeme ailelerine bağlandı. Sekiz duvarın düşey yüzleri ve dört döşeme bağlantısının üst yüzleri metrik UV aldı. Okuma alanının sekiz eğimli tavanı ve doğu spiral merdiveninin basamak, çekirdek, kenar ve komşu taş yüzeylerinde 50 mevcut nesnenin 3484 yüzüne taş malzemesi ve metrik UV uygulandı. Oditoryumun 230 mevcut ahşap panel, kapı ve çevre parçasına düşey damar dokusu ve yüz yönüne göre UV uygulandı. Akustik delikler, derzler ve açıklıklar değişmedi. Oditoryum zemin, sahne, geçiş basamakları ve taş ayaklarda 51 mevcut nesnenin 318 nötr yüzüne taş tane malzemesi ve metrik UV uygulandı. Batı cam merdiveninin iki kolu, sahanlıkları ve taş iç duvarlarında 41 mevcut nesnenin 249 yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. Giriş ile doğu/batı galeri dolaşımının üç mevcut döşemesinde yaklaşık 580m² üst yüzey, ortak taş plak ailesine ve metrik UV düzenine bağlandı. Grand Hall ana duvarları ve galeri dış yüzlerinde dokuz mevcut nesnenin 58 nötr yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. Doğu bahçe galerisinin yaklaşık 334m² mevcut zemininin üst yüzü taş plak malzemesine ve metrik UV düzenine bağlandı. Batı merdiven giriş iç duvarı ve kafe arka duvarı/başlığındaki üç mevcut nesnenin 18 nötr yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. Alt fuaye kuzey duvarının yaklaşık 169m² düşey yüzeyine taş derzi ve metrik UV uygulandı; yatay kenarlarda taş tane ailesi kullanıldı. Alt fuayenin yaklaşık 321m² tavan altı ve kavisli alın yüzeyinde 155 yüze taş tane malzemesi ve metrik UV uygulandı. Kuzey cam çatı doğu taş alın/alt duvarı ve batı uç duvarındaki üç mevcut nesnenin 19 nötr yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. Batı kavisli cam cephenin altındaki 18 mevcut taş duvar parçasının 144 yüzüne taş malzemesi ve kavis boyunca sürekli metrik UV uygulandı. Batı dönüşündeki beş mevcut taş duvar ve alt fuaye merdiven perdesinin toplam 36 nötr yüzüne taş malzemesi ve metrik UV uygulandı. Batı kafenin yaklaşık 288m² mevcut döşemesindeki 33 üst yüze taş malzemesi ve metrik UV uygulandı. Üst köprünün mevcut döşemesindeki iki üst yüze komşu taş ailesi ve metrik UV uygulandı; yalnız P05_FLOOR_LP1_BRIDGE değişti.. Açık: Renk, ışık gücü, armatür fotometrisi ve malzeme ürünleri kalibre değil; görünüm fiziksel ölçüm değildir. Tür, yükseklik, yaprak ve dallanma düzeni temsilî; tekil fotoğraf ağacı eşlemesi yok. Taş modülü, derz, renk, yön ve0,65m bant genişliği ölçülmemiş görünüm adayları. Renk, derz, malzeme bileşimi ve çizgisel yüzey derinliği ölçülmedi; saçak kotu koşullu. Fotoğraf homografisi düşük güvenli: dışarıda bırakma hatası188,89px. Çap, profil, kot ve tam armatür sayısı doğrulanmadı. Örgü tipi fotoğraftan;200×50mm modül,derz,renk ve yön aday. 32 adet sekiz göze uygulanan tekrar adayı; çap, kot, ürün ve fotometri doğrulanmadı. 900mm hücre,1,2mm derz,yön ve desen aday; fotoğraf dizimi birebir izlenmedi. Yedi konum ve180mm çap kısmi aday; tam yerleşim,ürün ve fotometri doğrulanmadı. Sayı, konum, ürün kesiti ve20 derece yönlenme kısmi aday; tam aydınlatma planı ve fotometri açık. Geometri ve UV değişmedi. 4x3m tekrar önceki aday ölçüdür; tekil taş, bitki türü ve fiziksel renk doğrulaması yok. Bina veya tüm çevre tamamlanmış değildir. Geometri, açıklıklar ve kotlar değişmedi. 3.2x2.4m duvar ve 3.6x3.6m döşeme tekrarları önceki görünüm adaylarıdır; ölçülmüş derz veya fiziksel renk kabulü değildir. Ara push yok; kapsam puanı değiştirilmedi. 015/016 ve 041/043 fotoğrafları taş yüzey sınıfını destekler. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; ölçülmüş panel, renk veya fiziksel kalibrasyon değildir. Geometri birebir korundu. Ara push yok. 073 fotoğrafı ahşap sınıfı ve düşey damar yönünü destekler. 1.2x2.4m doku tekrarı, ağaç türü, damar şekli ve renk ölçülmüş değildir. İnceleme ışıkları yalnız render için eklendi; sahneye kaydedilmedi. Ara push yok. 071/073 fotoğrafları açık taş yüzey ailesini destekler. 2m doku tekrarı, renk ve taş türü ölçülmüş değildir; yeni derz çizelgesi üretilmedi. Tane etkisi oda uzaklığında hafiftir. Geometri, basamak kenarları ve açıklıklar birebir korundu. Ara push yok. 066 fotoğrafı taş basamak ve derzli taş duvar ailesini destekler. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; kesin taş modülü, renk ve metrik kamera çözülmedi. Geometri ve açıklıklar birebir korundu. Ara push yok. 017/026/070/077 taş yüzey sınıfını destekler; 0.9m plak, 3.6m tekrar ve kanonik yön mevcut R43 görünüm adayıdır, ölçülmüş derz dizimi değildir. Geometri ve açıklıklar birebir korundu. Ara push yok. 026/034/087/119 kaynakları taş yüzey sınıfını destekler. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; ölçülmüş panel çizelgesi ve renk kalibrasyonu değildir. Galeri iç beyaz yüzleri, geometri ve gerçek açıklıklar korundu. Ara push yok. 041/043 taş yüzey ailesini destekler. 0.9m plak ve 3.6m tekrar mevcut R43 görünüm adayıdır; ölçülmüş derz çizelgesi değildir. Geometri ve açıklıklar birebir korundu. Ara push yok. 066/097 giriş taş duvarını, 093 kafe arkasındaki taş sınırı destekler. Mevcut R82/R83 kabuk adaylarının ölçü ve konum belirsizliği sürer. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; ölçülmüş panel çizelgesi veya renk değildir. Geometri ve giriş açıklığı korundu. Ara push yok. 051/055 alt fuayenin taş yüzey ailesini destekler. R72 sınır/kot adayları değişmedi. 2m tane ve 3.2x2.4m derz tekrarları ölçülmüş panel çizelgesi değildir. Geometri birebir korundu. Ara push yok. 051/055 taş tavan ailesini destekler. 2m tane tekrarı görsel adaydır; fotoğraftaki tekil plak derzleri yeniden kurulmadı. R06 mevcut geometri, açıklık ve kotları birebir korundu. Ara push yok. 087/119 kuzey alın taşını, 093/097 batı uç taşını destekler. 2m tane ve 3.2x2.4m derz tekrarları mevcut görünüm adayıdır; ölçülmüş plak çizelgesi veya fiziksel renk değildir. Geometri ve açıklıklar birebir korundu. Ara push yok. 093 fotoğrafı taş bandı destekler. 2m tane ve 3.2x2.4m derz tekrarı görünüm adayıdır; ölçülmüş taş modülü değildir. 34 ortak kenarda UV farkı en fazla 0.000000954. Geometri ve açıklıklar aynı; gün ışığında doku kontrastı düşük, fiziksel renk/ışık kalibrasyonu açık. Ara push yok. 051/052 merdiven perdesini, 097 batı taş kabuğunu destekler. 2m tane ve 3.2x2.4m derz tekrarı görsel aday; ölçülmüş plak çizelgesi değildir. Geometri ve açıklıklar aynı. Perde dokusu mevcut ışıkta düşük kontrastlı; fiziksel renk/ışık kabulü açık. Ara push yok. Resmî Mudam kafe fotoğrafları CF01/CF02 eklendi; CF01 açık taş zemini ve derzleri gösterir. 3.6m doku tekrarı ve yaklaşık 0.9m modül mevcut görsel adaydır, rölöve değildir. Mobilya/eser üretilmedi; geometri ve açıklıklar birebir aynı. 045 üst dolaşım taşı ve 103 planıyla koşullu malzeme sürekliliği adayıdır. 017/077 taş ailesini destekler; kesin köprü derz çizelgesini kanıtlamaz. 3.6m tekrar/0.9m modül ölçülmüş değildir. Kayıtlı ışıkta kontrast düşük; fiziksel renk kabulü açık. Geometri ve açıklıklar aynı. |
| P20 — Kat ayırma ve kesit | Sürüyor | %90 | Açık: Üç kat kot aralığı, yatay/düşey canlı kesit, kapalı halka kapakları, parça-kaynak seçimi ve tek parça görünümü mevcut. P20_KESIT_KAPAKLARI.md kayıtlı testleri kapsar; açık sınırlar doldurulmaz, tüm kot kombinasyonları kabul edilmedi. Kat kotları koşullu; bina kabulü yapılmadı. |
| P21 — Hafif türev ve dışa aktarma | Sürüyor | %70 | Açık: 8478 mesh / 3696922 üçgen GLB aktarımı denetlendi; hedef motor ve sadeleştirme açık. |
| P22 — Teslim doğrulaması | Sürüyor | %40 | Üretilen: Sahneler yeniden açılıyor; bölgesel geometri, dolaşım, kaynak ve render kayıtları tutuluyor. 18–25cm yüksekteki hatalı tam boy profil kaldırıldı;2m statik geçişte189 ışın ve63 döşeme örneği geçti.. Açık: Son bütünleşik bina kabulü, nihai kaynak/varsayım özeti, teslim paketi ve hedef motor kontrolü henüz tamamlanmadı. Geniş2,2m tarama sağ panele çarpar; hareketli kanatlar bu statik testten ayrı. Gerçek kapı mekanizması ve eşik ölçüsü açık. |


## Kontrol sonuçları

R92 **kullanıcı düzeltmesi**: zemin kat batı galerisinin işaretlenen bağımsız diyagonal bölmesi ve doğudaki eşi kaldırıldı. 54 geçiş ışını engelsiz; döşeme ve tavanlar korundu. [Önce/sonra](reports/R92_KONTROL_RAPORU.md). R91'de batı uç duvarının eski üst kotları da mevcut cam çatıya bağlandı; 597 birleşim kontrolü geçti. Bu iki paket geometri değişikliğidir.

R90 **geometri üretimi**: giriş yönündeki yüksek atriumun çerçevesiz tek cam temsili kaldırılarak aynı açıklıkta 12 cam panel ve 9 metal çerçeve üretildi. Yeni sahne yeniden açıldı; 21 kapalı parça, 51.914 yerel yüzey örneği ve bütün sahne/fark denetimi geçti. [Önce–sonra ve kaynak sınırları](reports/R90_KONTROL_RAPORU.md). Profil ölçüleri aday; bütün bina tamamlanmadı.

R89 üst galeri devam kontrolü: 9.558 çatı–duvar çevre örneğinde kaçış yok; 71 ışıklık kontrol doğrultusu açık. Dört yeni iç render kaynaklarla incelendi. [Renderlar ve sınırlar](reports/R89_YEREL_CATI_KONTROLU.md). Geometri sürümü ve yüzdeler değişmedi; eksik kaynaklı idari/teknik hacimler açık.

R89 ek çatı kontrolü: 24 ana çatı/fener/tepe yüzeyinde 330.913 ve 228 yan çatı camının kenar bantlarında 256.816 geçerli yerel örnek incelendi; örtü kaybı bulunmadı. Saçak altındaki 25 aday, geçiş camının kot aralığının dışında; rastgele duvar eklenmedi. Sahne ve GLB değişmedi, ilerleme yüzdeleri artırılmadı. [Yerel çatı kontrolü ve sınırları](reports/R89_YEREL_CATI_KONTROLU.md).

P07: 164 yeni mesh / 67 kapalı hacim kontrol edildi; sıfır alanlı yüz yok. Kapı geçişi üç yükseklikte açık. Üç kamera aktarımı 0,009 px altında. [P07 yeniden açma kontrolü](reports/P07_verification.json).

P09: üç başlangıç basamağı, kot katmanları, yukarı/aşağı yönlerinin ayrılması ve paketli fotoğraflar yeni Blender sürecinde denetlendi. [P09 yeniden açma kontrolü](reports/P09_verification.json).

Üst merdivenin eski P05 kılavuz yönü tersti; düzeltildi. 049/050 ile ilişkili aşağı merdiven ayrı tutuluyor. Ziyaretçi şemasının çizgi sayısı gerçek rıht sayısı sayılmadı.

## Ölçü durumu

Ana kabuk henüz bütün bina düzeyinde kabul edilmedi. OSM uyum RMS'si yaklaşık 1,02 m, iki bağımsız kontrol RMS'si 1,91 m; source-plan ölçeği bu sınırlarla kullanılıyor. Kat kotları, saçak, profil ve kalınlık parametreleri koşullu. Sahnedeki büyük bölüm `90_UNCERTAIN_OR_PROXY` altında; fiziksel imalat doğruluğu iddiası yok.

## Sıradaki üretim

Zemin/alt galeri iç duvar ve açıklıkları, kaynaklarla henüz çözülememiş cephe nişleri, taş/derz ve aydınlatma, arazi/historik duvar bağlamı, dışa aktarım optimizasyonu ve bütün bina taraması. Üst/alt Grand Hall merdivenleri, doğu spiral ve batı merdiven bölgesel olarak üretildi; pavyon merdiveni R25'te açıkça temsilî. Yeni paketlerde eski kaynak/ölçü belirsizlikleri kaybolmaz. Rutin onay beklenmez.

Önceki P03/P04/P05/P06/P07 sahneleri `scenes` içinde sürümlü olarak korunur. `build_mudam.py` eski ve kullanılmaz. Yeni betikler mevcut sürümün üzerine yazmayı reddeder.

[Çatı üretim raporu](reports/P10_P11_CATI_RAPORU.md): 3.203 kapalı hacim ve 380 çubuk bağlantısı denetlendi. Pavyon/okuma feneri panelizasyonu, ana iç gergi/gölgeleme ve batı panel düzlemselliği açık.

[Giriş detay raporu](reports/P12_GIRIS_DETAY_RAPORU.md): kapı mekanizması kesinleşmedi; görünen düz cam kanatlar ve donanımlar ayrı üretildi. Rutin onay beklenmez.

[Model-plan kesit kontrolü](PLAN_KONTROL.html) · [Okuma alanı raporu](reports/P15_P17_OKUMA_BOSLUGU_RAPORU.md) · [Malzeme / dışa aktarma raporu](reports/P19_P21_ONIZLEME_RAPORU.md).

[R02 Grand Hall geçit düzeltmesi](reports/R02_GH_GECISI_RAPORU.md): kesintisiz eski cam kaldırıldı, geçide taşan üç etüt duvarı yerel kırpıldı. 15 ışın testi bütün görünür meshleri kapsar; tam oda ve çatı birleşimi kabulü açık.

## R03 üst merdiven ayağı

R03 v003: 022/023 kaynaklı kıvrımlı cam dönüş, yuvarlak küpeşte, taban kanalı, gömme taş alan ve armatür adayı eklendi. Üç başlangıç basamağının küçük sınır kesişimleri onarıldı; kaynak nesneler korundu. 20 kapalı hacim, 65 destek örneği, 12 girinti ışını ve 15 geçit ışını kontrolü geçti. Güncel GLB 7.33 MB, 3595 mesh ve 69812 üçgen.

Tam üst kol, üst sahanlık, eğimli korkuluk devamı ve bütün detay ölçülerinin kesinleştirilmesi açık. [R03 kaynak / varsayım / kontrol raporu](reports/R03_MERDIVEN_DONUS_RAPORU.md).

## R04 / R05 — Grand Hall merdivenleri
Üst kol R04 v003 ve alt kol R05 v004 çalışma adayları eklendi. Alt katta 114/055 fotoğraflarıyla kıvrımlı döşeme uzantısı ve üçgen köşe boşluğu düzeltildi; bütün yerel dolaşım kontrolleri yeniden geçti. Gerçek rıht sayıları, kesit kalınlıkları ve detay ölçüleri açık. [R04 raporu](reports/R04_UST_MERDIVEN_RAPORU.md) · [R05 raporu](reports/R05_ALT_MERDIVEN_RAPORU.md).

R06 alt fuaye tavanı ve R07 merdiven arkası düz taş duvarları eklendi; yeni sahnede iki merdiven ve önceki açıklık kontrolleri tekrar geçti. [R06](reports/R06_ALT_FUAYE_RAPORU.md) · [R07](reports/R07_MERDIVEN_BOSLUGU_RAPORU.md).

R08/R09: 015/016 ile 24 kollu armatür ve eğimli tavan; PDF103 ile oda iç çevresi, üç geçiş ve döşeme bağlantıları eklendi. Yeniden açma, açıklık/baş mesafesi ve günışığı kontrolleri geçti. [R08](reports/R08_OKUMA_TAVANI_RAPORU.md) · [R09](reports/R09_OKUMA_MEKANI_RAPORU.md). Doğu spiral merdiveni için kaynak uyuşmazlığı inceleniyor.

## 23:35 UTC civarı — R10 doğu spiral
041–044, 102/103 ve PDF sembolünden 34 rıht/540 derece koşullu aday üretildi. Yön, Boolean birleşimi ve bütün çevrede eski duvar engeli üç ayrı kontrolde düzeltilerek v004 kaydedildi. Baş mesafesi/destek/geçiş ve önceki üst merdiven kontrolleri geçti. Bahçe uç camı ve çatı birleşimi sıradaki iş; tam bina hâlâ sürüyor.

## 23:43 UTC civarı — R11/R12
Doğu uç cam cephe adayı, çatıya bağlı taş alın duvarı ve açık pavyon bağlantısı üretildi. Üst çatı şeridi açık belirsizlik. Batıdaki 108 cam panel düzleştirildi; maksimum köşe düzeltmesi 5,102 mm, çerçeveler korundu. Yeniden açma ve geometri kontrolleri geçti. Pavyon cam çatı detaylarına devam ediliyor.

## 23:52 UTC civarı — R13
Push sonrasında üretim sürdü. 089 ile pavyon kulesinin sekizgen taslağı dört yüzlü cam kuleye düzeltildi. 108 cam/334 kapalı hacim, düzlem/kalınlık ve taş saçak bağlantıları yeniden açılarak kontrol edildi. Batı cam merdivenin 066/097 ve kat planı incelemesine geçiliyor.

## 2026-10-09 00:02 UTC civarı — R14
İki kollu batı cam merdiven 066/097 ve 102/103 ile üretildi. 17 görünür rıht ayrı sayıldı; 17+17 ve eşit kat kotu bölüşümü aday. İlk denemenin üst galeri döşeme bağlantısı düzeltilip geçiş açıldı. 151 kapalı hacim, 102 basamak örneği ve bağlantı kontrolleri geçti; detay ve kot belirsizlikleri raporda.


2026-10-09 00:17:05 UTC — R16 v002: 089/090/092/093/094/097/099 ile 2222 dış çatı profili ayrı koyu kaplama malzemesine bağlandı. 5108 nesnenin geometri/konum/görünürlüğü aynen korundu; kaydedilen sahne tekrar açılarak denetlendi. R15 cephe adayları görsel kontrolde reddedildi, ana sahneye alınmadı.


2026-10-09 00:24:48 UTC — R17 v001: pavyon döşemesi, merdiven rezervi, karşı pencere ve iç yüz üretildi. 19 kapalı hacim ve yerel geçit/pencere/döşeme testleri geçti. Merdiven/parapet eksik; R15 cephe denemeleri hâlâ reddedilmiş durumda.


2026-10-09 00:33 UTC — R18 v002: iki açık geçit kapısı, yan/üst camlar ve dokuz yuvarlak iç portal eklendi. 61 kapalı hacim, merkezi geçiş ve önceki döşeme/pencere kontrolleri geçti. Ölçüler koşullu; oditoryum kaynak incelemesi sürüyor.


2026-10-09 00:45 UTC — R19 v002/R20 v002: oditoryum oda, taş kademeler, sahne, kaset tavan, camlı arka kabin ve 128 koltuk adayı üretildi. Yeni LCB fotoğraflarıyla yanlış ahşap zemin yorumu düzeltildi. Kesin ölçüler ve gizli koltuklar açık; paneller sıradaki iş.


R23/R24 üst galerilerin duvar/geçişleri ve cam ışıklık adayları, R25 temsilî pavyon merdiveni/parapeti ve R26 doğu çatı bağlantısı eklendi. Her biri kendi kaynak, belirsizlik ve yeniden açma raporuna sahiptir. Tam bina doğrulaması yapılmadı.


## 9 Ekim 02:48 UTC ara durum

R35 güncel sahne; R29–R35 bölgesel sahneler, kaynak/varsayım kayıtları ve renderlarla kaydedildi. Güncel GLB ve plan kesitleri R35 ile eşleşiyor. Bina tamamlanmadı: [mimari açık konular](reports/architectural_open_issues.json) içinde cephe–galeri, üst geçit–çatı ve giriş tavanı çelişkileri ayrı izleniyor. Arazi henüz ilk hendek etüdü; ayrıntılı çevre ve nihai teslim açık.


2026-10-09 03:46 UTC — R36–R43 ara üretim: koşullu cephe başlık kotu; üst geçit başlığı ve açıklık düzeltmesi; park bağlantıları/19 OSM ağacı; giriş tavan sürekliliği; ortak mesh verisi; Grand Hall çatı lamelleri; taş döşeme yüzeyleri. R40 alt cephe pencereleri duvara oturmadığı için reddedildi. R41 ile GLB34,62→27,14MB; sonraki detaylar ayrıca eklendi. Tam bina tamamlanmadı. A01 cephe/oda,A04 arazi,A06 alt pencere ve A07 fotoğraf köşe kimliği açık; rutin onay beklemeden üretim sürüyor.

- 2026-10-09 06:04:22 UTC — `6687c42` origin/main normal push doğrulandı; HEAD ve origin/main eşleşiyor. R44–R47 sahneleri, kontroller, renderlar ve30.603.316 bayt GLB (6782 mesh,775276 üçgen) gönderildi. Önceki push03:48:52 UTC; saatlik hedef aralığı bu kayıtta aşıldı. Paris08:00 durum raporu modelin tamamlanmadığını açıkça kaydeder. Üretim kat ayırma/canlı kesit ve kalan mimari kontrollerle devam ediyor.

## P20 canlı inceleme · 9 Ekim 2026

[Canlı 3B inceleme](MODEL_INCELEME.html): üç kat aralığı, yatay/düşey kesit, kesilmiş yüzlerin seçimden elenmesi ve parça-kaynak bağlantıları doğrulandı. Geometri değişmedi. [Kontrol raporu](reports/P20_CANLI_INCELEME_RAPORU.md). Model üretimi sürüyor.


2026-10-09 06:50 UTC civarı — R48 v002 iki küpeşte kopukluğu ve beş cam üst bitişi; R49 v001 35 mineral/42 metal yüzey; R50 v001 Grand Hall 20 silindir armatürü üretildi. R48 ilk sürümü görsel kontrolde reddedildi. Her yeni sahne yeniden açılıp denetlendi; R50 genel denetiminde 6.892 görünür mesh, sıfır açık/sayısal bulgu. Boyut/ankraj ve malzeme adayları raporlarda ayrı; bütün bina tamamlanmadı.


2026-10-09 06:54:15 UTC — R51 v001: ana çatının dört geniş yüzüne 168 dizi/3.816 lamel eklendi. 028/029 ile alan ayrımı kontrol edildi; adım ve imalat ölçüleri koşullu. Yeniden açma, önceki geometri, panel sınırı ve genel kapalı mesh denetimleri geçti. Görsel kontrol üç bakışta yapıldı; üretim sürüyor.


2026-10-09 06:57:08 UTC — `1a21b8b4fc4c8acef1bbcbe88777397a23225bf0` origin/main normal push doğrulandı; uzak main SHA ile yerel HEAD eşleşti. R48–R51, canlı 3B kat/kesit/seçim arayüzü ve 33.842.004 bayt R51 GLB gönderildi. Vendor Three.js kaynaklarındaki mevcut tek whitespace uyarısı upstream SHA korunarak bırakıldı; proje dosyalarında diff-check ve viewer-core kontrolleri geçti. Üretim cephe–galeri kaynak kontrolüyle kesintisiz devam ediyor.


2026-10-09 07:30:14 UTC — R52 v009: iki galeri camı plan sınırına bağlandı; 22 yeni kapalı parça, oda duvarı boşluğu ve taş ayak birleşimi koordine edildi. 7.072 görünür mesh; kapalı hacim, dolaşım ve önceki geometri kontrolleri geçti. İkinci genişlik ve kaynak kamera kimlikleri koşullu; A01 kısmen koordine edildi. Üretim sürüyor.


2026-10-09 07:42:11 UTC — R53 v002: galeri nişinin taş yan yüzleri, plak eşiği ve mineral tavan altı işlendi; 28 nesne/168 yüz. 7.726 hesaplanan geometri nesnesi aynen korundu; UV ve gömülü doku kontrolleri geçti. Kaynak ölçüleri koşullu; alt cephe pencerelerinin duvarla ilişkisine devam ediliyor.


2026-10-09 07:51:23 UTC — R54 v002: beş tarihî duvar çentiği ve alt cam adayı; 45 yeni parça. 56 hacim/60 ışın, alt galeri ve bütün sahne kontrolleri geçti. 7.117 görünür mesh; ölçüler ve ilk iki pencere yanındaki duvar kaydı koşullu. A06 kısmen koordine edildi; peyzaj ve duvar yüzeylerine devam ediliyor.


2026-10-09 07:54:50 UTC — e82204cb308201b58e7a8e78ab9d0448f84f5691 origin/main normal push doğrulandı; uzak main SHA yerel HEAD ile eşleşti. R52–R54 sahneleri, kaynak/varsayım kayıtları ve 34.056.012 bayt R54 GLB gönderildi. 7.117 görünür mesh; model tamamlanmadı. Push ardından tarihî duvar yüzeyleri ve hendek çevresi üretimi devam ediyor.

2026-10-09T08:08:21.555779+00:00 — R55 v002: tarihî duvar/hendek görünümü işlendi; 7.781 hesaplanan nesnede geometri aynı. v001 çim tekrarı reddedildi. Kotlar ve tarihî örgü boyutları temsilî; üretim sürüyor.

2026-10-09T08:15:36.197964+00:00 — R56 v002: 19 OSM konumunda temsilî dallı/yapraklı taçlar;38 yeni mesh,204 yaklaşım kontrolü,7136 görünür mesh denetlendi. İlk seyrek taç denemesi yayımlanmadı; üretim sürüyor.

2026-10-09T08:21:29.355219+00:00 — R57 v001: giriş paspas/ızgara yuvası iki döşemeyle koordine edildi. 60 yeni parça,441 destek,52 kapı açısı,204 yaklaşım kontrolü geçti. R58 köprü korkuluğunun012/008 fotoğraflarıyla düzeltmesine geçildi.

2026-10-09T08:30:32.573796+00:00 — R58 v005: kaynak yakın çekimleriyle köprü korkuluğu iri boru/levha/cam düzenine çevrildi. Kolon teması ve160 taban desteği geçti;OSM kayıt farkı açık. 7211 görünür mesh. Üretim sürüyor.

2026-10-09T08:35:26.291975+00:00 — R59 v001: giriş/köprü taş döşemesi ve açık kenar bandı;50 yüz işlendi. Döşeme sınırı ve kotu korundu;204 yaklaşım örneği geçti. Üretim sürüyor.


2026-10-09T08:50:57.210117+00:00 — R60 v002 giriş/kolon/saçak yüzeyleri; R61 v002 fotoğrafta görülen altı armatür ve yuvaları. 7.235 görünür mesh,102 yuva ışını kontrol edildi. Eşleme belirsizliği açık; model üretimi sürüyor.


2026-10-09T08:56:21.447708+00:00 — 386951b5754ae3f75a4c0e79c132e45728ebf85f origin/main normal push doğrulandı; uzak main ve yerel HEAD aynı. R55–R61 sahneleri, renderlar ve kaynak kontrolleri gönderildi; R61 GLB84.707.696 bayt, tarayıcıda7.235 parça yüklendi. GitHub50MB tavsiye uyarısı verdi, aktarım başarılı ve dosyalar100MB sınırının altında. R62 döşeme örgüsü düzeltmesi sürüyor; üretim durmadı.


2026-10-09T08:57:18.495971+00:00 — R62 v001:013 yakın çekiminde belirlenen balıksırtı örgüyle yaklaşım taşı düzeltildi.17 yüz;geometri değişmedi. Giriş donatıları çalışması sürüyor.


2026-10-09T09:08:12.464329+00:00 — R63 v002 giriş panel/levhası; R64 v001 geçişi kapatan eski yükseltilmiş sabit alt profil düzeltildi.189 statik açıklık ışını,63 zemin örneği;7264 görünür mesh. Yan cephe pencerelerinin kaynağına devam ediliyor.


2026-10-09T09:34:14.834499+00:00 — Üretim kaydı basit HTML arayüzüne bağlandı. Son kayıtlar, arama, güncel sahne ve son push bilgisi doğrudan bu Markdown dosyasından okunuyor. R65 v002 çapraz gergi paketi kabul edildi; R66 geçit armatürlerinin sayısal kontrolleri geçti, son görsel kontrolü sürüyor. Modelin bütünü henüz tamamlanmadı.


2026-10-09T09:36:08.688352+00:00 — R65 v002 çapraz gergileri ve R66 v001 boyuna eleman/armatürleri görsel ve sayısal kontrolden geçti. R66:130 yeni kapalı parça,146 temas,32 lens açıklığı;7.634 görünür mesh. Armatür toplam adedi ve kesit ölçüleri aday. Geçit döşemesi ve çevre kaynaklarına devam ediliyor.


2026-10-09T09:45:55.459281+00:00 — Üretim panosu sadeleştirildi: beyaz zemin, siyah yazı,23 iş paketi ve ilerleme yüzdeleri. Her paket açılınca kalan işler gösteriliyor; teknik kayıtlar Markdown’da. Güncellemeler kısa özetlerle otomatik yenileniyor.


2026-10-09T09:48:57.535166+00:00 — R67: cam geçidin çapraz derzli taş döşemesi eklendi. İki yüz güncellendi; geometri ve kotlar korundu. Kaynak karşılaştırması, UV kontrolü ve iki render tamamlandı; modül ve desen aday.


2026-10-09T09:54:54.572662+00:00 — R68: pavyon yanındaki hendek kolu ve altı tarihî duvar eklendi. Harita çizgileri,30 duvar ve440 zemin örneği kontrol edildi; pavyonla yüz kesişimi yok. Kotlar ve duvar genişlikleri temsilî; kalan arazi işleri sürüyor.


2026-10-09T09:59:48.153715+00:00 — Saatlik hafif yayın düzeni kuruldu. Blender sahneleri ve GLB modelleri yerelde kalacak; yalnız pano, render, rapor ve üretim dosyaları gönderilecek. Mevcut saatlik otomasyon güncellendi; önceki model dosyaları yayımlanmış Git geçmişinde kalır.


2026-10-09 10:01:18 UTC — a7254f4b9d8f04c62cf0abddbe15aee722b357a9 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender/GLB modelleri yerelde tutuldu.



2026-10-09T10:07:29.485136+00:00 — R69: alt fuayenin gömme armatürleri ve tavan yuvaları eklendi.29 hacim ve119 ışın kontrolü, üç render tamamlandı. Konumlar ve çaplar kısmi aday; galeri aydınlatma referanslarına devam ediliyor.

2026-10-09 10:15 UTC — Canlı model 404 hatası düzeltildi. Blender ve sürümlü GLB arşivleri yerelde; tek güncel kayıpsız sıkıştırılmış GLB webde yayımlanır. Ortak model kaydı ve 60 saniyelik otomatik güncelleme eklendi. R69 tarayıcıda 7.669 parça ile açıldı; 89,20 MB özgün aktarım 54,18 MB olarak gönderilir. Mimari doğruluk kabulü anlamına gelmez.


2026-10-09 10:15:25 UTC — e2444462d0651ebac27af4dfaf92d3c6b97b8530 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



2026-10-09 10:18:20 UTC — 93ea9612b6416371665177c0b4df7e92f900349c origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



2026-10-09 10:23:15 UTC — Canlı xrweb.studio model yayını tarayıcıda doğrulandı: R69 ve 7.669 model parçası açıldı. GitHub Pages dağıtımı başarılı; ekran görüntüsü ve yayın kontrol raporu kaydedildi.


2026-10-09 10:23:25 UTC — f141c2a1606a74b566a4197076fab8fb091030d2 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



2026-10-09 10:32:45 UTC — R70: galeri ray ve spot adayları tamamlandı.86 kapalı parça,194 ışın,80 bağlantı;7.755 görünür mesh kontrolü ve üç render geçti. Adet, konum ve ölçüler kısmi aday; tam aydınlatma planı değildir.


2026-10-09 10:36:32 UTC — Kapsam kararı: yalnız bina ve kalıcı mimari sistemler. Sanat eserleri, heykeller, enstalasyonlar, sergi panoları, geçici bölmeler ve sergi mobilyaları modellenmeyecek. Plan ve saatlik üretim talimatı buna göre güncellendi.


2026-10-09 10:40:58 UTC — Üretim sırası güncellendi; sıradaki iş tüm duvarların kat kat kontrolü.

Tüm duvarlar → Zeminler ve döşemeler → Cam çatı geometrisi kontrolü → Cam çatı–duvar birleşimleri kontrolü → Merdivenler ve sahanlıklar → Pencereler ve kapılar → Korkuluklar → Diğer kalıcı mimari elemanlar → Bütünleşik plan–kesit uyumu ve gerekli ölçek düzeltmeleri → Malzeme ve yüzey detayları → Çevre düzenlemesi.

Bu sıra sonraki üretim kararlarında eski paket sırasının önüne geçer. Mevcut üretilmiş parçalar korunur; ilk iş bütün duvarların kat kat envanter ve geometri kontrolüdür. Duvarlardan önce yeni armatür, malzeme veya peyzaj detayı üretilmez. Her aşamada kaynak kontrolü sürer; bütün binanın plan–kesit uyumu geometrik elemanlar tamamlandıktan sonra ayrıca değerlendirilir. Gerekli düzeltme tek eksende veya genel ölçekleme olabilir; etkilenen eksen/sistem, referans, katsayı ve önce/sonra ölçüleri kaydedilir, bağlı açıklık ve birleşimler yeniden kontrol edilir. Kaynak çelişkisini gizlemek için zorla uyum sağlanmaz; özgün sürümler korunur.


## 2026-10-09 11:11:03 UTC — Duvar kontrolü R71 / R72

54 galeri duvarında 48 köşe düzeltildi. Grand Hall alt cephe boşluğu ve iki yüksek duvarın birleşimleri yeniden kuruldu. 96 galeri, 561 alt duvar, 20 temas ve 210 çatı taşma kontrolü geçti. Kullanıcının üç ekran görüntüsü kayda alındı. Yan salon bitişleri, merkez cam altı ve diğer bölgesel kontroller sürüyor; bütün duvarlar tamamlandı olarak işaretlenmedi. [Duvar kontrol listesi](reports/DUVAR_KONTROL_LISTESI.md).


## 2026-10-09 11:21:37 UTC — R73 / R74 duvar kontrolü

Galerilerin açık iç/dış duvar gövdeleri birleştirildi; kaynak Grand Hall geçidi korundu. 540 yüzey/90 geçiş kontrolü geçti. Studio dört köşe birleşimi ve sekiz boşluk kontrolü tamamlandı. Envanter 213 duvar adayını kapsıyor; genel tamamlanma onayı verilmedi.


2026-10-09 11:27:22 UTC — 86848362801a26019aab3f01b176c686c5f15644 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.


## 9 Ekim — R75 / R76 duvar kontrolü

Oditoryumda altı köşe, doğu üst merdiven çevresinde bir duvar ucu ve batı alt galeride bir dönüş bağlantısı düzeltildi. Sahne yeniden açılarak yerel testler, değişmemesi gereken nesneler ve bütün geometri kontrol edildi; hata yok. Bağlam renderları ve plan karşılaştırmaları incelendi. Duvar aşaması hâlâ açık; kalan bağımsız uçlar kaynaklarla inceleniyor.

## 9 Ekim — R77 batı uç bağlantısı

Batı kafe uç duvarının eğrisel taş cepheyle kopuk birleşimi düzeltildi; kotlar değiştirilmedi. On iç yüzey örneği ve iki mevcut nesne dışındaki geometri kontrolü geçti. Önce/sonra görseller incelendi. Çatı üst kotu ayrı açık kontroldür.

## 9 Ekim — R78 zemin galerileri

Batı kademeli ve doğu düz galeri iç yüzü mevcut dış kabuğa bağlandı. İki yeni duvar gövdesi; 126 kaynak yüzü, 1226 oda içi ve 102 merdiven boşluk örneği geçti. Tüm sahnede galeri girişleri açık kaldı. Kaynak plan ve iki iç render incelendi. Asansör çevresi ve genel duvar kabulü hâlâ açık.

## Öncelik güncellemesi — kapalı bina kabuğu

Öncelik, bütün iç mekânların duvar, zemin ve çatı/örtü sınırlarını plan, kesit ve fotoğrafa göre birlikte tamamlamaktır. Yanlış açık yüzey, eksik döşeme veya eksik üst örtü kalmadan kapı/pencere detayına geçilmez. Kaynakta gerçek açıklık olan yerler kendi sistemiyle çözülür. Sanat eseri ve sergi elemanı eklenmez. Yerel ölçü belirsizliği kaydedilir; gerçek geometri uydurulmaz.

## 9 Ekim — R79 eksik çatı köşeleri

Yanlış kare kesicinin kaldırdığı iki atrium çevresi çatı parçası geri kazanıldı. 342 örtü, 112 değişmez kuzey sınırı ve yedi gerçek okuma boşluğu kontrolü geçti. Üç bağlam renderı incelendi. Duvar–zemin–çatı birleşik kapanış denetimi sürüyor.


## R80 — kuzey cam şeridin alt kapanışı

087/119 ile zemine devam eden cam şeridin modeldeki alt açıklığı kapatıldı. 536 kapanış örneği, kapalı geometri ve değişiklik sınırı kontrolleri geçti; iki render incelendi. Genel kabuk kabulü açık. [Kontrol raporu](reports/R80_KONTROL_RAPORU.md).


2026-10-09 12:26:54 UTC — 6a434d91685e7e28d9918a4b219bd04ffbcb0306 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



## R81 — alt fuaye yan hacimleri

Eksik yan duvar, döşeme ve tavanlar 104 planına göre eklendi; oditoryum geçişleri korundu. 31 kapalı parça ve 405 sınır örneği geçti. [Rapor](reports/R81_KONTROL_RAPORU.md). Genel kabuk kabulü açık.


## R82 — batı merdiven giriş kabuğu

Eksik yan cam, üst örtü ve taş iç duvar eklendi; mevcut döşeme korundu. İlk 19 bölge taramasında kayıp alt/üst örtü veya 1,2 m kotunda yanal kaçak kalmadı. Çok kotlu kenar kontrolü devam ediyor; genel kabuk tamamlandı olarak işaretlenmedi. [Rapor](reports/R82_KONTROL_RAPORU.md).


## R83 — çatı kenar kapanışları

İki üçgen cam geçiş ve kafe arka taş duvarı eklendi. 81 eski kaçak doğrultusu kapandı; çok kotlu taramada giriş alt camlarında 18 bulgu kaldı. [Rapor](reports/R83_KONTROL_RAPORU.md).


## R84 — giriş sabit camlarının zemine kapanışı

12 sabit parça düzeltildi; önceki 18 alt açıklık kapandı. Hareketli kapı kanatları korundu. İki render, geometri ve değişiklik sınırı kontrolü geçti. [Rapor](reports/R84_KONTROL_RAPORU.md).


## R85 — batı üst sahanlık kabuğu

Eski düz döşeme uzantısı kaldırıldı; mevcut PDF dönüşünün eksik duvar ve tavanları eklendi. 571 sık örnek ve üst galeri geçiş regresyonu geçti. [Rapor](reports/R85_KONTROL_RAPORU.md).


## R86 — pavyon cam kenarları ve kabuk taraması

Cam kenarlarındaki aşırı küçültme düzeltildi. 26 bölgede 92.600 sık nokta ve 208.272 çok kotlu doğrultuda eksik zemin/örtü veya yanal kaçak bulunmadı. Genel görünüş ve kaynak bindirmeleriyle kontrol sürüyor. [Rapor](reports/R86_KONTROL_RAPORU.md).


## R87 — küçük batı galerisinin eksik kabuğu

Resmî plandaki küçük üst galeri önceki taramaya dahil değildi; döşeme ve çatısı eksikti. Oda ve bağlantı kabuğu eklendi. 29 bölgenin 97.080 sık örneği ve 218.136 çok kotlu ışını kontrol edildi; geçişler açık. Çatı eğimi ve kaynaklar arası yerel farklar henüz kesinleşmedi. [Rapor](reports/R87_KONTROL_RAPORU.md).


## R88 — batı merdiven cam birleşimleri

Basamaklardan yapılan ek taramada sekiz cam kenarı kaçağı bulundu ve düzeltildi. 25 panelin yalnız kenar payı değişti; 170 konum ve 12.240 yanal ışın yeniden kontrol edildi. [Rapor](reports/R88_KONTROL_RAPORU.md). Genel kabuk ve kaynak kabulü hâlâ açık.


2026-10-09 13:27:20 UTC — f2389998c9e0d07c0b17ac8fd32040c986c49b28 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



## R89 — alt kat duvar–döşeme birleşimi

37 çevre duvarı, değişmeyen iç tavanın üstünden zemin kat döşemesinin altına uzatıldı. Cephede açık görünen kat birleşimi kapandı; 296 önce/sonra ışın ve iki bina görünüşü incelendi. [Rapor](reports/R89_KONTROL_RAPORU.md).

### R89 kapsam denetimi

Diğer dört merdivende 590 konum ve 21.240 yanal ışın geçti. WC, vestiyer ve dükkân ayrı denetlendi. Toplam 33 bölge, 99.632 sık örnek ve 223.752 çok kotlu ışında eksik alt/üst örtü veya yanal kaçış bulunmadı. Bu sonuç kaynakta sınırı belirsiz idari/teknik alanları kapsamaz; bunlar bitmiş gösterilmiyor. [Kapsam kaydı](reports/R89_EK_KAPSAM_KONTROLU.md).


2026-10-09 13:47:14 UTC — 9d0f19a92bb71474146f651419888547b48216ee origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



2026-10-09 14:18:53 UTC — 368595ab6731eb8ad1fc1d4decd584489e0c66dd origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



2026-10-09 14:29:55 UTC — 879a076bf3f506bc42613a6b00159733d0f7b951 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



2026-10-09 14:40:43 UTC — 51a40aa5dc43f074080b4e6952559383502465f0 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



## R93 — Kuzey cam profil hizalaması

R93: Kuzey cam şeridi yatay kayıtları yan bandın ortak kotlarına bağlandı. Önce/sonra render kontrol edildi. Önceki üç ekran görüntüsündeki duvar–çatı bağlantıları ve içeride görünen mavi temsil hâlâ açık düzeltme işi.

[Kontrol raporu](reports/R93_KONTROL_RAPORU.md). 30 panel ve 15 profil yeniden üretildi; dört ortak yatay kot doğrulandı.


2026-10-09 14:53:13 UTC — 3d710e1f7355b899ec05c65c9125da7be3b132dd origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



## R94 — İşaretli kabuk birleşimleri

R94: Üç işaretli görünüş üzerinde gerçek geometri düzeltildi. Mavi iç temsil yüzeyleri kaldırıldı; batı ara çatı örtüsü/üst cam bandı, doğu duvar bağlantısı ve taşan duvar kotu düzeltildi. Son sahne üç açıdan kontrol edildi. Kesin çatı kesiti, köşe profilleri ve batı küçük çatı uç birleşimi hâlâ açık.

[Üç açıdan sonuç ve açık işler](reports/R94_KONTROL_RAPORU.md).


2026-10-09 15:13:23 UTC — c3e43d5efd44e726e053785635798d3c78c737dd origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



## R95 — SS1–SS5 düzeltmeleri

R95: Kullanıcının SS1–SS5 işaretleri ayrı düzeltildi. Cam kenar şeridi/dönüşü ve dış uç duvarı eklendi; kafe zemin katındaki yanlış duvar uzantısı kaldırıldı; yanlışlıkla kaldırılmış doğu giriş duvarı geri kuruldu. Önce/sonra aynı 84 yerel kontrolde R94’ün 75 başarısızlığı R95’te sıfır. Dış görünüşler ve iki zemin kat kesit görünüşü incelendi.

[İşaret bazlı sonuç görüntüleri](reports/R95_KONTROL_RAPORU.md).


2026-10-09 15:53:58 UTC — 3dec699583cea276a7e4c6875d20fe8e72a26384 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



## R96 — Üst kat düzeltmeleri

R96: Küçük batı galerisini kesen iki eski zemin kat duvarı üst döşeme altında sonlandırıldı. 2016 iç oda ile 103 merdiven kabuğunun farklı ölçekleri uzlaştırıldı; iki iç duvar kopyası kaldırıldı, kafe üzerine taşan +1 döşemesi daraltıldı. Okuma alanının doğusundaki eksik oda, servis merdiveni sınırı ve üst asansör kuyusu yüzleri kaynak planıyla üretildi. Kafe çatısına fotoğrafta görünen alt çubuk sistemi aday ölçülerle eklendi.

[Kaynaklar, kesit görselleri ve açık işler](reports/R96_KONTROL_RAPORU.md). Servis merdiveni basamakları ve kesin imalat ölçüleri açık; tüm bina tamamlanmadı.


2026-10-09 16:21:36 UTC — de27b405a677a823c03489a54b73494a74a217fd origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.

## R97 — Servis merdiveni ve pano

R97: Servis merdivenine 24 basamak/sahanlık parçası eklendi; yolu kesen alt kat tavanı ve giriş duvarı yerel olarak açıldı. Yedi kuyu duvarı iki kat arasında devam ettirildi. 110 yerel kontrol ve önceki duvar/cam düzeltmelerinin gerileme kontrolü geçti.

[Kontrol görselleri ve kaynak sınırları](reports/R97_KONTROL_RAPORU.md). Plan sembolündeki 24 bölme ölçülmüş rıht sayısı değildir. Dönüş yönü, rıht yüksekliği ve sahanlık aday; korkuluk ve alt kata devam ilişkisi açık. Bütün bina kabulü yapılmadı.

R97: Üretim panosunda tarihsiz R-sürüm kayıtlarının görünmemesi düzeltildi. Son doğrulanmış sürüm, son değişiklik ve öncelik ayrı gösteriliyor. Son kontrol saati üretim güncellemesi diye etiketlenmiyor. Yüzdeler gerçek iş adımı kabulü olmadan artırılmadı.

## R98 — Köprüye taşan duvar

R98: +1 kat köprüsüne taşan merdiven arka duvarı, üst başlık ve lento üç parçada kaynak plan sınırına çekildi. Aynı 118 yerel karşılaştırmada önceki 116 taşma yeni sahnede sıfır. Diğer işaretli bölgeler henüz tamamlanmadı.

Asansör çevresi, Studio/servis odası dışındaki kat ilişkileri ve son iki galeri duvar–döşeme işareti açık. Bu paket yalnız köprüye taşan duvarı düzeltir. [Önce/sonra ve kontrol raporu](reports/R98_KONTROL_RAPORU.md).


2026-10-09 16:55:36 UTC — 7af38d8a5b9f6d64c34b40ff77ce085027835154 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.

## R99 — Batı galeri giriş duvarı

R99: Batı galerinin planda çizili kısa giriş duvarı eklendi. Kuzey geçidini kapatan, üst odadan yanlış devam ettirilmiş R87 alt duvarı kaldırıldı. 15 duvar noktası ve iki girişte altı geçiş kontrolü geçti.

Merdiven yanı ikinci galeri işareti ile +1 Studio/servis/asansör çevresinin bütün kat ilişkileri açık; tüm ekran görüntüleri çözüldü denmedi. [Önce/sonra ve kontrol raporu](reports/R99_KONTROL_RAPORU.md).

## R100 — Galeri tavan–duvar temasları

R100: İki galeri tavanının dokuz plan noktası mevcut giriş duvarlarının iç yüzüne bağlandı. En büyük yerel uyumsuzluk 0,337 m idi; kontrol edilen 18 alt/üst köşe artık aynı sınırda. Batı galeri duvarı ve iki girişin geçiş kontrolleri yeniden geçti.

[Önce/sonra ve kontrol raporu](reports/R100_KONTROL_RAPORU.md). Bu yerel çizim uzlaştırması ölçülmüş imalat geometrisi değildir. Gerçek giriş boşlukları ve fotoğraf 026’daki yüksek merdiven yanı geçidi korunur. +1 Studio/servis/asansör çevresinin bütün kat ilişkileri ve diğer kabuk birleşimleri açık.


2026-10-09 17:12:01 UTC — 4d550d3ccf6f4d1acdbfb409f152e4f0c66f540f origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.

## R101 — Okuma odası yan geçidi

R101: Okuma odası–doğu servis odası bağlantısının planda çizili fakat eksik bırakılmış iki yan duvarı eklendi. 15 eksik duvar probu düzeldi; dokuz geçiş ve sekiz zemin/tavan kontrolü geçti. Diğer mevcut geometri değişmedi.

[Kontrol ve önce/sonra görselleri](reports/R101_KONTROL_RAPORU.md). +1 Studio, asansör ve diğer katlar arası kabuk ilişkileri hâlâ inceleniyor. Geçit duvarının yüksekliği ve kalınlığı aday; bütün bina kabulü yok.


2026-10-09 17:19:37 UTC — 476b2d557ca46ef08305132b4d781556b2070247 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.


2026-10-09 17:24:59 UTC — R101 kabuk kontrolü yenilendi: 25.156 alt/üst örtü örneği ve 9.558 galeri çatı kenarı ışını. Yeni geometri yok; yüzde değişmedi. Giriş önü dış alanı duvarla kapatılmadı. Ayrıntılar: reports/R101_KABUK_YENIDEN_KONTROL.md. Üst katın tüm yüzleri ve çelik/cam düğümlerinin kabulü açık.

## R102 — Üst servis duvar köşeleri

R102: Üst servis odası ve merdiven kuyusunda 14 duvarın 12 dış köşesi birleştirildi. Önceden açık olan 10 köşe probu kapandı; iç plan çizgileri ve açıklıklar korundu. Servis merdiveninin 110 kontrolü yeniden geçti.

[Kontrol ve önce/sonra görselleri](reports/R102_KONTROL_RAPORU.md). Bütün bina kabulü yok. Diğer üst kat duvar/örtü birleşimleri ve katlar arası devamlılık kontrolü sürüyor; ölçülmemiş kalınlık ve kotlar aday.


2026-10-09 18:22:34 UTC — 1fbcdd0e78043fa2c16d9fe9b5b43613851dce00 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.

## R103 — Üst galeri iç yüz birleşimleri

R103: Batı üst galeriye taşan dört duvar/tavan parçası mevcut plan sınırına kırpıldı. Servis odası birleşimindeki çıkıntı ve merdiven dönüşündeki yanlış tavan uzantısı kaldırıldı. Kapı ve koridor geçişleri korundu.

[Önce/sonra ve kontrol raporu](reports/R103_KONTROL_RAPORU.md). Bütün bina kabulü yok. Diğer kabuk birleşimleri ve kat ilişkileri kaynaklarla karşılaştırılmaya devam ediyor; ölçülmemiş kotlar ve kalınlıklar aday.

## R104 — Alt merdiven duvar devamı

R104: Alt batı galeri girişindeki kısa duvarın 5 cm geride kalan arka yüzü, komşu merdiven duvarıyla hizalandı. Ön yüz, giriş ucu ve kotlar korundu; alt galeri geçiş kontrolleri geçti.

[Önce/sonra ve kontrol raporu](reports/R104_KONTROL_RAPORU.md). Bütün bina kabulü yok. Diğer kabuk birleşimleri ve kat ilişkileri kaynaklarla karşılaştırılıyor; komşudan devralınan kalınlık ve kotlar ölçülmemiş adaylardır.

## R105 — Batı galeri döşeme/tavan teması

R105: Batı zemin galerisinde mevcut duvar ile döşeme/tavan arasındaki yaklaşık 20 cm açıklık giderildi. Yalnız iki mevcut nesne genişletildi; 1.030 temas ve 108 giriş/güzergâh kontrolü geçti. Önce/sonra görüntüleri karşılaştırıldı.

[Önce/sonra ve kontrol raporu](reports/R105_KONTROL_RAPORU.md). Bütün bina tamamlanmadı. Diğer dar duvar–döşeme–tavan temasları kaynaklarla karşılaştırılıyor; mevcut kotlar ve kalınlıklar ölçülmemiş adaylardır.


2026-10-09 19:23:33 UTC — 55f7c7f15e5adbecb220899530c95d88c67445d5 origin/main normal push doğrulandı. R103–R105 geometri düzeltmeleri, pano, renderlar, raporlar ve tek güncel web GLB gönderildi; Blender ve eski GLB dosyaları yerelde kaldı.

## R107 — Okuma odası döşeme teması

R107: Okuma odasının eski döşeme kenarı mevcut PDF2016 duvar konturuyla uzlaştırıldı; duvar dibindeki açık şerit giderildi. Merkez boşluk ve üç geçit korundu. 1.313 döşeme/boşluk ve 36 geçiş kontrolü geçti; önce/sonra görüntüleri incelendi.

[Önce/sonra ve kontrol raporu](reports/R107_KONTROL_RAPORU.md). Bütün bina tamamlanmadı. Diğer küçük odaların üst örtüleri, kalan çelik/cam birleşimleri ve bina son kontrolü açık; kesin kot ve malzeme ölçüleri hâlâ aday.

2026-10-09 19:43 UTC — R107 sonrası küçük üst odalarda 1.882 döşeme/tavan temas örneği, ana çatıda 1.864 ve yan çatılarda 1.802 profil ucu kontrol edildi; bu örneklerde eksik temas bulunmadı. Bunlar yeni geometri değişikliği değildir. Bağlantı donanımı ve bütün bina kabulü açık. R103–R105 için Pages dağıtımı 19:28:39 UTC'de başarıyla tamamlandı (691a609, çalışma 37979918482). R107 henüz yerelde; sonraki saatlik yayına hazır.

## R108 — Zemin servis duvar köşeleri

R108: WC, vestiyer ve dükkânda 15 mevcut duvarın 11 ortak köşesi birleştirildi. Önceki 22 boşluk örneği kapandı; kaynak eksenleri, kalınlık, kotlar ve kapı uçları korundu. 44 köşe ve 96 servis geçiş/destek kontrolü geçti; yakın önce/sonra görüntüleri incelendi.

[Önce/sonra ve kontrol raporu](reports/R108_KONTROL_RAPORU.md). Bütün bina tamamlanmadı. Diğer kabuk birleşimleri, merdiven/kapı detayları ve bütünleşik kaynak kontrolü açık; ölçülmemiş kalınlık ve kotlar aday.

## R109 — Servis merdiveni altı duvar köşeleri

R109: Servis merdiveni altındaki üç mevcut duvarın iki köşesi birleştirildi. Önceki dört boşluk örneği kapandı; mevcut kapı kesisi ve merdiven korundu. Sekiz köşe örneği, genel geometri ve merdiven geçiş kontrolleri geçti; önce/sonra görüntüleri incelendi.

[Önce/sonra ve kontrol raporu](reports/R109_KONTROL_RAPORU.md). Bütün bina tamamlanmadı. Diğer kabuk birleşimleri, merdiven/kapı detayları ve bütünleşik kaynak kontrolü açık; ölçülmemiş kalınlık ve kotlar aday.
# R107–R109 ek kontrol kaydı

[Temas taramaları, güncel görünüşler ve açık kalan konular](reports/R109_EK_TARAMALAR.md). Geometri değişiklikleri R107 okuma odası döşemesi, R108 servis duvar köşeleri ve R109 merdiven altı duvar köşeleriyle sınırlıdır. Bütün bina kabulü henüz tamamlanmadı.


2026-10-09 20:14:37 UTC — a48cdb398257cb9101891a3def42176943fdd923 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.

## R111 — Kafe geçidinin büyük üst örtü açıklığı

R111: Kafe–batı galeri geçidinde eksik üst örtü oluşturuldu. Aynı kamera karşılaştırmasında yatay yarık kapandı; zemindeki açık geçit korunuyor. Yeniden açılan sahnede önceki 132 örtüsüz örnek kapandı; genel geometri ve galeri geçiş kontrolleri geçti.

Öncelik büyük kabuk sorunları. Doğu merdiveni–duvar birleşimi ve kalan büyük açıklıklar bitmeden köşe veya malzeme detayına geçilmez. Örtü kotu mevcut 4,35 m galeri tavanı adayıdır; ölçülmüş uygulama detayı değildir.

[Önce/sonra ve kapsam](reports/R111_KONTROL_RAPORU.md).

## R112 — Doğu galeri giriş üst örtüsü

R112: Doğu galeri girişinin eksik üst örtüsü oluşturuldu. Önceki 81 örtüsüz örnek kapandı; geçitler ve yüksek atrium açıklığı korundu. Aynı kamera görsel karşılaştırması, sahne farkı, geometri ve geçiş kontrolleri geçti; altı merdiven ailesi taramasında yeni baş mesafesi engeli bulunmadı.

Öncelik büyük kabuk sorunları. Kalan büyük duvar/zemin/çatı açıklıkları bitmeden köşe veya malzeme detayına geçilmez. Örtü kotu mevcut 4,35 m galeri tavanı adayıdır; ölçülmüş uygulama detayı değildir.

[Önce/sonra ve kapsam](reports/R112_KONTROL_RAPORU.md).

## R113 — Galeri–servis uzun duvarları

R113: Zemin katın iki galerisinde servis alanına bakan eksik uzun duvarlar kaynak plan konturunda oluşturuldu. Önceki 360 eksik yüzey örneği kapandı. Galeri ve servis geçişleri, genel geometri ve sahne farkı kontrolleri geçti; iki aynı kamera önce/sonra görüntüsü incelendi.

[Kullanıcının işaretlediği bölgelerin tek tek güncel kontrolü](reports/R113_KULLANICI_ISARETLERI.md). R113 üzerinde özgün cam birleşimi, profil hizası ve üst kat taşma kontrolleri tekrar geçti. Yeni 6.292 bölgesel kabuk örneğinde boşluğa kaçan yatay ışın veya hiç alt/üst yüzey bulamayan örnek yok; bu, bütün yüzeylerin mimari kabulü değildir. Merdiven, okuma boşluğu, pavyon boşluğu ve oditoryumun farklı döşeme kotları ayrı değerlendirilir.

Üretim hedefi: 10 Ekim 2026 Europe/Paris 09:00. Öncelik kaynakla doğrulanan büyük kabuk sorunları, ardından merdiven, kapı/pencere ve korkuluklar. Saatlik doğrulanmış yayın sürer; yüzde yalnız tamamlanan işlere göre güncellenir.

Bütün bina ve kullanıcının tüm ekran görüntüleri henüz kabul edilmedi. Duvar kalınlığı mevcut kaynak konturları arasında uzlaştırılmış adaydır; kotlar ölçülmüş değildir. Öncelik kalan büyük kabuk sorunlarıdır.

[Önce/sonra ve kapsam](reports/R113_KONTROL_RAPORU.md).


2026-10-09 21:12:57 UTC — 98d844ca5706db1ae397ae959ac7fbceca518a04 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.

## R114 — Alt merdiven sahanlık perdesi

R114: 051 ve 052 fotoğraflarında görülen alt merdiven üst sahanlığı yanındaki eksik düşey taş perde eklendi. Aynı kamera önce/sonra görüntüsü incelendi. Yeni elemanın döşeme ve tavan temasları, alt kat geçişleri, alt merdiven regresyonu ve altı merdivenin baş mesafesi kontrol edildi.

Elemanın varlığı fotoğrafta görülüyor; yerleşimi mevcut merdiven üst kiriş hattına hizalı adaydır. 0,28 m kalınlık ve mevcut kol genişliği ölçülmüş değildir. Plan 104 bu ayrıntıyı göstermiyor. Bu paket yalnız bir temsilî mimari elemandır; bütün bina veya taşıyıcı sistem kabulü değildir. Büyük kabuk sorunları ve açık üretim işleri önceliğini korur.

[Kontrol ve önce/sonra](reports/R114_KONTROL_RAPORU.md).


### R114 sonrası — batı cam merdiveni

Alt kol, üst kol ve dış görünüş 066/097 fotoğraflarıyla karşılaştırıldı; bu turda yeni geometri değiştirilmedi. [Görseller ve açık sınırlar](reports/R114_BATI_CAM_MERDIVEN_KARSILASTIRMASI.md). Saatlik push zamanı henüz gelmedi; son yayın 21:12:57 UTC.


### R114 sonrası — doğu spiral ve pavyon

Güncel sahne kaynaklarla karşılaştırıldı; iki özgün dolaşım kontrolü geçti. Yeni geometri değişmedi. Pavyon alt katının karanlık renderı kabul için yeterli değil; aydınlatılmış teşhis görüntüsü sıradaki kontroldür. [Kanıt ve sınırlar](reports/R114_DOGU_PAVYON_KARSILASTIRMASI.md).


Pavyon alt katının iki aydınlatılmış teşhis görüntüsü incelendi: görüntülenen ana sınırlar mevcut, yeni delik saptanmadı. 101 kesitindeki tarihî yapı birleşiminin bugünkü iç yüzeyi belirsiz; bu kısım tamamlandı sayılmadı. Geometri ve ilerleme yüzdesi değişmedi.


2026-10-09 22:14:54 UTC — a94b15fa5302ff365d4c0079f8223c2ca7c4eee6 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



### R114 sonrası — oditoryum

Ön ve arka kabuk görüntüleri 071 ve LCB_auditorium3 ile karşılaştırıldı. Yeni geometri değişmedi. Arka kabin camındaki opak görünüşün geometri/ışık ayrımı açık kontrol olarak kaydedildi. [Karşılaştırma](reports/R114_ODITORYUM_KABUK_KARSILASTIRMASI.md).


Oditoryum kabin penceresi: 18 ışın mevcut cama ulaştı; üç alçak ışın son sıra koltuk sırtlarını da gördü. Fazladan duvar/panel tıkanması saptanmadı. Geometri değiştirilmedi; ışık/malzeme görünüşü son detay aşamasında ele alınacak.


## R115: Pavyon kapısı cam tutucuları

R115: Altı mevcut camda 48 metal profil ve 48 conta üretildi. R115 sahnesi yeniden açıldı; mevcut geometri değişmedi, yeni çevre profilleri görsel olarak incelendi. Kesit ölçüleri temsilîdir. [Rapor](reports/R115_KONTROL_RAPORU.md).


R116: Sekiz yeni kullanıcı işareti için gerçek kabuk düzeltmeleri üretildi. Küçük oda iç bölmeleri kaldırıldı; dış sınır ve köprü duvarları mevcut çatı altına tamamlandı. Döşeme çakışmaları, portal/merdiven birleşimi, modern–tarihî alt cephe ve alt kat yan hacimleri düzenlendi. [Madde madde değişiklik ve açık sınırlar](reports/R116_KONTROL_RAPORU.md). Genel bina kabulü verilmedi; kapsam oranı yapay artırılmadı.


2026-10-09 23:27:53 UTC — 2f36b24e0c53f79d8247adf2e947938f421780be origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.


R117: Cephe köşesi altındaki dönüş tamamlandı; beş pencere, girintileri ve tarihî duvar açıklıkları birlikte köşe içine taşındı. Üst köprünün iki galeriyle döşeme bağlantısı ve doğu duvar ucu üretildi. Fotoğraf 004/116 ve plan 103 esas alındı. Pencere dizisinin 2,459 m kaydırılması mevcut model köşesine göre türetilmiştir; 0,12 m kenar payı ve diğer miras boyutları ölçülü rölöve değildir. Bütün bina kabulü ve kalan üretim işleri açıktır.


2026-10-09 23:46:28 UTC — 1b8dec982bfdb75e5f7d43f571eb0229a06a5b45 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.


R118: İki köprü bağlantı döşemesinin mevcut galeri eşikleriyle çakışan hacimleri çıkarıldı. Yeni parçalar yalnız eksik yan şeritlerde kalıyor; eski eşik ve zemin yüzeyi korunuyor. R117 bağlantılarına ait düzeltmedir; 62 önceki çift yüzey örneği giderildi, 78 son örnekte tek zemin yüzeyi var. Yeni mimari ölçü eklenmedi. Bütün bina kabulü değildir.

R119: Üst galerilerin dört eşiğinde ve batı dönüş döşemesinde yinelenen yüzeyler ayrıldı. Tamamen diğer döşemenin içinde kalan bir dönüş parçası gizlendi; açıklıklar ve bitmiş zemin kotu korundu. 1.364 yerel örneğin 716sında önce çift/üçlü yüzey vardı; sonra tüm örneklerde tek yüzey var. Beş mevcut nesne değişti, yeni nesne ve ölçü eklenmedi. Bütün bina kabulü değildir.

R120: Alt fuaye ile oditoryum döşemesinin çakışan ön şeridi ayrıldı. Fuaye döşemesiyle bütünüyle örtüşen iki giriş döşemesi gizlendi; özgün nesneler ve girişlerin zemin kapanışı korundu. 15.436 örneğin 306sında önce çift üst yüzey vardı; sonra tüm örneklerde tek yüzey var. Üç mevcut nesne değişti, yeni nesne veya ölçü yok. Bütün bina kabulü değildir.

R121: Zemin katta doğu dolaşım alanı, batı kafe ve küçük oda birleşimindeki üst üste binen döşeme hacimleri ayrıldı. Tamamen yinelenen bağlantı eşiği gizlendi; döşeme kapsamı korundu. Altı mevcut nesne değişti; yeni nesne veya mimari ölçü yok. 47.667 konumun 1.569unda önce çift yüzey vardı; sonra tüm örneklerde tek üst yüzey var. Bütün bina kabulü değildir.

R122: Batı üst kat dönüş tavanındaki yinelenen örtü gizlendi; kafe tavanı ile ön servis örtüsünün örtüşen hacmi ayrıldı. İki mevcut nesne değişti. 7.178 konumun 152sinde önce çift üst yüzey vardı; sonra tamamında tek yüzey var. Örtü kapsamı korundu; bütün bina kabulü değildir.

R123: Ana cam çatının dördüncü yüzünde aynı yerde iki kez üretilmiş iki çelik profil gizlendi; mevcut karşılıkları korundu. İki nesne değişti. Eşleşen profillerin en büyük köşe farkı 0,0027 mm; yüzler ve malzemeler aynı. Yeni mimari boyut yok; bütün bina kabulü değildir.


2026-10-10 00:49:18 UTC — eea8ade15d72d9b2fc65ae9cbca91a276e9397b3 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.


R124: Doğu yüksek duvarı, giriş başlığı, kafe sınırı, batı iç duvar ve köprü ucundaki yinelenen duvar hacimleri ayrıldı. Beş mevcut nesne değişti, yeni nesne veya mimari boyut yok. Altı yönden 88.912 örnekte birleşik dış sınır ve açıklıklar korundu. Bütün bina kabulü değildir.

R125: Alt oditoryum giriş duvarları, üst servis geçitleri ve batı cam/galeri duvar sınırlarında yedi hacim örtüşmesi ayrıldı. Yedi mevcut nesne değişti; yeni nesne veya mimari boyut yok. 24.036 ışında birleşik dış sınır ve açıklık kapsamı korundu. Bütün bina kabulü değildir.

R126: Üst köprü, sahanlık, okuma odası, Studio ve doğu oda döşemelerinin altı örtüşmesi ayrıldı. Beş mevcut nesne değişti; yeni nesne veya mimari boyut yok. 6.336 örnekte zemin kapsamı korundu, önceki 304 çift üst yüzey giderildi. Bütün bina kabulü değildir.

R127: Alt fuaye örtüsü ile oditoryumun iki yan örtüsü ve iki alt galeri örtüsünün dört hacim çakışması ayrıldı. Dört mevcut nesne değişti; yeni nesne veya mimari boyut yok. Altı yönden 250.156 örnekte birleşik dış sınır korundu. Bütün bina kabulü değildir.

R128: Okuma odasının eğimli örtüsü ile doğu odasının düz örtüsü arasındaki yinelenen hacim ayrıldı. Bir mevcut örtü değişti; yeni nesne veya mimari boyut yok. Birleşik dış sınır korunumu örneklendi; bütün bina kabulü değildir.


2026-10-10 01:45:55 UTC — b448b8e2ddb9d821d24a8ed2f66377a7edc2c208 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.


P21 aktarım: R128 geometrisi ve 8.477 parça değişmeden yinelenen buffer blokları paylaşıldı. Ham GLB 91.415.240 → 81.686.612 bayt; gzip 54.619.398 → 52.537.621 bayt. 12.532 veri görünümünün baytları birebir korundu. Mimari üretim artışı değildir; yüzde değişmedi. Sonraki saatlik yayına dahil.


2026-10-10 02:49:13 UTC — 82aebe3bf3eb0192cd73bfd052643167fce2e339 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



## R129 — Tarihî taş ve hendek malzemeleri

R129: 28 mevcut parçada tarihî taş ve hendek çimi için altı gömülü doku yenilendi. Kabul v002: geometri/UV/konum değişmedi; dört önce-sonra görünüş incelendi. v001 çim tekrar sınırları nedeniyle kabul edilmedi. Kullanıcı malzeme ve yakın çevre önceliği verdi; sohbet heartbeat otomasyonu kaldırıldı. Genel oran %73; mimari tamamlanma iddiası yok.



2026-10-10 06:38:23 UTC — 2286b119a355fb81d579ea25d80d73c1cd0a072f origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.

R130: Arşiv OSM verisinde iğne yapraklı olarak kayıtlı yedi ağacın geniş yapraklı taçları değiştirildi. Yedi dal ve yedi iğne yaprak ağı üretildi; eski 14 taç parçası gizlendi, gövdeler ve konumlar korundu. Ağaç türü, 8m yükseklik, 2.2m taç yarıçapı, dallanma ve renk ölçülmüş değildir. Bu yedi ağacın sınıf düzeltmesi bütün çevrenin kabulü değildir. Ara push yapılmayacak; doğrulanmış toplam kapsam %90 hedefine kadar yerel üretim sürecek. Kapsam puanı bu sınıf düzeltmesiyle otomatik artırılmadı.

R131: Sonradan üretilen 12 kabuk parçasındaki 115 yüz mevcut taş duvar ve taş döşeme ailelerine bağlandı. Sekiz duvarın düşey yüzleri ve dört döşeme bağlantısının üst yüzleri metrik UV aldı. Geometri, açıklıklar ve kotlar değişmedi. 3.2x2.4m duvar ve 3.6x3.6m döşeme tekrarları önceki görünüm adaylarıdır; ölçülmüş derz veya fiziksel renk kabulü değildir. Ara push yok; kapsam puanı değiştirilmedi.

R132: Arşiv OSM 759811369 karma ağaçlık sınırı mevcut park zeminine işlendi. 421.08m² bitkili zemin sert kaplamadan ayrıldı; mevcut 4m aday yol koridorları korundu. Bir zemin değişti, bir kapalı zemin nesnesi eklendi. OSM sınırı rölöve değildir. Düz arazi kotu, yol genişliği ve çim görünümü temsilîdir; diğer peyzaj sınırları, bitki dağılımı ve tarihî ayrıntılar açık. V001/v002 ortak köşe ağ bağlantısı nedeniyle reddedildi; v003 ayrı kapalı adalar kullanır. Ara push yok. P18 son adımı kaynaklı kısmi üretim nedeniyle 0→0.5; diğer puanlar değişmedi.

R133: Üç arşiv yol güzergâhı mevcut park zemininin koordinatlı kaplama dokusuna işlendi: 83345393 ve 49910981 taş döşeme, 50643005 küçük taş kaplama sınıfını taşır. İki gömülü 4096px doku ve tek malzeme kullanılır. Mevcut zemin geometrisi birebir korundu. Yol genişliği 4m aday; 600x300mm ve160x120mm görsel modüller, renk/derz düzeni ölçülmedi. V001–v003 yüz bölme adayları geometri/UV hatası nedeniyle reddedildi; v004 kabul edildi. Ara push yok. Kapsam puanı değişmedi.

R134: Okuma alanının sekiz eğimli tavanı ve doğu spiral merdiveninin basamak, çekirdek, kenar ve komşu taş yüzeylerinde 50 mevcut nesnenin 3484 yüzüne taş malzemesi ve metrik UV uygulandı. 015/016 ve 041/043 fotoğrafları taş yüzey sınıfını destekler. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; ölçülmüş panel, renk veya fiziksel kalibrasyon değildir. Geometri birebir korundu. Ara push yok. Kapsam puanı otomatik artırılmadı.

R135: Oditoryumun 230 mevcut ahşap panel, kapı ve çevre parçasına düşey damar dokusu ve yüz yönüne göre UV uygulandı. Akustik delikler, derzler ve açıklıklar değişmedi. 073 fotoğrafı ahşap sınıfı ve düşey damar yönünü destekler. 1.2x2.4m doku tekrarı, ağaç türü, damar şekli ve renk ölçülmüş değildir. İnceleme ışıkları yalnız render için eklendi; sahneye kaydedilmedi. Ara push yok. Kapsam puanı otomatik artırılmadı.

R136: Oditoryum zemin, sahne, geçiş basamakları ve taş ayaklarda 51 mevcut nesnenin 318 nötr yüzüne taş tane malzemesi ve metrik UV uygulandı. 071/073 fotoğrafları açık taş yüzey ailesini destekler. 2m doku tekrarı, renk ve taş türü ölçülmüş değildir; yeni derz çizelgesi üretilmedi. Tane etkisi oda uzaklığında hafiftir. Geometri, basamak kenarları ve açıklıklar birebir korundu. Ara push yok. Kapsam puanı otomatik artırılmadı.

P20 çevre görünürlüğü: Yakın çevre anahtarı artık revizyon adından bağımsız bölge kimliğini kullanır. R130 ağaç taçları (14), R132 bitkili zemin (1), R56 diğer taçlar (24) ve R68 pavyon hendeği (7) çevreyle birlikte gizlenir. Eski ad önekleri uyumluluk için korunur. Güncel R136 GLB içindeki gerçek nesne metaverisinde bu 46 parça ve görünür kalması gereken 234 R10/R19 bina parçası sınandı. Kesit/kat/seçim birim kontrolleri geçti. Bu test GPU performansı veya bütün görüntüleyici kabulü değildir. Ara push yok.

P20 kesit kapakları: Canlı görüntüleyicide yatay/düşey kesit kapakları eklendi. Üçgen kesişimlerinden kapalı halkalar çıkarılır; iç boşluklar delik olarak korunur. Açık veya dallanan halkalar doldurulmaz. Aynı mimari nesnenin malzemelere bölünmüş GLB parçaları kapak hesabında birlikte kullanılır. Kapaklar seçilebilir ve parça yalıtma/çevre anahtarına uyar. Sayısal kesit kotu artık 0.05m sürgü adımına yuvarlanmadan kullanılır. Değişmeyen kesitlerde kapaklar yeniden hesaplanmaz. Üst kat denemesinde altı karmaşık sınır açık kaldı; son adım yalnız kısmi. Ara push yok.

R137: Batı cam merdiveninin iki kolu, sahanlıkları ve taş iç duvarlarında 41 mevcut nesnenin 249 yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. 066 fotoğrafı taş basamak ve derzli taş duvar ailesini destekler. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; kesin taş modülü, renk ve metrik kamera çözülmedi. Geometri ve açıklıklar birebir korundu. Ara push yok.

R138: Giriş ile doğu/batı galeri dolaşımının üç mevcut döşemesinde yaklaşık 580m² üst yüzey, ortak taş plak ailesine ve metrik UV düzenine bağlandı. 017/026/070/077 taş yüzey sınıfını destekler; 0.9m plak, 3.6m tekrar ve kanonik yön mevcut R43 görünüm adayıdır, ölçülmüş derz dizimi değildir. Geometri ve açıklıklar birebir korundu. Ara push yok.

R139: Grand Hall ana duvarları ve galeri dış yüzlerinde dokuz mevcut nesnenin 58 nötr yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. 026/034/087/119 kaynakları taş yüzey sınıfını destekler. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; ölçülmüş panel çizelgesi ve renk kalibrasyonu değildir. Galeri iç beyaz yüzleri, geometri ve gerçek açıklıklar korundu. Ara push yok.

R140: Doğu bahçe galerisinin yaklaşık 334m² mevcut zemininin üst yüzü taş plak malzemesine ve metrik UV düzenine bağlandı. 041/043 taş yüzey ailesini destekler. 0.9m plak ve 3.6m tekrar mevcut R43 görünüm adayıdır; ölçülmüş derz çizelgesi değildir. Geometri ve açıklıklar birebir korundu. Ara push yok.

R141: Batı merdiven giriş iç duvarı ve kafe arka duvarı/başlığındaki üç mevcut nesnenin 18 nötr yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. 066/097 giriş taş duvarını, 093 kafe arkasındaki taş sınırı destekler. Mevcut R82/R83 kabuk adaylarının ölçü ve konum belirsizliği sürer. 2m tane ve 3.2x2.4m derz tekrarları görsel adaydır; ölçülmüş panel çizelgesi veya renk değildir. Geometri ve giriş açıklığı korundu. Ara push yok.

R143: Alt fuaye kuzey duvarının yaklaşık 169m² düşey yüzeyine taş derzi ve metrik UV uygulandı; yatay kenarlarda taş tane ailesi kullanıldı. 051/055 alt fuayenin taş yüzey ailesini destekler. R72 sınır/kot adayları değişmedi. 2m tane ve 3.2x2.4m derz tekrarları ölçülmüş panel çizelgesi değildir. Geometri birebir korundu. Ara push yok. R142 atlas adayı önceki balıksırtını örttüğünden reddedildi; R143 tabanı R141.

R144: Alt fuayenin yaklaşık 321m² tavan altı ve kavisli alın yüzeyinde 155 yüze taş tane malzemesi ve metrik UV uygulandı. 051/055 taş tavan ailesini destekler. 2m tane tekrarı görsel adaydır; fotoğraftaki tekil plak derzleri yeniden kurulmadı. R06 mevcut geometri, açıklık ve kotları birebir korundu. Ara push yok.

P21 performans: R144 aynı kamera yerel tarayıcı ölçümünde kenarlar açık 10.47, kapalı 12.45 kare/sn. Akıcılık kabulü verilmedi; ölçüm kayıtları P21_TARAYICI_PERFORMANS_OLCUMU.md içinde. Geometri ve %74 değişmedi; ara push yok.

R145: Kuzey cam çatı doğu taş alın/alt duvarı ve batı uç duvarındaki üç mevcut nesnenin 19 nötr yüzüne taş tane/derz malzemesi ve metrik UV uygulandı. 087/119 kuzey alın taşını, 093/097 batı uç taşını destekler. 2m tane ve 3.2x2.4m derz tekrarları mevcut görünüm adayıdır; ölçülmüş plak çizelgesi veya fiziksel renk değildir. Geometri ve açıklıklar birebir korundu. Ara push yok.

R146: Batı kavisli cam cephenin altındaki 18 mevcut taş duvar parçasının 144 yüzüne taş malzemesi ve kavis boyunca sürekli metrik UV uygulandı. 093 fotoğrafı taş bandı destekler. 2m tane ve 3.2x2.4m derz tekrarı görünüm adayıdır; ölçülmüş taş modülü değildir. 34 ortak kenarda UV farkı en fazla 0.000000954. Geometri ve açıklıklar aynı; gün ışığında doku kontrastı düşük, fiziksel renk/ışık kalibrasyonu açık. Ara push yok.

R147: Batı dönüşündeki beş mevcut taş duvar ve alt fuaye merdiven perdesinin toplam 36 nötr yüzüne taş malzemesi ve metrik UV uygulandı. 051/052 merdiven perdesini, 097 batı taş kabuğunu destekler. 2m tane ve 3.2x2.4m derz tekrarı görsel aday; ölçülmüş plak çizelgesi değildir. Geometri ve açıklıklar aynı. Perde dokusu mevcut ışıkta düşük kontrastlı; fiziksel renk/ışık kabulü açık. Ara push yok.

R148: Batı kafenin yaklaşık 288m² mevcut döşemesindeki 33 üst yüze taş malzemesi ve metrik UV uygulandı. Resmî Mudam kafe fotoğrafları CF01/CF02 eklendi; CF01 açık taş zemini ve derzleri gösterir. 3.6m doku tekrarı ve yaklaşık 0.9m modül mevcut görsel adaydır, rölöve değildir. Mobilya/eser üretilmedi; geometri ve açıklıklar birebir aynı. Kullanıcının son talimatı: bu iş bitince birikmiş doğrulanmış çalışmayı push et ve gerçekçi kapsam raporu ver. Genel oran %73.913, panoda %74.


2026-10-10 09:23:47 UTC — 57518e0aa83a7e3204ab8c20e7fea223552c3f5c origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.


R149: Üst köprünün mevcut döşemesindeki iki üst yüze komşu taş ailesi ve metrik UV uygulandı; yalnız P05_FLOOR_LP1_BRIDGE değişti. 045 üst dolaşım taşı ve 103 planıyla koşullu malzeme sürekliliği adayıdır. 017/077 taş ailesini destekler; kesin köprü derz çizelgesini kanıtlamaz. 3.6m tekrar/0.9m modül ölçülmüş değildir. Kayıtlı ışıkta kontrast düşük; fiziksel renk kabulü açık. Geometri ve açıklıklar aynı. Kapsam %74; yerel kabul.


2026-10-10 09:31:55 UTC — e0308a6ab08338a79d648224beee84852a445cb5 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.


R150 aday çalışması: ACT 2024 0.5m arazi rasteri ve 2,229,465 sınıflandırılmış nokta arşivlendi; iki hendekte 3,008.284m² eğimli aday üretildi. v001 köprü üstüne çıkan arazi ve pavyon duvar altı açıklıkları nedeniyle kabul edilmedi. Yeni GLB/push yok, güncel kabul R149, kapsam %74. Sonraki işlem köprü kaplama noktalarını mekânsal/kot filtresiyle ayırmak ve zemin örnek kapsamını ölçmek.


2026-10-10 11:43:34 UTC — 1e9df9476c2eb8357cbf6e468be36db35f40a878 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



2026-10-10 13:58:27 UTC — 196bf406048212f0942880838a186047b5f33c20 origin/main normal push doğrulandı. Pano, renderlar, raporlar ve üretim betikleri gönderildi; Blender ve arşiv GLB dosyaları yerelde; tek güncel sıkıştırılmış web GLB gönderildi.



2026-10-18 21:35:06 UTC — 7e3efc62f5c71dbda41dc12c35866b9cc326e92a origin/main normal push doğrulandı. R418 Context 3 yakın çevre inceleme GLB: Draco/WebP, 8.310.648 bayt; SHA256 8ce6269e267ec44abac4a7ca2dcf03c35f8cfa5e4a048fb3aa2edfe81a532a3a. Diğer Context 3 katmanları korundu. Bütün sur/zemin kapsamı tamamlanmış veya kaynak doğruluğu kabul edilmiş değildir. İlk canlı kontrol R314 döndürdü; dağıtım bekleniyor.

