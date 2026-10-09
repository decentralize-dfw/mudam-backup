# R41 — ortak mesh verisi

R39 mimarisi korunarak tekrar eden parçalar ortak Blender mesh verisine bağlandı. Nesne adları, element kimlikleri, kaynak/varsayım etiketleri, görünürlük, yüz bağlantıları, malzemeler ve UV koordinatları korundu. Nesneler birleştirilmedi.

Ayrı mesh veri sayısı 6327 → 3449; 3970 nesne yeniden bağlandı. İki dosya bağımsız Blender açılışlarıyla karşılaştırıldı: 7298 nesne, en büyük dünya-koordinatı farkı 0.008754 mm. Bu **sayısal dönüşüm toleransıdır; binanın ölçüm doğruluğu değildir.**

R40 alt pencere denemesi görsel kontrolde reddedildi ve bu sahneye dahil edilmedi. Ayrıntılar [R40 raporunda](R40_KONTROL_RAPORU.md). Diğer mimari belirsizlikler açık sorun kaydında geçerlidir. GLB sonucu ayrı aktarım kontrolünde kaydedilir; hedef motor performansı henüz ölçülmedi.

GLB yeniden doğrulandı:34.622.312→27.142.168 bayt;6.754 nesne ve759.497 üçgen korundu. Yaklaşık%21,6 dosya küçülmesi.
