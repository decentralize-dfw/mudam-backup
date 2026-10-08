# P05 — ana kabuk etüdü, v002

8 Ekim 2026. Güncel dosya: `scenes/MUDAM_P05_KABUK_v002.blend`. Bu aşama ana bina üzerinde plan, kesit ve fotoğraf karşılaştırmasına temel sağlar; detaylı/as-built model değildir.

## Eklenenler

- Kaynak dış sınırını izleyen ana cephe yüzeyleri ve giriş girintisi.
- Zemin/üst galeri bölgeleri, üst köprü ve stüdyo; alt galeri/fuaye/oditoryum bölgeleri.
- Zemin döşemesinde aşağı inen merdivene ait gerçek boolean boşluğu. Üst kat hol boşluğuna döşeme doldurulmadı.
- Ana çatı ve fener kütlesi; doğuda düz, batıda eğrisel cam örtü yüzeyleri. Yüksek kenarlar galeri tarafında, alçak saçaklar V'nin dış kenarında tutuldu.
- Galeri ışıklık ve ana hol açıklıkları çıkarılmış çatı döşemesi etüdü.
- Üst galerilerde kuzeye bakan cam düzlemleri ve eğrisel beton örtü biçimi denemesi.
- Pavyon bağlantı geçidi ve pavyon duvarında geçiş açıklığı.
- Yukarı ve aşağı merdiven için ayrı renkli bağlantı hatları. Bunlar basamak geometrisi değildir.

## Yeni üst kat kaynakları

[Tim Culbert / tamamlanmış galeriler](https://imreyculbert.blogspot.com/2007/10/photographs-of-completed-luxembourg.html), 5 Ekim 2007: UG01 dış cephe, UG02–UG03 galeri ışıklıklarının iç görüntüleridir; fotoğraf kredisi Thomas Mayer. UG02–UG03 yalnız 150×100 piksel olduğundan genel biçim için kullanılır; profil/derz ölçmek için kullanılmaz. Metin galerilerin eğrisel beton örtülerini ve kuzey ışığı kullanımını açıklıyor.

[Tim Culbert / yapım kaydı](https://imreyculbert.blogspot.com/2007/10/luxembourg-museum-gallery-opens.html): UC01–UC02, beton çatı kabuklarının yapım/yerleştirme görüntüleridir. Kaynak bunları Kasım 1999 yapımına bağlar ve üst galerilerin duvarlarını 6 metreden yüksek olarak anlatır. Metindeki açılış tarihi diğer kurumsal kayıtlarla farklıdır; modelin tarihsel durumu buna dayanarak değiştirilmedi.

Beş dosya kaynak URL, kredi ve SHA-256 ile `references/upper_gallery_2007/manifest.json` içinde kayıtlıdır. Eski 105 fotoğrafın kamera atlasına doğrulanmış konum gibi eklenmedi.

## P02/P04 karşılaştırması

084 kesitindeki okunabilir yatay hatlar yaklaşık zemin y=149, üst döşeme y=129, alt döşeme y=170, ana çatı tepe y=26 piksel olarak alındığında üst/alt kat aralık oranı yaklaşık 20/21 olur. 101 üzerinden kullanılan koşullu kotların oranı 4,86/5,33≈0,91'dir. 084'ün düşük çözünürlüğü ve ±2 piksel okuma duyarlılığı içinde bu bir oran tutarlılığı kontrolüdür; bağımsız metre ölçüsü değildir. İki kesitin farklı yönleri/tarihleri ve kesin plan izleri hâlâ açık.

021/022, geniş merdivenin alt başlangıcını ve yukarı doğru kolunu; 051/115, alt fuayeye inen kesintisiz eğrisel kolu destekliyor. Gizlenen basamaklar nedeniyle tam rıht sayımı kapanmadı. P02/P04 tamamlandı olarak işaretlenmedi; P05 sadece bu koşullu değerlerin bütün bina üzerindeki sınamasıdır.

## Geometrik kontrol

Dosya yeni Blender işlemi içinde açıldı. 310 yeni mesh nesnesinde sıfır alanlı yüz bulunmadı. 20 görsel paketli; negatif nesne ölçeği yok. Aşağı merdiven kesicisi zemin döşemesinden 10,64 m³ **etüt geometrisi** çıkarıyor; düşey ışın testi boşluğun açık, komşu döşemenin mevcut olduğunu doğruladı. Pavyon bağlantı cephesindeki engelleyici yüz kaldırıldı. [Makine kontrolü](P05_verification.json).

Bu testler mimari doğruluk veya fotoğraf eşleşmesi testi değildir. Üç kontrol kamerası tasarım inceleme kameralarıdır; metrik fotoğraf kameraları değildir.

## Açık geometri işleri

1. Ana örtünün asimetrik alt yüzeyleri, taş/cam sınırları ve düşey cam yarığı. Şu an tek kütle hipotezi var.
2. Galeri ışıklıklarının gerçek sayısı, aralıkları ve kesitleri. Beş tekrar yalnız biçim etüdüdür.
3. Batı cam merdiven çıkıntısı, giriş/dokümantasyon bölgesindeki küçük ışıklık ve ana holün taş duvar kırıkları.
4. Galeri pencere boşlukları, kapı ailesi ve giriş portalinin kesin genişlik/yüksekliği. Giriş başlık oranı 0,60 çalışma varsayımıdır.
5. Kat/döşeme kalınlıkları, merdiven rıhtları ve sahanlıkları; taşıyıcı/cam/çelik detayları.
6. Arazi, tarihî duvar ve alt kat çevre kabuğu. Alt döşemelerin görünmesi tamamlanmış dış cephe anlamına gelmez.

Sonraki adım: 116/119/087 görüntüleriyle ana çatı ve cephe silüetinin eşleştirilmesi; ortak geometri üzerinde ilk kamera pilotu. Bu düzeltmeler kapanmadan P07 detaylı duvar üretimine geçilmez.
