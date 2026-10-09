# P20 · Canlı model incelemesi

9 Ekim 2026. [İnceleyiciyi aç](../MODEL_INCELEME.html).

R47 v002 GLB üzerinde üç kat aralığı, yatay kot kesimi ve iki düşey kesim yönü eklendi. Düzlemin tarafı ters çevrilebilir. Bütün katlarda devam eden nesneler kot aralığında kırpılır; bunlar gerçek BIM kat sınıflandırması değildir. Alt kat −5,65…−0,30; zemin −0,30…4,60; üst kat 4,60…10,05 m çalışma aralıklarıdır. Sınırlar mevcut model kotları etrafındaki inceleme paylarıdır, kaynakta ölçülmüş değerler değildir.

Parçalar tıklamayla veya ad aramasıyla seçilir. Kaynak görselleri, Blender özel özellikleri, konum/detay güveni ve R26–R47 paket kayıtları gösterilir. Camın arkasını seçme anahtarı, tek parça görünümü ve yakınlaşma bulunur. Kesilen yüzler seçim ışınından da elenir; vurgu kutusu tıklama engeli oluşturmaz. Genel, üstten ve güneyden görünüşler ile çevre/kenar çizgisi anahtarları vardır.

## Kontroller

- R47 aktarımı ve P21 doğrulamasının aynı dosyayı göstermesi zorunlu. Başarısız veya eksik doğrulama yüklemeyi durdurur.
- Tarayıcıda 6.782 model nesneli 30,6 MB GLB yüklendi. Yükleme/hazır durumları ve hata mesajı vardır. Sayfa modeli değiştirmez.
- Üst, zemin ve alt katlar; yatay ve düşey kesit ile ters yön görsel olarak denetlendi. Alt kat −3,80 m kesitinde, kesilmiş tavan yerine `R29_W_FLOOR` tıklamayla seçildi.
- `R45_STONE_GRIP_FINISH_CANDIDATE` arama/seçme/yalıtma/yakınlaşma ve kaynak 023/024 bağlantıları denetlendi.
- Node kontrolü kat bantlarını, Blender Z → glTF Y dönüşümünü, kuzeyin −Z işaretini ve kesilmiş yüzlerin seçimden elenmesini kontrol eder.
- Kullanılan Three.js r180 ve MIT lisansı yerel `assets/vendor/three` klasöründedir. Resmî depo URL'leri ve SHA-256 kayıtları manifestte yer alır. Çalışma sırasında üçüncü taraf CDN gerekmez.

## Sınırlar

Kesitler kapaksız yüzey kırpmasıdır. Ekrandaki karanlık/boş kesim kenarı bina açıklığı olarak yorumlanamaz. Perspektif üst görünüş ölçü alınacak ortografik plan değildir; plan kontrolü sayfası ayrı kalır. Web önizlemesinde gölge/ışık görünümü Blender renderından farklıdır. Eski parça notları güncel revizyondan önce yazılmış olabilir. Bilinmeyen kaynak kimlikleri bağlantı uydurulmadan gösterilir. Bu araç modelin mimari doğruluğunu tek başına kabul etmez.
