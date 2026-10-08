# Mudam - üretim durumu

8 Ekim 2026. Blender 4.2 / metre / EPSG:32632 yerel koordinatlar.

## Güncel teslim

[MUDAM_P09_MERDIVEN_v004.blend](scenes/MUDAM_P09_MERDIVEN_v004.blend) giriş, çatı ve merdiven çalışmalarını birlikte içerir. [Görsel inceleme](URETIM.html) · [Üretim raporu](reports/P07_P09_URETIM_RAPORU.md).

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
| P10-P22 | Başlamadı | Detay paketleri tamamlanmış sayılmıyor |

## Kontrol sonuçları

P07: 164 yeni mesh / 67 kapalı hacim kontrol edildi; sıfır alanlı yüz yok. Kapı geçişi üç yükseklikte açık. Üç kamera aktarımı 0,009 px altında. [P07 yeniden açma kontrolü](reports/P07_verification.json).

P09: üç başlangıç basamağı, kot katmanları, yukarı/aşağı yönlerinin ayrılması ve paketli fotoğraflar yeni Blender sürecinde denetlendi. [P09 yeniden açma kontrolü](reports/P09_verification.json).

Üst merdivenin eski P05 kılavuz yönü tersti; düzeltildi. 049/050 ile ilişkili aşağı merdiven ayrı tutuluyor. Ziyaretçi şemasının çizgi sayısı gerçek rıht sayısı sayılmadı.

## Ölçü durumu

Ana kabuk henüz bütün bina düzeyinde kabul edilmedi. OSM uyum RMS'si yaklaşık 1,02 m, iki bağımsız kontrol RMS'si 1,91 m; source-plan ölçeği bu sınırlarla kullanılıyor. Kat kotları, saçak, profil ve kalınlık parametreleri koşullu. Sahnedeki büyük bölüm `90_UNCERTAIN_OR_PROXY` altında; fiziksel imalat doğruluğu iddiası yok.

## Sıradaki üretim

Üst merdiven tam kol/rıht/sahanlık zinciri; ayrı alt merdiven; galeri duvar/açıklıkları; çatı panel ve taşıyıcıları. Her adımda ilgili plan, kesit/kot ve fotoğraf kimlikleri yeniden karşılaştırılır. Rutin üretim için kullanıcı onayı beklenmez.

Önceki P03/P04/P05/P06/P07 sahneleri `scenes` içinde sürümlü olarak korunur. `build_mudam.py` eski ve kullanılmaz. Yeni betikler mevcut sürümün üzerine yazmayı reddeder.
