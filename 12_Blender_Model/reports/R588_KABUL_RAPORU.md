# R588 Batı terası ve cephe–hendek birleşimi: yerel kontrol kaydı

Bu paket, batı terası ile müze cephesi, istinat yüzeyi ve hendek zemini arasındaki bağlantıların yerel düzeltmesidir. Genel müze çevresi veya 11 bölgenin tamamı için nihai kabul değildir. Bu kayıt v013–v020 geometri ve normal düzeltmelerini kapsar. Son sahne ve temas AO çıktısı için `R588_AO_BUILD.json` içindeki gerçek girdi/çıktı alanları; son görsel ve aktarım sonucu için `R588_BROWSER_QA.json` ile `R588_RELEASE_VALIDATION.json` esas alınır.

## Yapılan geometri

- Batı apronunun üst yüzeyi ve istinat gövdesi, kaynakta görülen dış sınır ve az sayıdaki bağımsız eğimli düzlemle kapalı bir bütün olarak yeniden kuruldu. Taş/toprak malzeme sınırı yapay bir düşey basamağa dönüştürülmedi.
- Eksik 8.19282 m² alt zemin ve 14.68160 m² cam cephe köşesi zemini tamamlandı. Köşedeki eski döşemelerin yeni zemine taşan kısımları bütün kalınlık boyunca temizlendi.
- R549–R322 birleşiminin 12.33 m uzunluğundaki hattı eşlendi. v015 bütün-hat kontrolünde 41 ölçümle en büyük açıklık 4.96 µm idi; v019'daki son iç yüzey kontrolü aşağıda ayrıca kaydedildi. Bu ölçüler modelin birleşim/düzlem sürekliliğini gösterir; gerçek yapı kotlarının rölöve doğruluğu değildir.
- Alt zemindeki yapay sabit-X birleşimi, kaynakta gerçekten görülen diyagonal kot kırığına göre düzenlendi. Büyük dik banka yüzeyi korundu.
- R546 ile yeni restorasyon zemininin y=3.2 ortak hattı beş ACT kot kontrolünden bağımsız bir doğruyla kuruldu. Kaynak uyumu RMS 5.03 mm, en büyük fark 7.46 mm; v014 kontrolünde ortak gölgelendirme normal farkı 0.0198°, UVMap farkı 1.36e−8, MicroUV farkı 2.43e−7 idi.
- Ardından R546'nın restorasyon zeminiyle üst üste gelen kuzey kanadı bütünüyle kaldırıldı. 1.31629665 m² yinelenen yüzey temizlendi; gerekli 0.31929493 m² güney parçası orijinal üst koordinatlarıyla kapalı tutuldu. v016'da 30 ölçümle ortak hat açıklığı en fazla 1.43 µm, açık kenar ve sıfır alanlı yüz sayısı sıfırdır. Bu adım yalnız R546'yı değiştirdi; 18,299 diğer mesh aynı kaldı.

## Kaynakla ölçülen farklar

| Kontrol alanı | RMS | En büyük fark | Kapsam |
|---|---:|---:|---|
| Cam cephe köşesi kaynak düzlemi | 0.02516 m | 0.05323 m | 50 bağımsız kontrol noktası |
| Uzun R549–R322 terası kaynak düzlemi | 0.038936 m | 0.101245 m | 25 kaynak noktası; ilk küçük köşe alanından ayrı kapsam |
| Sol R549_1–R322 terası: bütün kontrollere uyum | 0.019623 m | 0.049971 m | 25 kaynak noktası |
| Sol teras: ayrılmış kontrol sınaması | 0.033000 m | 0.060632 m | 19 eğitim + 6 ayrılmış kontrol; iki istasyon bütünüyle dışarıda |
| Alt hendek tabanı düzlemi | 0.01584 m | 0.03325 m | Açık zemin kontrolleri |
| Batı üst yamaç | 0.01962 m | 0.04053 m | x=[−34,−31], y=[1.2,3.8] |
| Doğu üst yamaç | 0.04634 m | 0.10341 m | x=[−31,−24], y=[1.2,3.8] |
| Temizlenen R546 batı dönüşünde korunan zemin | 0.03733 m | 0.05958 m | Kaynakta görünen üç zemin kontrolü |

Son satırda kuzeybatıdaki sura çarpan ışınlar zemin ölçüsü olarak kullanılmadı. Kapalı/örtülü alanların kesin taban kotu bu ölçümlerle doğrulanmış değildir. ACT ve sınıflanmış arazi verisi arasında bazı yerlerde 0.2–0.5 m fark bulunur; bunlar ölçülü rölöve yerine geçmez.

## Malzeme ve aktarım

Taş, toprak ve yatay kapak alanları ayrıldı. R552'de taşın dikdörtgen biçimde toprağa taşması, aynı yüzey kotlarını koruyan malzeme bölümlendirmesiyle giderildi; ölçülen en büyük yüzey konum farkı 5.96e−7 m idi. Yatay kapakta yerel CC0 kumtaşı renk/normal/roughness haritaları kullanıldı; renk düzenlemesi kalıcı PNG'ye işlendi ve glTF'ye doğrudan bağlandı. ACT görüntüsü cephe ya da nihai yüzey dokusu olarak kullanılmadı.

Temas AO işlemi yalnız ortam kapanımı içindir; bütün ışıkların veya temel rengin bake edildiği anlamına gelmez. Son AO, Draco/WebP, tekrar içe aktarma ve tarayıcı sonuçları için `R588_RELEASE_VALIDATION.json` ve `R588_BROWSER_QA.json` esas alınmalıdır. Bu rapor tek başına yayınlandığını veya son sıkıştırılmış dosyanın kabulünü ilan etmez.

## Görsel kontrol ve sınırlar

`R588_west_v016.png`, aynı kamera yönündeki `R586_west_source.png` ile karşılaştırıldı. Eski R546 kuzey kanadının oluşturduğu küçük sivri dil kaldırıldı. Büyük koyu diyagonal banka yüzeyinin üç kenarında komşu yüzler bulunuyor; geometrik normal ile köşe normalleri uyumlu. Bu görünüm bir delik veya bozuk normal olarak sınıflandırılmadı: kaynakta gerçek dar ve dik bir kot kırığı bulunuyor.

Dik banka yüzeyinde tek yeşil malzemenin okunabilirliği ve kaynakla malzeme sürekliliği hâlâ sınırlıdır. Yüzey, gölgeyi saklamak için düzleştirilmedi. Örtülü duvar ayakları, bazı istinat eğimlerinin devamı ve güneyde kontrol alanı dışına uzanan düzlemler kısmen yorum içerir. Taş/toprak sınırının görsel izleme belirsizliği yaklaşık ±0.08 m'dir. Bu sınırlamalar açıkken bütün çevre için “birebir”, “tamamlandı” veya “%100” sonucu çıkarılamaz.

Ana müze geometrisinin korunması ve paketteki bütün eklenen/değişen/gizlenen nesnelerin listesi için `R588_PACKAGE_INHERITANCE.json` esas alınır. Denetim konum, topoloji, dönüşüm ve görünürlük hash'lerini karşılaştırır; beklenen malzeme/UV/AO değişikliklerini geometri değişikliği olarak saymaz.

## Kanıt kayıtları

- `R588_NOTCH_V014_BUILD.json`: beş kaynak kontrolü, ortak kenar, UV ve normal sürekliliği.
- `R588_R546_SINGLE_OWNER_V016_BUILD.json`: bütün yinelenen kanadın temizliği, kapalı güney parçası, yeniden açma ve kaynak farkları.
- `R588_PACKAGE_INHERITANCE.json`: ana müze ve hedef dışı geometrinin korunması.
- `R588_RELEASE_VALIDATION.json`, `R588_BROWSER_QA.json`: son aktarım ve tarayıcı kanıtları.

## Son cephe–teras temas kontrolü (v020)

v017, teknik yan duvarların üst yüzey normallerini bozmasını düzeltti. Uzun sağ teras hattındaki gerçek iç sırt ise v019'da giderildi: miras uzun/ince üçgenler 1 m aralıklar ve düzlem kırıkları boyunca bölündü, 135 köşe eklendi ve kaynakla sınırlandırılmış eğim bir kez uygulandı. v019'un 423 iç düzlem kontrolünde eksik ışın yoktu; en büyük iç düzlem farkı 0.41161 mm, RMS 0.02920 mm idi. Bunlar modelin kendi süreklilik ölçüleridir; uzun terasın 25 kaynak noktasına uyumu ayrı olarak RMS 38.936 mm, en büyük 101.245 mm farktır.

Önceki v019 üstten görselinde soldaki sorun “hafif kısa geçiş/ton çizgisi” olarak eksik tanımlanmıştı. Webde düşük bakış, bu 9.01 m temas hattında yaklaşık 0.47–0.50 m yanlış kot ve açıkta kalan beyaz/yeşil alt yüzeyi gösterdi. Sorun yalnız bir gölgelendirme ayrıntısı değildi; v020'de sol R549_1–R322 birleşimi boyunca geometri düzeltildi.

`R588_LEFT_JUNCTION_V020.json` kaydında R322'ye 383 köşe eklendi, 463 köşe düzeltildi; en büyük kot müdahalesi 0.53783 m'dir. Mevcut R549 kenar kotu 1 m genişliğinde sürekli geçişle korundu. Gerçek dış istinat tepesi korunarak bağımsız ACT zemin kontrollerinden kurulmuş düzlem uygulandı; tarama ağı veya yüzey resmi nihai model olarak alınmadı. Diğer 18,299 mesh'in geometrisi değişmedi.

Yeniden açma kontrolü geçti; R322 ve R549_1 gövdelerinde açık kenar ve sıfır alanlı yüz sayıları sıfırdır. Aynı tasarım yüzeyine karşı 296 kesit kontrolünde eksik ışın yoktur. Ortak kenar farkı en fazla 0.12178 mm, iç tasarım düzlemi farkı en fazla 0.82201 mm'dir. Bu iki sayı **model içi bağlantı/düzlem sürekliliğine** aittir ve kaynak ölçüm doğruluğu olarak okunmamalıdır.

Kaynak düzleminin 25 kontrolün tamamına uyumu RMS 19.623 mm, en büyük 49.971 mm'dir. İki istasyonun bütünüyle ayrıldığı 19 eğitim + 6 kontrol sınamasında RMS 33.000 mm, en büyük 60.632 mm elde edildi. Batı A ucunda taramanın cepheyi yayarak zemini örtmesi nedeniyle kenar sürekliliği komşu açık zeminden yorumlandı; doğrudan ölçülmüş kabul edilmedi. Düzlem, örneklenen x=[−23,−15] ve cepheden en fazla 3 m dışarı alanın ötesine yeni kanıt olmadan uzatılamaz. Dış sur tepesinin bütün kotları bu çalışma ile yeniden kabul edilmiş değildir.

Son kaynak/model karşılaştırmaları `R588_left_join_v020_source_top_final.png`, `R588_left_join_v020_source_oblique_final.png` ile `R588_left_join_v020_model_top_final.png`, `R588_left_join_v020_model_oblique_final.png` ve `R588_left_join_v020_model_glass_final.png` dosyalarıdır. Son eğik ve cam-cephe kontrolünde önceki koyu düşey kopma ile beyaz/yeşil alt yüzey görünümü giderildi. Bu sonuç yalnız düzeltilen temas alanlarının yerel kontrolüdür; bütün müze halkası veya tüm çevre için nihai kabul, birebirlik ya da %100 sonucu değildir.

Doğrulanan geometri sahnesi: `MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v020.blend`; SHA-256 `f0afb8eff89572e49ab849f9cbcfef8d5d05985a953da7d135f8d9a1e746a4e1`. Son temas AO sahnesi, GLB hash/boyutu, tarayıcı sonucu ve yayın durumu `R588_AO_BUILD.json`, `R588_RELEASE_VALIDATION.json` ve `R588_BROWSER_QA.json` içindeki gerçekleşmiş son kayıtlardan alınmalıdır.
