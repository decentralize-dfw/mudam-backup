# Mudam ayrıntılı Blender modelleme planı

8 Ekim 2026 · Planlama sürümü 1

Amaç, Mudam'ın dışını ve içini birlikte açıklayan, yakın mesafede incelenebilen, katları ayrılabilen ve kesit alınabilen bir mimari model üretmektir. Duvar, açıklık, merdiven, taşıyıcı, kaplama ve birleşimler ayrı ve düzenlenebilir sistemler olarak kurulacaktır. Bu aşamada model üretilmedi; üretim yöntemi, iş paketleri, kanıt sınırları ve kabul ölçütleri hazırlandı.

Başlangıç kararı: önce ortak koordinat ve düşey geometri, sonra bina kabuğu ve dolaşım, ardından sistemler ve birleşimler, en son malzeme ve sunum. Bütün yapı kapsamdadır. Giriş → Grand Hall → bir galeri hattı yalnızca yöntemi sınayacak ilk ayrıntılı örnek bölgedir; nihai kapsamı daraltmaz.

## Çalışma belgeleri

- [Sistemler ve mimari detaylar](01_SISTEM_VE_DETAY_KATALOGU.md): eleman bazında üretim ve kontrol şartları.
- [Ölçü çözümü ve araştırma](02_OLCU_KANIT_VE_ARASTIRMA.md): kotlar, eksik referanslar ve kaynak çatışmaları.
- [Blender üretim şartnamesi](03_BLENDER_URETIM_SARTNAMESI.md): sahne, nesne, parametre, malzeme ve dışa aktarma düzeni.
- [İş paketleri](is_paketleri.json): bağımlılıklar, teslimler, tamamlanma koşulları.
- [Başlangıç parametreleri](parametreler.json): bilinen değerler ve boş bırakılmış ölçüler. `null`, sıfır anlamına gelmez.
- [Mevcut fotoğraf atlası](../10_Olcekli_Plan_ve_Fotograf_Analizi/FOTOGRAF_ATLASI.html) ve [arşiv kataloğu](../KATALOG.html).

## Başlangıç verisi ve güven düzeyi

117 kaynak dosyası, 105 fotoğraf, üç resmî kat şeması, iki kesit görseli ve 2016 PDF'sinden çıkarılan iki vektör kat şeması mevcut. Fotoğraf konumu çalışmasında 63 nokta ve yön tahmini, 33 aday bölge, 9 çözülemeyen kayıt var. Bunlar modelin karşılaştırma adaylarıdır; kalibre edilmiş kamera çözümleri değildir.

0, +1 ve −1 planları OSM bina izine ortak ölçekle oturtuldu. Dokuz eşleştirmede RMS fark 1,023 m; çözümden ayrılmış iki köşede 1,909 m. Bu, kaynaklar arası uyumdur; saha doğruluğu değildir. Milimetrelik detay üretmek, bina ölçülerinin milimetre doğruluğunda bilindiğini göstermez.

4000 piksel planlar daha fazla çizim bilgisi içermiyor. 2016 vektör çizgileri çözünürlükten bağımsızdır, fakat ziyaretçi/sergi şeması niteliği taşır; duvar kalınlıkları ve uygulama detayları için tek başına yeterli değildir. Kesit 101 henüz yatay ve düşey ölçüye kalibre edilmedi. İçindeki renkli ve tarihsel öğeler kalıcı binaya otomatik aktarılmayacak.

Üst kat için doğrulanmış iç fotoğraf ataması yok. Ana çatı yüksekliği, kat kotları, döşeme kalınlıkları, kapı ölçüleri ve profil kesitleri bilinmiyor. Bu eksikler bütün çalışmayı durdurmaz; etkilenen elemanın ayrıntılı üretimini sınırlar.

Her nesnenin dört ayrı doğruluk alanı olacak: plan konumu, düşey geometri, eleman detayı ve malzeme. Bir duvarın plandaki yeri güçlü, kalınlığı zayıf olabilir. Tek bir genel güven puanı bu farkı gizlemeyecek.

| Kanıt sınıfı | Anlamı | Kullanım |
| --- | --- | --- |
| A | Ölçülü birincil kaynak veya doğrulanmış saha ölçüsü | Kaynağın toleransı korunarak geometriyi belirler |
| B | Birden çok bağımsız görüntü ve çizimle tutarlı çıkarım | Değeri ve belirsizliği birlikte kaydet |
| C | Tek görsel, şema veya zayıf geometrik çıkarım | Düzenlenebilir geçici çözüm |
| U | Veri yok veya çelişki çözülemedi | Boş parametre ya da açıkça işaretli temsilî geometri |

Mevcut dış kontur mutlak ölçüm bakımından A değildir. Kameralar B/C adaylarıdır; çoklu görünüş testi tamamlanmadan B kabul edilmeyecek.

## Modelin kapsadığı alanlar

| Bölge | Üretilecek kapsam | Başlangıç durumu |
| --- | --- | --- |
| Yaklaşım ve tarihî çevre | Meydan, giriş köprüsü, hendek, yakın kale duvarları, arazi ve dolaşım | Yatay ilişkiler var; kotlar eksik |
| Giriş | Portal, saçak, vestibül, döner kapı ve yan doğramalar | Fotoğraf bakımından güçlü; ölçüler çıkarılacak |
| Grand Hall | Döşeme, yüksek taş yüzeyler, boşluklar, büyük merdiven ve cam örtü | Ana oranlar çözülmeli |
| Doğu cam salon | Cam örtü, destek sistemi, spiral merdiven, taş sınırlar | Görsel kapsam iyi; taşıyıcı kesitleri eksik |
| Batı cam salon ve kafe | Eğrisel çatı, cephe, döşeme, bağlantılar | Karşı kanattan aynalanmayacak; ek referans gerekli |
| Zemin galerileri | Çevre duvarları, açıklıklar, kapılar, ahşap döşeme, tavan | Geçici sergi panelleri ayrılmalı |
| Üst kat | İki kanat, küçük galeri, dolaşım, stüdyo/belgeleme alanı, çatı ışıklıkları | Plan esaslı hacim; ayrıntı için araştırma öncelikli |
| Alt kat | Galeriler, fuaye, oditoryum, merdiven boşlukları, servis eşikleri | Oditoryum fotoğrafları var; galeriler daha zayıf |
| Yan pavyon | Çokgen kaide, cam üst yapı, bağlantı geçidi, alt düzey | Pavyon ve ana çatı ayrı geometrik aileler |
| Servis alanları | Asansör, WC, teknik kapılar, görünen servis elemanları | Kesin katı bilinmeyen ayrıntılar geçici |
| Yeraltı teknik hacimler | Kesitte görünen depo/teknik hacim ilişkileri | Kesit tarihi ve kotu doğrulanana kadar temsilî |

Mekân adları ilk yerleşim adlarıdır; resmî plan etiketi ve yerel bölge kodu birlikte tutulur. Fotoğraf arşivindeki 'doğu/batı' açıklamaları da planla yeniden kontrol edilir.

## Tarih ve kalıcı mimari

Hedef, kalıcı mimariyi anlatan ana modeldir. 2016 sergi şeması, 2019 fotoğraf dizisi ve sonraki resmî fotoğraflar tek bir tarihli bina durumuymuş gibi birleştirilmeyecek. Kalıcı duvar, geçici sergi bölmesi, sanat eseri ve hareketli mobilya farklı koleksiyonlarda tutulacak.

Sergi panosu, tavandan asılı eser veya geçici renkli cam öğesi yapısal eleman kabul edilmez. Bir parçanın kalıcı olup olmadığı iki farklı tarihli kaynakta kontrol edilir. Tarihsel varyantlar ana geometriyi değiştirmeden açılıp kapanabilir. Tam bir '2026 mevcut durum' modeli, o tarihe ait saha/kurum referansı olmadan ileri sürülmeyecek.

## Üretim sırası ve aşama teslimleri

### Aşama 0 Referansların sabitlenmesi

Kaynak kimlikleri ve orijinaller korunur. Fotoğraflar tarih, bölge, olası kat ve panorama durumuyla indekslenir. Model dosyası ayrı üretim klasöründe açılır. Blender sürümü, makine belleği, GPU ve hedef gösterim ortamı kaydedilir. Mevcut çalışma için yüksek ayrıntılı Blender ana model ve ondan türetilen web modeli varsayılır; motor özel kararları daha sonra gerçek hedefle sınanır.

Teslim: kaynak manifesti, proje ayarları, bölge listesi, açık sorun listesi. Kabul: her kullanılacak referans kimliği dosyaya geri götürür; kaynaklara yanlış tarih veya ölçü atanmamıştır.

### Aşama 1 Yatay ve düşey geometrinin çözülmesi

Dış kontur, ana akslar, kat boşlukları, merdiven merkezleri ve pavyon bağlantısı ortak koordinata alınır. OSM konturu ile mimari kontur farklı referanslar olarak korunur. Kesit düzleminin plan üzerindeki izi çözülür; aynı açıklığın plan ve kesit karşılığı belirlenmeden yükseklik hesabı yapılmaz.

Zemin bitmiş döşemesi yerel Z=0 kabul edilir. Diğer kotlar bilinmeyen parametrelerdir. Kesitten ve perspektiflerden alt/üst döşeme, parapet, çatı oturma ve tepe kotları için aralıklar çıkarılır. Bütün bina için tek sabit kat yüksekliği dayatılmaz.

Teslim: ölçü defteri, en az iki ana kesit, sade kütle modeli, çözülen ve açık kalan parametreler. Kabul: merdiven başlangıç ve bitişleri aynı kat kotlarına bağlanır; ana boşluklar düşeyde devam eder; alternatif kaynak farkları belgelenir.

### Aşama 2 Bütün binanın sade geometrisi

Üç ziyaretçi katı, ana çatı, yan salonlar, pavyon, giriş ve arazi ilişkisi birlikte kurulur. Bu aşamada kaplama derzi, vida veya gerçekçi malzeme eklenmez. Amaç, dış silüet ve iç mekânın aynı hacim modelinde uyuşmasıdır.

Teslim: plan, dört ana yön görünüşü, iki kesit ve dış/iç kontrol kameraları. Kabul: hiçbir galeri tavandan/çatıdan taşmıyor; katlar arasında hayalî döşeme yok; pavyon geçidi bağlantı kotuna ulaşıyor; fotoğraf uyumunu sağlamak için farklı bölgeler rastgele esnetilmemiştir.

### Aşama 3 Kabuk ve dolaşım

Beton kütleler, döşeme kenarları, duvar açıklıkları, taşıyıcıdan ayrı kaplama yüzeyleri, merdivenler ve sahanlıklar kurulur. Katlar ve odalar arasında bağlantı tablosu çıkarılır. Her kapı bir boşluk, kanat ve bağlı iki mekânla tanımlanır.

Teslim: tüm alanları kapsayan mimari kabuk; ilk kapı/pencere listesi. Kabul: açıklıklar gerçek boşluk olarak çalışır; merdiven rıht toplamı kat farkıyla uyuşur; dolaşım çizgisi duvardan geçmez; kesitte görünen döşeme ve parapet kenarları süreklidir.

### Aşama 4 Çatı ve taşıyıcı sistemler

Önce çatı yüzeylerinin sınırları, sonra ana taşıyıcı eğriler/akslar, ardından ikincil profiller ve panel bölünmeleri kurulur. Doğrusal, eğrisel ve çokgen cam sistemler ayrı tarif edilir. Fotoğraftaki yansıma çizgisi profil veya derz sanılmayacak.

Teslim: ana cam örtü, iki yan salon, pavyon ve cam geçit için ayrı sistem modelleri. Kabul: en az üç farklı görünüşte silüet, panel sayısı ve bağlantı konumu tutarlıdır; detay uğruna ana çatı biçimi değiştirilmez.

### Aşama 5 Bir örnek bölgede tam ayrıntı

Giriş kapısı/portal, Grand Hall merdiven–korkuluk–taş birleşimi ve bir galeri penceresi seçilir. Her biri geometri, malzeme, yakın kamera ve kesit ile tamamlanır. Tekrarlı varlık sistemi ve malzeme ölçeği burada sınanır.

Teslim: üç örnek detay grubu, varlık kütüphanesi, düşük ayrıntı türevi. Kabul: yakın görüntüde kalınlık ve birleşim okunur; kesitte açık uç yoktur; aynı eleman farklı yerlerde tutarlı ölçü ve malzemeyle üretilebilir. Bu teknik kontrol geçince yöntem bütün binaya yayılır; ayrıca izin bekleme kapısı değildir.

### Aşama 6 Bütün bölgelere ayrıntının yayılması

Kapılar, pencereler, korkuluklar, taş derzleri, tavanlar, süpürgelikler, aydınlatmalar ve görünen servis detayları sistem kataloğuna göre tamamlanır. Üst katın araştırması sonuçlanmadıysa burada plan esaslı temsilî detaylar ayrı işaretlenir; başka kattan kopyalanıp doğrulanmış gibi sunulmaz.

Teslim: sistem ve mekân kapsam tablosu; tamamlanmamış öğelerin açık listesi. Kabul: her bölge için geniş görünüş, yakın detay ve kesit kontrolü vardır; 'tamamlandı' ile 'kanıt yok' ayrıdır.

### Aşama 7 Malzeme ve ışık

Nötr ışık altında taş, beton, ahşap, metal ve cam örnekleri karşılaştırılır. Sonra gerçek yönelimli güneş ve iç aydınlatma eklenir. Fotoğrafın beyaz ayarı malzemenin rengi olarak kopyalanmaz. Sanat eserleri ve geçici mobilyalar ayrı isteğe bağlı sahnedir.

Teslim: malzeme kütüphanesi, UV kontrolleri, gündüz ve gece görüntüleri. Kabul: fiziksel doku boyutu tutarlı; camın arkasındaki mimari okunabilir; taş derzleri köşelerde devam eder; render hatasını saklamak için cam opaklaştırılmamıştır.

### Aşama 8 Kat ve kesit deneyimi

Katları gizleme, ayrıştırma, yatay/düşey kesit ve dolaşım için ayrı sunum düzeni yapılır. Birden çok katı geçen merdiven, cam örtü ve duvarlar özel bağlantı grubuna alınır. Her kat kapatıldığında üstünde asılı kapı veya boşta korkuluk kalmaması test edilir.

Teslim: yüksek ayrıntılı ana model, hafif türev, örnek etkileşim durumları. Kabul: model sabit koordinata geri döner; kesit kapakları doğru malzemeyi gösterir; çarpışma yüzeyleri görünür geometriyi takip eder. Motorun kesit/şeffaflık davranışı gerçek dışa aktarmada denenir.

### Aşama 9 Son doğrulama ve teslim

Dosya temiz bir oturumda yeniden açılır; dokular, bağlantılar ve render kameraları kontrol edilir. Kaynak katmanları açılarak plan/kesit bindirmeleri ve sabit fotoğraf karşılaştırmaları hazırlanır. Nesne, üçgen, doku belleği ve çalışma hızı hedef cihazda ölçülür.

Teslim: sürümlenmiş `.blend`, varlıklar, parametreler, kaynak manifesti, dışa aktarma dosyaları, kontrol görüntüleri ve kalan belirsizlik raporu. Sadece güzel render almak tamamlanma ölçütü değildir.

## Hangi detay ne kadar modellenmeli

Görsel ayrıntı düzeyi ile ölçü güveni ayrı tutulur. Aşağıdaki mesafeler üretim stratejisidir, bina ölçüsü değildir.

| İnceleme biçimi | Geometri düzeyi | Örnek |
| --- | --- | --- |
| Uzak dış görünüş | Kütle, gerçek çatı silüeti, büyük açıklıklar | Taş kanatlar, cam tepe, hendek |
| İnsan ölçeğinde dolaşım | Çerçeve kalınlıkları, söveler, basamaklar, korkuluklar | Yaklaşık 1–5 m mesafeden mekân |
| Yakın mimari inceleme | Gerçek birleşim hacmi, cam kenarı, metal tutucu, derz | Yaklaşık 0,3–1 m mesafeden detay |
| Seçili detay incelemesi | Kaynakta görülebilen vida, conta ve profil kesiti | Yalnızca kanıtı olan bağlantılar |

Silüet, boşluk, gölge ve kesit sonucu etkileniyorsa geometri kullanılır. İnce yüzey pürüzü normal/bump ile; yakın ve görünür derzler geometriyle çözülür. Görünmeyen donatı, ankraj gömülme boyu, çelik et kalınlığı veya cam katman dizisi kaynak yokken icat edilmez. Gerekli görsel temsil U sınıfında tutulur.

## Kabul hedefleri

Sayısal hedefler model üretim tutarlılığı içindir; tarihî yapının gerçek ölçü toleransları değildir.

- Ortak kotlara bağlı parçaların sayısal birleşme sapması: yaklaşık 1 mm veya daha az; bilinçli derzler hariç.
- Referans düzlemindeki çizgi takibi: kaynak çizgisinin kalınlığı ve belirsizlik bandı içinde. Düşük çözünürlüklü çizime santimetre doğruluğu atfedilmez.
- İyi kalibre edilmiş, panorama olmayan kontrol görüntülerinde hedef: temel kenarların medyan izdüşüm farkı görüntü genişliğinin %1'inden az; %2'den fazla fark yeniden inceleme sebebi. Bu yalnızca görsel uyum ölçütüdür.
- Kamera çözerken kullanılmamış en az iki görünüşle büyük sistem kontrolü. Yeterli görüntü yoksa bağımsız kontrol eksikliği yazılır.
- Pencere/kapı tiplerinin hepsi ve sayılan bütün örnekleri eleman listesinde bulunur. Adetler çizimden sayılmadan tahmin edilmez.
- Gözlemlenebilir bütün bölgeler kontrol edilir; üst kat ve teknik alan eksikleri teslim raporunda görünür kalır.
- Her kesinleştirilmiş elemanın kaynak kimliği; her varsayımın etkilediği parametre ve yeniden kontrol koşulu vardır.

## Öncelikli riskler ve çözüm

| Risk | Etkisi | Önlem |
| --- | --- | --- |
| Kat kotlarının yanlış çözümü | Bütün merdiven, cephe ve çatı değişir | Ayrıntıdan önce düşey geometri aşaması |
| Şematik çizginin gerçek duvar kabulü | Kalınlık ve oda ölçüsü bozulur | Taşıyıcı, kaplama ve geçici bölmeyi ayrı izle |
| Eski kesitin mevcut yapı kabulü | Yanlış hacim/çatı oluşur | Kesit izi ve fotoğraf eşleştirmesi |
| +1 fotoğraf eksikliği | Üst kat ayrıntısı tahmine dönüşür | Birincil kaynak, fotoğraf ve sanal tur araştırması |
| Fotoğraf kamerasına aşırı uyum | Bir açı iyi, diğerleri yanlış | Birden çok kamera ve ayrılmış kontrol görüntüsü |
| Taş duvarın tümünün taşıyıcı kabulü | Kesit ve açıklıklar yanlış olur | Malzeme yüzeyi ile yapı sistemini ayır |
| Çok erken küçük detay | Büyük ölçü değişikliğinde yeniden iş | Aşamalı geometri ve parametre bağımlılıkları |
| Aşırı ağır ana sahne | Dolaşım ve teslim yavaşlar | Bağlı kopyalar, bölge dosyaları, ayrı hafif türev |

Takvim, ilk örnek bölgedeki üretim hızı ve referans çözüm süresi görülmeden gün cinsinden kesinleştirilmez. Kritik yol: ölçü çözümü → tüm bina kütlesi → kabuk/dolaşım → cam sistem → örnek detay → yaygınlaştırma → doğrulama. Kaynak araştırması bu akış boyunca ilgili bölgenin yanında ilerler.

## İlk modelleme oturumunun görevleri

1. Blender ortamını ve mevcut proje dosyalarını kontrol et; ana sahne ve çalışma ölçeğini oluştur.
2. Üç kat şemasını, OSM konturunu ve kesiti kilitli referans koleksiyonlarına yerleştir.
3. X/Y koordinat dönüşümünü iki bilinen noktayla doğrula; Z=0 referansını tanımla.
4. Dış kontur, ana boşluklar ve pavyonu parametrik sade geometri olarak oluştur.
5. Kesit düzlemini ve kot adaylarını kaydet; çözülmeyenleri `null` olarak koru veya açıkça taslak aralığı seç.
6. Giriş, Grand Hall ve pavyon için üç başlangıç karşılaştırma kamerası kur; atlas yönlerini yalnızca başlangıç tahmini olarak kullan.
7. İlk oturum sonunda plan/kesit/silüet kontrol görüntüleri ve değişen parametre listesini kaydet. İlk oturumda ayrıntılı kapı kolu veya taş dokusu üretme.

## Kaynak bağlantıları

- [Mevcut ölçekleme raporu](../10_Olcekli_Plan_ve_Fotograf_Analizi/KALIBRASYON_RAPORU.txt).
- [Mudam resmî mimarlık sayfası](https://www.mudam.com/visit/architecture).
- [Luxembourg Kamu Yapıları proje ve teknik açıklaması](https://travaux.public.lu/fr/projets/projets-batiments/2006/nca.html).
- [Pei Cobb Freed proje kaydı](https://www.pcf-p.com/projects/mus%C3%A9e-dart-moderne/).

Bu web kaynakları 8 Ekim 2026 tarihinde kontrol edildi. Yeni bir ölçü veya tarih bilgisi, ilgili elemanın kanıt kaydına işlenmeden ana modelin kesin değeri yapılmaz.
