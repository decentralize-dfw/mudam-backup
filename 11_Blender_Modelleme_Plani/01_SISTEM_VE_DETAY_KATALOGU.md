# Mudam yapı sistemleri ve detay üretim kataloğu

Bu katalogda her satır bir üretim yükümlülüğüdür. Referans kimlikleri mevcut arşivin dosya numaralarıdır. Bir referansın belirtilmesi, ölçünün çözüldüğü anlamına gelmez. Eleman adetleri ve gerçek profil ölçüleri üretimden önce kayıt altına alınacaktır.

## Resmî açıklamanın desteklediği sistem ayrımı

Kamu Yapıları proje açıklaması, taşıyıcı duvar ve döşemeleri beton; iç/dış yüzeyleri ve galeri dışındaki döşemeleri doğal taş olarak tanımlar. Taş Bourgogne kökenlidir; galeri zeminleri ahşaptır. Cam örtünün ince çelik sistem ve metal doğramalarla kurulduğu, iç doğramalarda doğal ahşap kullanıldığı belirtilir. Üst galeriler için tepeden doğal aydınlatma tarif edilir. Bunlar malzeme ailesini destekler; eleman kalınlığı veya üretici ürününü belirlemez. [Resmî teknik açıklama](https://travaux.public.lu/fr/projets/projets-batiments/2006/nca.html)

## Arazi ve tarihî yapı

| Kod | Eleman | Modelleme kapsamı | Kontrol ve açık ölçü |
| --- | --- | --- | --- |
| SITE01 | Yakın arazi | Düzlem yerine eğimli yüzey; kırık şevler, bina oturuşu | Kot verisi yok; OSM yalnızca yatay referans |
| SITE02 | Hendek ve tarihî duvar | Duvar üstü, taban, kalınlık, köşe, yeni yapıyla aralık | 002–005, 063, 065, 088, 124; farklı kotları çöz |
| SITE03 | Giriş köprüsü ve meydan | Döşeme, parapet, eşik, bitiş derzi, görünen drenaj | 006–014; taş basamak sanılan eğimleri ayır |
| SITE04 | Arka yaklaşım | Köprü/rota, yan korkuluklar, kale ilişkisi | 087, 119; ana girişle karıştırma |
| SITE05 | Peyzaj | Yol kenarları, ağaç kütleleri, çim, yer örtücüler | 122/123 konumu çözülemedi; kesin dikim noktası verme |

Yakın çevre ayrıntılı, uzak çevre daha sade tutulur. Peyzajdaki ağaç yüksekliği ve taç genişliği fotoğraftan değişken aralıkla çözülür; tek referanstaki mevsim bütün sahneye kontrolsüz taşınmaz.

## Beton duvarlar ve döşemeler

Taşıyıcı duvarın aksı, kalınlığı, başlangıç ve bitiş kotu ayrı parametrelerdir. Taş kaplama taşıyıcı beton kalınlığını tanımlamaz. Görünür yüzeyden arka katman kalınlığı okunamıyorsa kesit gösteriminde bu ayrım temsilî olarak etiketlenir.

| Kod | Eleman | Ayrı üretilecek parçalar | Tamamlanma kontrolü |
| --- | --- | --- | --- |
| STR01 | Ana beton duvarlar | Düz/eğrisel gövde; açıklıklar; başlık ve bitişler | Bütün kat ve kesitlerde süreklilik; hayalî kolon yok |
| STR02 | Döşemeler | Kat plağı, merdiven boşluğu, döşeme kenarı, kaplama | Bitmiş kot ile beton üst kotu ayrılmış |
| STR03 | Kolon ve düşey destek | Kesit biçimi, başlık, ayak, görünen birleşim | Önce fotoğrafta gerçekten destek olduğu doğrulanmış |
| STR04 | Kiriş ve konsol | Açıklık, alt yüzey, oturma ve birleşim | Geometrik birleşim var; mühendislik kapasitesi iddiası yok |
| STR05 | Eğrisel taş/beton yüzey | Eğri kontrol noktaları, kalınlık, kenar sürekliliği | Farklı kot kesitleri ve teğetler kontrol edilmiş |
| STR06 | Yeraltı temsilî kabuk | Teknik hacim, depo sınırı, temel izi adayı | U sınıfı ve ayrı koleksiyon; görünmeyen donatı üretilmemiş |

Her döşeme boşluğu bir kimlik alır; üstündeki korkuluk, merdiven ve alt tavan aynı boşluk tarifini kullanır. Tek taraflı yüzey yerine kesitte anlamlı kalınlığı olan gövde kullanılır. Tasarlanmamış çakışmalar otomatik boolean ile gizlenmez.

## Taş cephe ve iç taş yüzeyler

| Kod | Eleman | Ayrıntılar | Referans |
| --- | --- | --- | --- |
| STN01 | Düz kaplama yüzeyi | Blok/levha modülü, yatay-düşey derz, şaşırtma, renk değişimi | 001–005, 010, 017, 019, 094 |
| STN02 | Köşe ve dönüş | Gerçek köşe taşı/levha dönüşü, birleşim izi, pah | 005, 059, 063; görünmeyen yüzü varsayım olarak tut |
| STN03 | Derin pencere sövesi | Eğimli yanak, başlık, denizlik, iç/dış dönüş | 056, 061–063, 100 |
| STN04 | Portal ve saçak | Açıklık üstü, yan yüzler, tavan, kolonla birleşim | 006, 008–014 |
| STN05 | İç döşeme | Plaka boyutu, döşeme doğrultusu, merdiven önü kesimler | 021–026, 045, 050–055 |
| STN06 | Parapet üstü | Üst taş, köşe, bitiş, fotoğrafta varsa damlalık | 007, 087, 098 |

Derzleri tek bir dünya koordinatlı dokuya bırakmak yerine yüzey yerel eksenleriyle kur. Farklı cephelerdeki sıra hizaları ve pencere çevresindeki kesilmiş taşları say. Taş modülü doğrulanana kadar tüm cepheye yayma. Taşın rengi, pürüzlülüğü ve boşluk gölgesi ayrı malzeme bileşenleridir.

## Kapılar

Her kapı örneği `DR_KAT_BOLGE_NUMARA` kimliği alır. Liste alanları: bağlı iki mekân, açıklık eni/yüksekliği, eşik kotu, duvar ve kasa derinliği, kanat adedi, menteşe/dönüş ekseni, açılma yönü, camlı bölüm, kasa, pervaz, kol, kilit yüzeyi, kapatıcı, eşik, kaynak ve kanıt durumu.

| Aile | Üretim kapsamı | Referans ve not |
| --- | --- | --- |
| DR01 Giriş döner kapı | Merkez eksen, cam kanatlar, üst/alt parçalar, sabit yan doğrama, eşik | 013/014; kanat sayısını görselden say, varsayma |
| DR02 Cam kapı | Yaprak, çerçeve, kol, menteşe veya pivot, cam kenarı | Pavyon/geçit ve giriş referansları; açılma türünü doğrula |
| DR03 Ahşap tek/çift kanat | Kanat, kasa, bölüntü, gömme/çıkma yüzey, donanım | 069/070/076; kesin kapı konumu araştırılacak |
| DR04 Teknik kapı | Sade kanat, kasa, görünen menfez/etiket | 079/080; katı bilinmeyen örneği bütün katlara çoğaltma |
| DR05 Asansör kapısı | Dış kapı, söve, çağrı paneli, kabin eşik ilişkisi | 077/078; durak katı doğrulanmamış |

Kapı kanadı origin noktası açılma eksenindedir; çarpışma ve görsel model ayrı olabilir. Açılma animasyonunda kasa ve duvarla kesişme kontrol edilir. Donanım markası, yangın sınıfı, gerçek erişilebilirlik uygunluğu kaynak yokken atanmaz.

## Pencereler ve sabit doğramalar

Pencereyi duvardaki resim düzlemi olarak değil, açıklık + söve + kasa + cam + iç/dış bitiş olarak kur. Her örnekte başlık/denizlik kotu, genişlik, derinlik, eğim, bölüntü sayısı ve varsa açılır kanat kaydedilir.

| Kod | Aile | Kritik ayrıntı |
| --- | --- | --- |
| WIN01 | Derin taş nişli galeri penceresi | İçteki dikdörtgen cam ile dıştaki eğik söve geometrisi ayrı; 061–063 |
| WIN02 | Tam boy cam yüzey | Düşey/yatay profil, alt kanal, köşe bağlantısı, taş sınır; 033/034/041 |
| WIN03 | Dar/ince cephe açıklığı | Açıklığın gerçek eni, çevre taş dönüşü; 094 gibi sınırlı referansta C |
| WIN04 | Üst galeri ışıklığı | Çatı boşluğu, yükseltilmiş kenar, ışık kırıcı/tavan ilişkisi; ek üst kat kaynağı şart |
| WIN05 | Cam geçit doğraması | Çatı-duvar köşesi, ara profil, kapı sonlanması; 064–068/099 |

Cam katman dizisi ve kalınlığı bilinmiyor. Render için seçilen optik kalınlık, gerçek yalıtım camı bileşimi olarak kaydedilmez. Silüette görünen cam kenarı geometri olur; iki çakışık yüzeyle cam taklit edilmez.

## Çelik ve cam örtüler

Alt sistemler: `ROOF_MAIN` merkezi cam örtü, `ROOF_EAST` doğu düz/eğimli salon, `ROOF_WEST` batı eğrisel salon, `ROOF_PAV` pavyon, `ROOF_LINK` bağlantı geçidi. Birinin panel örgüsü diğerine otomatik kopyalanmaz.

Her sistem şu sırayla üretilir:

1. Çevre sınırı ve oturma kotları.
2. Ana yüzeyler, eğriler, tepeler ve kırılma hatları.
3. Taşıyıcı ana hatlar; gerçekten görülen kablo/gergi veya çubuklar.
4. İkincil profil ve doğrama ağı.
5. Cam panel sınırları; kenar panelleri ve özel köşe parçaları.
6. Görünen düğüm, bağlantı plakası, profil ucu ve oturma detayı.
7. Kaynakta görünüyorsa conta, kapak profili, damlalık ve drenaj.

Parametreler: panel aks aralıkları, ana/ikincil profil dış boyutları, kesit ailesi, eğim, eğrilik, tepe ve taban kotu. Gerçek profil kodu veya et kalınlığı açık kaynakta çözülmedikçe `unknown` kalır. Fotoğraftaki siyah kenar; profil, conta, gölge veya yansıma olabilir; yakın ikinci görüntüyle ayrılır.

Ana referanslar: iç 025–040/110/114; dış 086–100/109/119; kesit 101. Panorama fotoğrafları biçim okumasında kullanılır, tek perspektif kamera çözümüne zorlanmaz. Panel sayıları her görünür yüz için ayrı kontrol çizelgesine işlenir. Gerçek sayı bulunmadan düzenli grid üretmek yalnızca taslaktır.

## Merdivenler ve korkuluklar

Merdivenler en az üç ayrı ailede izlenir: geniş ana kol ve sahanlık ilişkisi, ana boşluktaki eğrisel alt kat merdiveni, doğu cam salondaki spiral merdiven. 021/022, 050/051 ve 041/042 aynı geometri kabul edilmez.

| Kod | Üretilecek öğe | Hesap ve kontrol |
| --- | --- | --- |
| STA01 | Basamaklar | Rıht sayısı, rıht yüksekliği, basamak derinliği, burun, yan kesit |
| STA02 | Merdiven taşıyıcısı | Görünen alt yüzey ve yan kalınlık; spiral/eğri kontrolü |
| STA03 | Sahanlık | Kat ve ara kot, döşeme birleşimi, yürüyüş devamlılığı |
| RAI01 | Cam korkuluk | Panel sınırları, gerçek kenarlar, alt/yan tutucular, derzler |
| RAI02 | Metal küpeşte | Kesit, eğri, ek yerleri, duvar bağlantısı, bitiş ucu |
| RAI03 | Dış parapet/korkuluk | Üst taş/metal eleman, köşe, köprü kenarı |

Rıht sayısı tam sayıdır; toplam yükselme `n × h` ile kat farkını kapatır. Spiral merdivende yürüyüş hattı, dar iç uç ve dış kenar birlikte kontrol edilir. Eğrisel korkuluğu merdivenden bağımsız göz kararı spline ile çizmek yerine aynı geometrik referansa bağla. Kullanılan korkuluk yüksekliği gerçek ölçü veya geçici parametre olarak etiketlenir; genel standart bina ölçüsü yerine konmaz.

Detay referansları: 023/024, 041–044, 046–053, 055/115. Yakın fotoğrafın hangi kol veya katta olduğu kesinleşmeden detay o konuma sabitlenmez.

## Tavanlar ve iç mekân bitişleri

| Kod | Eleman | Üretim kapsamı |
| --- | --- | --- |
| INT01 | Galeri ahşap döşemesi | Tahta yönü, modül, kapı eşiği, kenar bitişi; 056–062 |
| INT02 | Galeri tavanı | Düzlem, ışıklık, ray, kenar/gölge derzi; 060 |
| INT03 | Oditoryum | Eğimli/teraslı zemin, sahne/perde, koltuk sırası, geçiş ve kapılar; 071–076 |
| INT04 | Akustik yüzey | Ahşap panel, perforasyon ve birleşimler; uzak görünüşte doku, yakında geometri |
| INT05 | Kaset tavan | Modül sayısı ve derinliği, duvar bitişi, armatür konumu; 074/075 |
| INT06 | Asansör ve WC | Yalnızca görünen donanımlar; kat ve oda yerleşimi doğrulanacak |
| INT07 | Aydınlatma ve görünür tesisat | Ray/spot, gömme armatür, menfez, görünür kanal, radyatör |
| INT08 | Yönlendirme | Kalıcı pano, kat etiketi, işaret levhası; geçici sergi yazılarından ayrı |

Oditoryum koltukları fotoğraf ve plana göre sayılır. Kaynak metinlerdeki kapasite değerleri çeliştiği için model adedi doğrudan bir metin sayısından üretilmez. Tesisatın görünmeyen bütün güzergâhı bu verilerle çözülemez; temsilî sistem gerekiyorsa ayrı ve açıkça belirtilmiş olmalıdır.

## Malzeme kütüphanesi

| Kimlik | Aile | Ayarlanacak özellikler | Doğrulama |
| --- | --- | --- | --- |
| MAT_STONE_EXT | Dış doğal taş | Fiziksel doku ölçeği, ton varyasyonu, pürüz, kir/su izi | Nötr ışıkta birden çok dış fotoğraf |
| MAT_STONE_INT | İç taş | Döşeme/duvar ayrımı, yüzey parlaması, derz | Gölgesiz ve yansımalı bölgeleri ayrı oku |
| MAT_CONCRETE | Görünen beton | Kalıp izi, ton, kenar, pürüz | Taş kaplama ile karıştırma |
| MAT_WOOD_FLOOR | Ahşap döşeme | Lif yönü, tahta genişliği, finisaj | Galeriler; fotoğraf ışığına göre renk kopyalama |
| MAT_WOOD_JOINERY | Ahşap doğrama | Panel yönü ve kenar, finisaj | Kapı/akustik kaplama ayrı varyant |
| MAT_METAL_FRAME | Metal çerçeve | Boya/anodize/çıplak metal olasılığı, yansıma ve pürüz | Fotoğraftan kesin alaşım iddia etme |
| MAT_HANDRAIL | Küpeşte metali | Kesit boyunca parlama, fırça yönü | Yakın korkuluk fotoğrafları |
| MAT_GLASS | Mimari cam | Yansıma/geçirgenlik, kenar tonu, optik kalınlık | İç ve dış görünüş beraber |
| MAT_SEAL | Derz/conta | Koyu ton, yüzey pürüzü, fiziksel genişlik | Görünür birleşimlerde |
| MAT_HISTORIC | Tarihî taş duvar | Yeni taştan farklı örgü, hasar, kir | Hendek ve kale fotoğrafları |

UV ölçeği metreye bağlıdır. Doku dosyaları renk/normal/pürüz olarak açık adlandırılır; veri haritalarının renk uzayı ayrı kontrol edilir. Marka, taş ocağı alt türü, metal alaşımı ve kaplama kimyası kanıt yokken kesinleştirilmez.

## Birleşimlerin ayrı kontrol listesi

- Taş kaplama ↔ beton gövde: kalınlık temsili, söve dönüşü ve kesit ayrımı.
- Taş ↔ taş köşe: sıra hizası, dönüş ve derz.
- Taş ↔ metal doğrama: açıklık payı, kasanın gömülmesi, gölge çizgisi.
- Çelik ↔ cam: panel kenarı, kapak/tutucu, görünen birleşim ve boşluk.
- Çatı ↔ taş duvar: oturma, çerçeve sonu, üst kapak; görünmeyen ankraj varsayım.
- Merdiven ↔ sahanlık: rıhtın bitişi, kaplama sürekliliği, boşluk kenarı.
- Korkuluk ↔ döşeme: ayak/tutucu konumu, kenar mesafesi, alt kanal.
- Kapı ↔ döşeme: eşik, malzeme geçişi, açılma boşluğu.
- Cam geçit ↔ ana yapı/pavyon: iki uç kotu, çatı/duvar dönüşü, hareket derzi görünüyorsa izi.
- Yeni bina ↔ tarihî duvar: temas mı, boşluk mu, köprü mü; fotoğrafla çöz.

Her birleşim için bir yakın görünüş ve bir basit kesit oluşturulur. Gerçekleştiği bölge, kaynak ve bilinmeyen katmanlar not edilir. Yakın görünüşü olmayan bir birleşimin vida/ankraj düzeni, uydurulmuş uygulama detayı olarak ana modele işlenmez.
