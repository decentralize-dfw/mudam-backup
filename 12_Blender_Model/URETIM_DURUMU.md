# Mudam - üretim durumu

9 Ekim 2026. Blender 4.2 / metre / EPSG:32632 yerel koordinatlar.

## Güncel teslim

[MUDAM_R47_OKUMA_ISIKLIGI_v002.blend](scenes/MUDAM_R47_OKUMA_ISIKLIGI_v002.blend) giriş, çatı ve merdiven çalışmalarını birlikte içerir. [Görsel inceleme](URETIM.html) · [Üretim raporu](reports/P07_P09_URETIM_RAPORU.md).

| Paket | Durum | Somut çıktı / açık konu |
| --- | --- | --- |
| P00-P01 | Tamam / eksikler belgeli | Kaynak manifesti, üst kat kanıtları |
| P02 | Sürüyor | Kesit tarihi ve izi açık |
| P03 | Tamam | Plan/OSM koordinat aktarımı; ölçme doğruluğu değildir |
| P04 | Sürüyor | Koşullu kat kotları; rıht zinciri açık |
| P05 | Sürüyor | Kabuk ve örtü etütleri; giriş saçağı ve alt cam örtü revize |
| P06 | Sürüyor | 087 / 119 / 116 koşullu kameraları; iç kamera açık |
| P07 | Bölgesel pilot | Girişte ayrı kapalı duvar/saçak/döşeme hacimleri |
| P08 | Bölgesel pilot | Girişte altı açıklık kimliği; cam/çerçeve ayrımı |
| P09 | Kısmi üretim | Üç geniş başlangıç basamağı ve düzeltilmiş üst merdiven yönü |
| P10-P11 | Bölgesel üretim | 794 ayrı cam panel, profiller, doğu gergi katmanı ve geçit; ayrıntılar koşullu |
| P12 | Giriş pilotu | Düz kanatlar, donanımlar, giriş kutusu oran düzeltmesi; mekanizma belirsiz |
| P13-P14, P16, P18 | Açık | Taş/derz, bütün açıklıklar, iç bitişler, arazi |
| P15, P17 | Bölgesel pilot | Okuma alanı döşeme boşluğu, cam korkuluk ve çatı açıklığı |
| P19 | Önizleme | Saydam cam ve genel gündüz ışığı; malzeme/ışık kalibrasyonu açık |
| P20 | Kontrol aracı | L00/LP1 yatay kesitleri plan üzerinde |
| P21 | Ara teslim | GLB aktarımı denetlendi; hedef motor optimizasyonu açık |
| P22 | Açık | Nihai mimari teslim doğrulaması yapılmadı |

## Kontrol sonuçları

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
