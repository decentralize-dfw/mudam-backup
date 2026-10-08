# R03 — Üst merdiven ayağı ve cam dönüş detayı

8 Ekim 2026. Güncel birleşik sahne: `../scenes/MUDAM_R03_MERDIVEN_CAM_DONUSU_v003.blend`.

Bu paket tam merdiven teslimi değildir. 021/022/023 fotoğraflarında görülen başlangıç detayı üretildi. Tam kol, üst sahanlık, eğimli korkuluk devamı ve merdivenin duvar oyuğu açık. 049/050 aşağı inen merdivene aittir; bu pakette üst merdiven kaynağı olarak kullanılmadı.

## Kaynakların söylediği ve söylemediği

| Kaynak | Gözlenen veri | Sınır |
|---|---|---|
| 021 | Üç geniş başlangıç basamağı, yukarı uzanan cam korkuluk, taş yan yüzey ve büyük duvar oyuğu | Tam rıht sayısı görünmüyor; metrik kamera çözülmedi |
| 022 | Kıvrımlı cam dönüşün üçüncü basamak üzerindeki ilişkisi; metal üst küpeşte ve taban profili | Kesin yarıçap, yükseklik ve panel bölünmesi yok |
| 023 | Yakın çekimde düşey cam ekleri, yuvarlak metal küpeşte, koyu taban kanalı, yuvarlak gömme zemin armatürü ve çevresindeki taş girinti | Gizli bağlantı, cam şartnamesi, elektrik ve taşıyıcı detay çıkarılamaz |
| PDF2016 sayfa 5, 102, 103 | Üç basamağın plan konturları ve kol yönü | Ziyaretçi şemasının seyrek basamak çizgileri gerçek rıht sayısı değildir |
| 101 | Önceki çalışmanın koşullu kat yüksekliği referansı | Üst merdiven sahanlığı kısmen örtülü; kesit doğrultusu ve gerçek kotlar kesinleşmedi |

Kaynak dosyalarının yolu ve SHA-256 değerleri `R03_source_receipt.json` içinde. Özgün dosyalar değiştirilmedi. Üst kat plan kırpması `../references/R03_upstairs_LP1_crop.png` ve yerleşim karşılaştırması `../references/R03_plan.svg` içinde.

## Üretilen geometri

Üç ayrı kıvrımlı cam panel adayı, kesintisiz yuvarlak küpeşte, panel başına iç/dış dudak ve alt gövdeden oluşan taban kanalı, taş basamakta gerçek girinti, armatürün koyu çerçevesi, cam merceği ve görünen yuva yüzeyi ayrı nesnelerdir. Gizli ankraj ve elektrik parçaları üretilmedi.

Cam dönüşü yaklaşık dairesel bir yay olarak kuruldu. Fotoğrafta yarıçapı değişen bir kıvrım olabilir; bu geometri kesin imalat biçimi değildir. Eğimli küpeşteye geçiş açık uç olarak bırakıldı; bitmiş korkuluk gibi kabul edilmemeli.

| Parametre | Aday değer | Dayanak |
|---|---|---|
| Merkez | 102/103 koordinatında 493, 498 | Kaynak konturlu üçüncü basamağın içinde; fotoğraf pozu ile doğrulanmadı |
| Yay yarıçapı / tarama | 0,62 m / 280° | Fotoğraf oranı; değiştirilebilir |
| Küpeşte yüksekliği | Basamak üstünden 1,05 m | Ölçülmemiş oran varsayımı |
| Cam kalınlığı / panel sayısı | 16 mm / 3 | Temsilî; gerçek ürün ve panel sayısı bilinmiyor |
| Küpeşte çapı | 45 mm | Temsilî kesit |
| Gömme taş alan | 0,55 m yarıçap / 50 mm derinlik | 023 görünümüne dayalı aday |
| Armatür dış / cam yarıçapı | 0,18 / 0,125 m | Fotoğraf oranına dayalı aday |

Bütün parametreler `../config/stair_glass_return.json` içinde. OSM tabanlı yatay ölçek ve kesitten türetilen kotlar önceki belirsizliklerini koruyor; milimetrik doğruluk iddiası yok.

## Geometri hatası ve düzeltme

İlk R03 v001 kontrolünde Boolean kesme, armatürün üzerini kapatan ters hacim üretti. İnceleme, eski üç basamağın PDF ön çizgisi ile ortak duvar eğrisini birleştiren kapanışlarında küçük, kendini kesen halkalar buldu. Önceki manifold/pozitif hacim kontrolleri bu hatayı tek başına yakalayamamıştı.

Her kapanış, iki çizginin gerçek kesişiminde kesilip küçük halka çıkarılarak düzeltildi. Atılan alanlar sırasıyla yaklaşık 0,0181, 0,0273 ve 0,0122 kanonik piksel². Basamakların fotoğrafla ilişkili ana konturları ölçeklenmedi. Eski kaynak nesneleri saklı tutuldu; yeni düzeltilmiş nesneler onların yerine görünür. v002 yalnız üçüncü basamağı düzeltti; v003 aynı kontrolü üçüne uyguluyor. Önceki denemeler yerel arşivde, yayımlanan sahne v003.

## Yeniden açma ve görünürlük kontrolleri

- 20 değerlendirilmiş kapalı hacim: pozitif hacim, manifold kenarlar, sıfır alanlı yüz yok.
- Üç plan sınırı: kendini kesme yok; üst yüz normal yönleri doğru.
- Cam tabanının 65 örnek noktası kaynak üçüncü basamağın üzerinde.
- Bütün görünür sahnede 12 düşey ışın: mercek, taş girinti ve dış basamak yüzeyi doğru yükseklikte ilk temas; eski yüzey onları örtmüyor.
- Önceki sahnenin 3819 kaynak meshinin geometri ve dönüşümleri değişmedi. Üç eski basamak gizlendi, düzeltilmiş kopyaları görünür.
- R02 geçidinin bütün görünür meshleri kapsayan 15 yerel ışın kontrolü tekrar geçti.

Ayrıntılı sonuç: `R03_verification.json`. Önizleme `../renders/qa/R03_stair_return.png`, çevredeki tamamlanmamış parçalar gizlenerek alınmış bir **bileşen görünümüdür**; fotoğrafla eşlenmiş tamamlanmış iç mekân değildir. Saydam cam ve metal genel önizleme malzemeleridir; taş doku/derz ve ışık eşlemesi açık.

## Tam merdiven için sonraki çözüm

Üst planın daralan basamak çizgilerinin üst döşeme tarafından örtülmeyi mi, fiziksel kol daralmasını mı gösterdiği çözülmeden bu çizgiler gerçek rıhtlara dönüştürülmemeli. Üst bağlantı, duvar oyuğu ve eğimli taş yan yüzey birlikte ele alınmalı. Rıht sayısı için seçilecek her aday, koşullu kat yüksekliği ve yürüyüş uzunluğuyla karşılaştırılmalı; aday sayı gözlenmiş sayı olarak sunulmamalı.

Yeniden açılmış doğrulanmış sahneden ikinci görünüm: `../renders/qa/R03_podium_overview.png`. Üç basamakla cam dönüşünün plan içindeki ilişkisi bu görüntüde ayrıca incelendi. Güncel P20 kesitleri R03 v003 sahnesine ait; L00 118 nesne / 2174 segment, LP1 211 nesne / 1846 segment. GLB bağımsız denetimi: 3595 mesh, 69812 üçgen, 7.325.788 bayt, aktarım sınır kutusunda fark 0 m. Bu sonuç mimari ölçü doğruluğu anlamına gelmez.
