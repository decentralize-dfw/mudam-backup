# Mudam - üretim durumu

8 Ekim 2026. Blender 4.2 / metre / EPSG:32632 yerel koordinatlar.

## Güncel teslim

[MUDAM_R03_MERDIVEN_CAM_DONUSU_v003.blend](scenes/MUDAM_R03_MERDIVEN_CAM_DONUSU_v003.blend) giriş, çatı ve merdiven çalışmalarını birlikte içerir. [Görsel inceleme](URETIM.html) · [Üretim raporu](reports/P07_P09_URETIM_RAPORU.md).

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

Üst merdiven tam kol/rıht/sahanlık zinciri; ayrı alt merdiven; galeri duvar/açıklıkları; çatı panel ve taşıyıcıları. Her adımda ilgili plan, kesit/kot ve fotoğraf kimlikleri yeniden karşılaştırılır. Rutin üretim için kullanıcı onayı beklenmez.

Önceki P03/P04/P05/P06/P07 sahneleri `scenes` içinde sürümlü olarak korunur. `build_mudam.py` eski ve kullanılmaz. Yeni betikler mevcut sürümün üzerine yazmayı reddeder.

[Çatı üretim raporu](reports/P10_P11_CATI_RAPORU.md): 3.203 kapalı hacim ve 380 çubuk bağlantısı denetlendi. Pavyon/okuma feneri panelizasyonu, ana iç gergi/gölgeleme ve batı panel düzlemselliği açık.

[Giriş detay raporu](reports/P12_GIRIS_DETAY_RAPORU.md): kapı mekanizması kesinleşmedi; görünen düz cam kanatlar ve donanımlar ayrı üretildi. Rutin onay beklenmez.

[Model-plan kesit kontrolü](PLAN_KONTROL.html) · [Okuma alanı raporu](reports/P15_P17_OKUMA_BOSLUGU_RAPORU.md) · [Malzeme / dışa aktarma raporu](reports/P19_P21_ONIZLEME_RAPORU.md).

[R02 Grand Hall geçit düzeltmesi](reports/R02_GH_GECISI_RAPORU.md): kesintisiz eski cam kaldırıldı, geçide taşan üç etüt duvarı yerel kırpıldı. 15 ışın testi bütün görünür meshleri kapsar; tam oda ve çatı birleşimi kabulü açık.

## R03 üst merdiven ayağı

R03 v003: 022/023 kaynaklı kıvrımlı cam dönüş, yuvarlak küpeşte, taban kanalı, gömme taş alan ve armatür adayı eklendi. Üç başlangıç basamağının küçük sınır kesişimleri onarıldı; kaynak nesneler korundu. 20 kapalı hacim, 65 destek örneği, 12 girinti ışını ve 15 geçit ışını kontrolü geçti. Güncel GLB 7.33 MB, 3595 mesh ve 69812 üçgen.

Tam üst kol, üst sahanlık, eğimli korkuluk devamı ve bütün detay ölçülerinin kesinleştirilmesi açık. [R03 kaynak / varsayım / kontrol raporu](reports/R03_MERDIVEN_DONUS_RAPORU.md).
