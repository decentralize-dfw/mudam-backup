# R107–R109 ek kontrolleri ve açık sınırlar

Bu kayıt geometri üretimi sayılmaz. Geometri düzeltmeleri R107, R108 ve R109 kabul raporlarında ayrı kayıtlıdır.

| Kontrol | Sahne | Sonuç | Sınır |
| --- | --- | --- | --- |
| Küçük üst odalarda duvar dibi döşeme/tavan | R107 | 1.882 örnek, eksik temas yok | Dört oda; kapı açıklıkları ve eksik duvarlar ayrı incelenir |
| Alt galerilerde duvar dibi döşeme/tavan | R107 | 2.988 örnek, eksik temas yok | Alt planın kendi koordinat dönüşümü uygulandı; röleve doğrulaması değil |
| Pavyon iki katta duvar dibi döşeme | R107 | 880 örnek, eksik temas yok | Örtü ve spiral merdiven biçimi bu testin dışında |
| Zemin servis odaları | R107 | 1.622 örnek; 10 tavan adayı | Tüm adaylar üst merdiven basamaklarına/yan duvarına denk gelir; 9 noktada 4,70–4,86 m kotunda geometri var, biri daha yüksek örtü incelemesi gerektirir. 4,35 m düz tavan varsayımı burada otomatik kapanış gerekçesi değildir |
| Ana cam örtü profilleri | R107 | 932 profil / 1.864 uç; temas eksiği yok | Uç kesit örneklemesi; bağlantı donanımı veya statik kabul değil |
| Yan cam örtü profilleri | R107 | 901 profil / 1.802 uç; temas eksiği yok | Eğik kesitli profiller afin koordinat hesabıyla dahil |
| Pavyon cam örtü profilleri | R109 | 216 profil / 432 uç; temas eksiği yok | Pavyonun dikdörtgen profil ailesi |
| Pavyon feneri çapraz çubukları | R109 | 16 uçta mevcut profille temas bulundu | İlk en yakın yüzey hesabındaki iki aday, çubuğun ilk 50 mm bölümünün profil içinde kalmasıyla açıklandı. Çubuklar uzatılmadı |

Üst giriş kesit görünüşü `R107_after_front_cut.png` olarak yeniden üretildi ve PDF2016 ön bölüm planıyla karşılaştırıldı. Kesitte kaldırılan alt kat ve çatı parçaları siyah boşluk olarak görünür; bu, fiziksel bina dışarıya açık demek değildir. Bu görünüş tek başına bütün katın kabulü değildir.

Alt galeri köşeleri için R110 adıyla hazırlanan değişiklik denemesi sahne kaydetmeden durdu: mevcut köşeler zaten R71'de birleştirilmiş, duvar üstleri R89'da döşemeye uzatılmış. R110 model sürümü veya tamamlanmış iş yok. Deneme betiği yalnız yerel `.local_source_cache/rejected_R110` içindedir. Son kabul edilmiş sahne R109'dur.

Plan karşılaştırma PNG'lerinin yazılmasında iki geçici Windows dosya erişim hatası oluştu. Üretici artık önce geçici dosyayı tamamlayıp hedefi tek işlemde değiştirir; kısa ve sınırlı erişim tekrarı sonrası dört R109 karşılaştırması başarıyla üretildi. Bu yazılım değişikliği model geometri düzeltmesi değildir.

## İşaretli bölgelerin güncel görünüşleri

R109 sahnesinden dört dış birleşim ve iki iç mekân görünüşü yeniden üretildi ve açılarak incelendi. Kameralar `R109_marked_render.json` içinde kayıtlıdır; çevre parçaları gizlenmedi. Dış görünüşlerde mevcut cam bağlantıları ve uç duvarları görülür. Bunlar bu pakette eklenmiş geometri değildir. İç görünüşlerde kafe tarafındaki yatay açıklıklar ile doğu merdiveni/duvar ilişkisi hâlâ kaynak karşılaştırması gerektirir; bu görüntüler bütün bölgenin mimari kabulü olarak kullanılmaz.
