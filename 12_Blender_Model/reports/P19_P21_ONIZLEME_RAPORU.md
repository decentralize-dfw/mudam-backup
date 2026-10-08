# Malzeme, kesit ve taşınabilir önizleme

P19: 014/015/016 gibi fotoğraflardaki saydam camı okuyabilmek için eski koyu önizleme malzemeleri düzeltildi. Cam geçirgenliği, kırılma indisi, pürüzlülük ve genel gündüz ışığı değiştirilebilir görselleştirme parametreleridir. Üretici cam şartnamesi veya kalibre edilmiş aydınlatma hesabı değildir. Taşın yüzeye göre tür/derz çalışması açık; gri granit ile açık taş tek malzemede kesinleştirilmedi.

Malzeme geçişi öncesi ve sonrası mesh koordinatları, yüz indeksleri ve nesne dönüşümleri bağımsız yeniden açmada karşılaştırıldı; geometri korunuyor. Giriş, üst kat boşluğu ve 116 bakışı yeni ışıkla render edildi. 116 için özgün 2000 × 1333 görüntü oranı korundu.

P20: modelin değerlendirilmiş ve görünür meshlerinden yatay kesit çizgileri çıkarıldı. L00: +1,20 m / 114 nesne / 996 parça; LP1: kat üstü +0,90 m / 210 nesne / 1832 parça. Cam ve opak yüzeyler ayrı açılıp kapanır. Çizgiler mevcut koordinat dönüşümüyle 102 ve 103 üzerine oturur; plana veya modele yerel esnetme uygulanmaz. Kaynak çizgiye yakınlık, kesin ölçü doğrulaması değildir. Eski kaba kabuğun Grand Hall çevresindeki sınırları, servis içleri ve birçok açıklık hâlâ çözülmelidir. Kesit aracı bu eksikleri de gösterir; tam kat planı kabulü yapılmadı.

P21: güncel görünür model glTF 2.0 / metre / Y-yukarı düzeninde GLB olarak dışa aktarıldı. 3573 mesh düğümü, 53260 üçgen, yaklaşık 6,6 MB. Blender dışındaki doğrulama, dosya başlığı, gömülü tampon, bütün nesne kimlikleri ve dünya sınırlarının eksen dönüşümünü denetledi. Sınır farkı 0,0 m. Bu, aktarım tutarlılığıdır; binanın gerçek ölçü doğruluğunu kanıtlamaz.

GLB'de genel gökyüzü ışığı yer almaz; cam görünümü görüntüleyicinin transmission desteğine bağlıdır. Hedef motor optimizasyonu, kesit/kat arayüzünün tüm binaya uygulanması ve son mimari doğrulama açık. Ana düzenlenebilir dosya Blender sahnesidir.

R02 güncellemesi: aynı araçlar yeni birleşik sahneye yeniden uygulandı. L00 115 nesne / 1010 kesit parçası; LP1 211 / 1846. Güncel GLB 3578 mesh / 53300 üçgen / 6609192 bayt. Kimlik ve dünya sınırı aktarım denetimi yeniden geçti. Önceki P19 GLB sürümlü olarak korunur.
