# Mudam Blender üretim şartnamesi

Bu şartname yazılım sürümünden bağımsız sahne sözleşmesidir. Kullanılacak Blender sürümündeki modifier, malzeme ve dışa aktarma davranışları ilk üretim oturumunda küçük bir örnekte doğrulanır. Ana `.blend` dosyası henüz oluşturulmadı.

## Koordinat ve birim sözleşmesi

1 Blender birimi = 1 metre. Uzunluk metre olarak saklanır; detay arayüzünde gerekirse milimetre gösterilir. Dünya X doğu, Y kuzey, Z yukarıdır. Büyük UTM sayıları geometri koordinatı olarak kullanılmaz; proje yerel orijine kaydırılır.

Mevcut atlasla bağlantı:

```text
UTM CRS = EPSG:32632
E0 = 293425.0 m
N0 = 5499960.0 m
Blender X = Easting - E0
Blender Y = Northing - N0
Blender Z = ilgili bitmiş/taşıyıcı kot - zemin bitmiş kotu
Atlas x_m = Blender X
Atlas y_m = -Blender Y
```

Atlasın ekran Y ekseni aşağı yönlüdür; bu işaret değişimi atlanırsa model kuzey–güney yönünde aynalanır. Kaynak PNG ayrıca elle döndürülüp dünya dönüşümü ikinci kez uygulanmaz. PNG/PGW/PRJ dönüşümü ya da canonical SVG dönüşümü seçilir; ikisi üst üste kullanılmaz.

PGW piksel merkezini, SVG dönüşümü sürekli resim koordinatını tarif eder; yarım piksel farkı dikkate alınır. Her içe aktarma iki uzak kontrol köşesi ve bir yön kontrolüyle sınanır. Zemin Z=0 yerel seçimdir; mutlak yükseklik henüz bilinmiyor. Kuzey UTM grid kuzeyidir; güneş/gerçek azimut için yakınsama farkı ayrı ele alınır.

## Koleksiyon düzeni

```text
MUDAM
  00_REFERENCE_LOCKED
    PLANS_LM1_L00_LP1
    SECTIONS
    OSM_AND_SITE
    PHOTO_MATCH
  01_DATUMS_AND_AXES
  02_STRUCTURE
    LM1 / L00 / LP1 / MULTILEVEL
  03_ENVELOPE
    STONE / OPENINGS / GLAZING
  04_ROOFS
    MAIN / EAST / WEST / PAVILION / LINK
  05_INTERIORS
    LM1 / L00 / LP1
  06_CIRCULATION
    STAIRS / RAILINGS / LIFT
  07_SITE
    TERRAIN / HISTORIC_WALLS / PATHS / LANDSCAPE
  08_FIXED_FITTINGS
    LIGHTS / VISIBLE_SERVICES / SIGNAGE
  09_TEMPORARY_EXHIBITIONS
  10_CAMERAS_AND_LIGHTING
  90_UNCERTAIN_OR_PROXY
  91_COLLISION
  92_EXPORT_DERIVED
  99_QA
```

Bir nesnenin tek sahibi vardır. Kat/sistem gibi ikincil sınıflandırmalar özelliklerle tutulur; aynı geometri yanlışlıkla iki kez dışa aktarılmaz. Çok katlı duvarın veya merdivenin hangi kat gizleme durumunda görüneceği ayrı `visibility_group` alanında tanımlanır. Yapı fiziğiyle sunum koleksiyonu karıştırılmaz.

## Nesne adları ve özellikleri

Örnek ad: `MUD_L00_GH_RAIL_003_MASTER`. Kat kodları `LM1`, `L00`, `LP1`; geçici teknik hacimler `TECH_UNVERIFIED`. Bölge kodları `ENT`, `GH`, `EAST`, `WEST`, `PAV`, `LINK`, `AUD`, `SITE`. Adın içine kesinleşmemiş ölçü gömülmez.

Her mimari nesnede şu özellikler bulunur:

```text
element_id, element_type, zone_id, level_id
source_ids, source_date, permanent_or_temporary
confidence_xy, confidence_z, confidence_detail, confidence_material
parameter_ids, assumption_note, status
visibility_group, export_group, collision_role
```

Değerler görünür nesnede tutulur; yalnızca üretim betiğinde saklanmaz. Referans kimlikleri manifestte gerçek dosyaya çözülür. Eksik kanıt boş metinle saklanmak yerine `unknown` veya `unresolved` olarak belirginleştirilir.

## Dosya ve sürüm düzeni

```text
12_Blender_Model/
  scenes/MUDAM_MASTER_v001.blend
  modules/structure.blend
  modules/roofs.blend
  modules/interiors.blend
  assets/doors/ windows/ railings/ materials/
  scripts/
  config/
  textures/
  renders/qa/ presentation/
  exports/high/ realtime/
  reports/
```

Bu dizin bir sonraki üretim aşamasının hedefidir; şu an varmış gibi kabul edilmez. Ana modelin editable sürümü saklanır. Modüller ihtiyaç arttıkça ayrılır; ilk oturumda gereksiz dosya parçalanması yapılmaz. Her ana geometri değişikliğinden önce sürüm kaydı alınır; orijinal kaynaklara yazılmaz.

Üretim betikleri tekrar çalıştırıldığında yalnızca kendilerine ait koleksiyon/kimlikleri günceller. Kullanıcı tarafından elle değiştirilmiş nesneler otomatik silinmez. Parametre, geometri üretimi, malzeme ve dışa aktarma işlemleri ayrı tutulur. Taslak geometriyi yeniden üretmek, dokuları veya elle düzeltilmiş kapıları kaybettirmemeli.

## Parametrik üretim kuralları

- Kotlar tek veri tablosundan okunur. Duvar yüksekliği, döşeme üstü, merdiven toplam yükselmesi ve kapı başı aynı datumlara bağlanır.
- Duvar gövdesi, kaplama ve açıklık tarifleri ayrıdır. Boolean sonucu gerekiyorsa kaynak açıklık nesnesi korunur.
- Tekrarlı kapı, profil, cam panel ve tutucular bağlı kopya/instance olabilir. Gerçek tip farkı varsa ayrı aile açılır.
- Eğri tabanlı korkuluk ve profil üretiminde yerel eksenler ve kesit yönü test edilir; negatif ölçekle ters normal bırakılmaz.
- Ölçü değiştiğinde bağlı detaylar güncellenir; elle rastgele sürüklenmiş kopyalar oluşmaz.
- Taş dizisi ve panel örgüsü sınır panellerini de üretir; son sıradaki taş/cam duvardan taşmaz.
- Sadece uygulama için kopyalanmış dışa aktarma nesnelerinde modifier uygulanır. Ana modelde düzenlenebilir tarif korunur.

## Malzeme ve geometri disiplini

Yüzey normalleri, iç/dış yönler ve çakışık yüzeyler her sistem tamamlanınca kontrol edilir. Kapalı duvar, döşeme ve cam hacimleri için manifold geometri hedeflenir; bilerek açık referans yüzeyleri ayrı işaretlenir. İnce profil kenarlarında bevel gerçek ölçüye bağlıdır; bütün sahneye aynı rastgele bevel değeri uygulanmaz.

UV ve doku ölçeği fiziksel boyutlarla kaydedilir. Bir taş levhaya uygun doku büyüklüğü model ölçeği değişince sessizce değişmez. Materyal testleri önce nötr sahnede, sonra bina ışığında yapılır. Render odaklı shader ile web uyumlu shader aynı sonucu vermeyebilir; ikisi ayrı türev olarak yönetilir.

Cam için kalınlık, çerçeve, kenar ve optik davranış ayrı kontrol edilir. Şeffaflık sıralaması, üst üste yüzeyler ve gölge davranışı hedef motorda denenir. Cam arkasındaki elemanların kaybolması geometri eksikliği mi render sorunu mu ayrılır.

## Kat gizleme ve kesit

Modelde her katı ayırmak, nesneleri gelişigüzel Z yönünde taşımakla yapılmaz. Ayrıştırma için dönüşümler kayıtlıdır; sıfırlama bütün katları esas datumlara döndürür. Çok katlı öğelerin görünürlük kuralı açık bir tabloda tutulur.

Kesit düzlemi ana geometriyi tahrip etmez. Duvar, kaplama, döşeme ve çatı malzemeleri kesitte doğru ayrılır. Kesit kapağı tüm hacmi tek bir siyah yüzeye çevirmemeli. Kaynağı bilinmeyen iç katmanlar kesitte görünür olduklarında 'temsilî' durumları da aktarılır. Kapı/pencere boşlukları kesit kapatma işleminde yanlışlıkla doldurulmaz.

Test durumları: yalnızca 0; yalnızca +1; yalnızca −1; tüm katlar; çatı kapalı/açık; yatay kesit; ana merdivenden düşey kesit; pavyondan kesit. Her durumda havada kalan donanım, kaybolan bağlantı ve yanlış kapatılmış boşluk aranır.

## Performans ve dışa aktarma

Ana detaylı model, görsel ayrıntıyı korur. Web/dolaşım türevi ayrıca üretilir. Polygon veya doku bütçesi donanım görülmeden kesin sayı olarak dayatılmaz; üç örnek detay bölgesinde ölçülür. İlk rapor üçgen, draw call karşılığı materyal/nesne sayısı, doku belleği, dosya boyutu ve hedef cihazdaki kare süresini içerir.

Uzak ayrıntıda küçük cıvata/derzler haritaya aktarılabilir; çatı silüeti, pencere derinliği ve merdiven profili korunur. Çarpışma geometrisi ayrı ve basittir. Geçici sanat eserleri ve bitki örnekleri ana bina performans ölçümünden ayrı raporlanır.

Planlanan teslimler: `.blend` ana dosya; hedef ortam uygunsa `.glb` türevi; isteğe bağlı başka formatlar için ayrı doğrulama. Bir dosyanın açılması tek başına başarılı aktarım değildir: metre ölçeği, eksen, materyal, cam, UV, instance ve görünürlük kontrol edilir. Özel Python mantığının veya modifier'ın hedef motorda çalışacağı varsayılmaz.

## Son kontrol paketi

Her sürüm tesliminde aşağıdakiler üretilir:

1. Üç katın ortografik üst görünüşü ve kaynak bindirmesi.
2. Dört ana yönden dış görünüş ve çatı planı.
3. Grand Hall, ana merdiven ve pavyonu açıklayan kesitler.
4. Aynı kameralardan alınmış referans/model karşılaştırmaları; kaynak görüntü değiştirilmeden.
5. Kapı, pencere, çelik/cam, korkuluk ve taş birleşimi yakın görünüşleri.
6. Nesne kapsam ve belirsizlik raporu; açık parametreler.
7. Eksik doku, çakışık yüzey, normal, ölçek ve dolaşım kontrolleri.
8. Temiz oturumda dosya yeniden açma ve dışa aktarma geri yükleme kontrolü.

Sunum görüntüleri ile teknik kontrol görüntüleri ayrı saklanır. Teknik kontrol görselinde dramatik ışık, sis veya yoğun alan derinliği geometrik hatayı gizlememeli.
