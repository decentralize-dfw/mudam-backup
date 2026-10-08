# P06 — ana örtü ve fotoğraf kontrolü

8 Ekim 2026 · Güncel çalışma: `scenes/MUDAM_P06_CATI_KONTROL_v002.blend`.

**Durum: kısmi etüt; kabuk kabul edilmedi.** Bu sürüm ana çatının ilk taslağındaki tek seviyeli yüzey düzenini düzeltiyor. Kamera 119 koşullu kontrol kamerasıdır; atlasın doğrulanmış konumlarına aktarılmadı. Ana örtü dışındaki bina hâlâ P05 etüdüdür.

## Kaynakların çapraz kontrolü

| Kaynak | Kontrol | Sonuç / sınır |
| --- | --- | --- |
| 102 zemin şeması | Ana hacmin dış izdüşümü ve kanatlarla ilişkisi | 462–688 / 334–560 kanonik piksel sınırı korundu; kaynak şema çatı rölövesi değildir. Köşe şeridi ve fener izi koşullu. |
| 101 mimari kesit | İki saçak, iki omuz, fener ve tepe | y=287/247 saçak; y=210/170 omuz; y=131 fener üstü; y=111 tepe. Kesitin tarihi/izi çözülmediği için metre karşılıkları koşullu. |
| 119 cam cephe | Silüet ve çatı köşeleri | 7 nokta ile kamera hesabı; 4 omuz noktası hesap dışında kontrol; ayrıca iki yan kanat kontrolü başarısız. |
| 116 yüksek giriş bakışı | Yüksek taraftaki örtü, yükselen taş duvar, aradaki cam şerit | Biçim yönünü destekliyor; kamera eşleştirmesi yapılmadı. Kesin fener köşe karşılıkları ve alt bağlantılar açık. |
| 026 Grand Hall | Alt eğimli örtü, düşey cam ve taş duvar ilişkisi | Alt sistemin tek düşey cam prizma olmadığı görülüyor. P05 alt kabuk henüz düzeltilmedi; bu bölge detaya geçirilemez. |

Bu sürümde plan görüntüleri, OSM dönüşümü ve katların yatay konumları değiştirilmedi. Yapıyı fotoğrafa uydurmak için plan esnetilmedi.

## Geometri değişikliği

Ana örtü iki saçak/omuz seviyesine ayrıldı; dört ana eğimli yüzey, aradaki dar cam yüzeyler, fener ve tepe ayrı nesnelerdir. Giriş tarafındaki yüksek saçak altına iki taş yüzey ve bir cam şerit etüdü eklendi. Eski çatı gizlendi; P05 dosyası korundu.

Kesit oranından düşük/yüksek saçak yaklaşık 13,92 / 17,66 m, düşük/yüksek omuz 21,12 / 24,86 m çıkar. Bunlar ölçülmüş kotlar değildir. Fenerin 40 kanonik piksel toplam genişliği ile 34 piksel düz köşe şeritleri fotoğraf biçimine dayanan adaylardır; ölçülü paftadan okunmadı. Yapısal kalınlık, çelik profil ve cam panel örgüsü üretilmedi.

## Kamera hesabı ve sapmalar

Geometri sabit tutularak 7 kamera parametresi çözüldü. Görüntü 1600×754; ana nokta görüntü merkezinde kabul edildi. Kırpma, özgün odak bilgisi ve lens bozulması bilinmiyor. Elle seçilen noktaların okuma hassasiyeti yaklaşık 3 pikseldir; yanlış köşe eşleştirmesi belirsizliği buna dahil değildir.

| Kontrol | Eski çatı | Yeni aday |
| --- | ---: | ---: |
| Kamera hesabındaki 7 nokta RMS | 12,11 px | 8,56 px |
| Hesap dışındaki 4 omuz noktası RMS | 39,22 px | 6,03 px |

Eski adayın en iyi bulunan kamerası arama sınırındaki 35 m uzaklığa dayanıyor; bu karşılaştırma mutlak en iyi çözümlerin kanıtı değildir. Omuzlar aynı fotoğraftadır; bağımsız fotoğraf doğrulaması sayılmaz.

**Yan kanat kontrolü başarısız:** aynı kamera değiştirilmeden batı yüksek taş duvar ucu yaklaşık 54,7 px, doğu ucu yaklaşık 88,1 px sapıyor. Bu noktaların yükseklik/konum karşılığı da aday olduğundan hata yalnız kamera ya da yalnız geometriye yüklenemez. Ana çatı uyumu bütün binanın kabulü için yeterli değildir. Ham seçimler ve sonuçlar `P06_camera_fit_119.json` içindedir.

## Kaydedilmiş Blender dosyasının denetimi

Dosya yeni Blender işleminde açıldı: 27 yeni mesh, sıfır alanlı yüz yok, negatif nesne ölçeği yok; çatı üst yüzleri yukarı bakıyor. Çatı–fener–tepe arasındaki 32 köşe eşleşmesinde boşluk 0 m. Fotoğraf kamera arka planına paketli. Blender projeksiyonu ile hesap betiği arasındaki en büyük fark 0,0104 pikselin altında. Bu, yazılım aktarımını denetler; binanın ölçü doğruluğunu kanıtlamaz. Ayrıntı: `P06_verification.json`.

## Sonraki düzeltme sırası

1. 116 ve 087 için güvenilir köşe eşleşmeleri kur; kanat uçlarıyla birlikte ortak kamera/kabuk kontrolü yap.
2. Yan kanat yüksek kenarları, alçak saçaklar ve ana örtü altındaki eğimli cam yüzeyleri çöz. Taş/cam sınırlarını 026 ve dış fotoğraflarla bağla.
3. Plan/kesit/fotoğraf uyumu sağlanan bölgeyi kabul et; ancak o bölgede duvar, kapı, basamak, korkuluk ve çelik detayına geç.

Her yeni modelleme adımı için plan kaynağı, kesit/kot dayanağı, fotoğraf kimliği, yapılan değişiklik ve kalan çelişki kaydedilecek. Kaynağı eksik eleman “doğrulanmış” yapılmayacak. Referans belirsizliği yeni üretimin içinde kaybolmayacak.
