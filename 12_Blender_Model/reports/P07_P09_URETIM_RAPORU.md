# P06-P09 üretim kontrolü

8 Ekim 2026. Güncel dosya `reports/P09_build_report.json` içinde kayıtlıdır. Son dosya giriş, çatı ve merdiven çalışmalarını birlikte içerir; önceki sahneler korunur.

## Üretilenler

- **P06:** 119 ve 087 için ana çatı + kanat uçlarından koşullu kamera hesabı; karşı yöndeki 116 için ayrı kamera. Üç fotoğraf Blender kameralarına paketlendi. Önceki yalnız çatıya dayanan kameranın yan kanat sapması, geometri esnetilmeden yeniden değerlendirildi.
- **Giriş kabuğu / P07 pilotu:** plandaki üçgen saçak ile geri çekilmiş giriş cephesi ayrıldı. Saçak, köşe desteği, döşeme, cephe yan parçaları, pencere üstleri ve ara kirişler ayrı kapalı hacimlerdir. Döşeme ve tavan, üç yüzlü geri çekilmenin tamamına uzatıldı.
- **Açıklıklar / P08 pilotu:** üç cephe yüzünde alt/üst toplam altı açıklık kimliklendirildi. Camlar, önizleme çerçeveleri ve taş kabuk ayrı nesnelerdir. Ortadaki giriş geçişi camla kapatılmadı. Cam giriş kutusunun yanları ve üstü var; döner kanatlar ve mekanizma henüz yok.
- **Alt cam örtü:** ana örtünün altındaki cam bant, iki eğimli yüzey, taş üçgenler ve orta cam şerit ayrıldı. Eski döşemenin camların önüne taşıyan üçgen parçaları, atrium boşluğu kare plan sınırına genişletilerek kaldırıldı. Bu çatı değişikliği mevcut alt merdiven boşluğunu değiştirmez.
- **Yan cam salonlar:** önceki rastgele üst kat +0,8 m saçak kotu kaldırıldı; fotoğrafa dayanan koşullu kot adayları kaydedildi. Batı örtüsünün eğrisel dış plan sınırı ve düz iç sınırı ayrıldı. Düşey eğri hâlâ çalışma hipotezidir.
- **Küçük okuma feneri:** 103'teki dokümantasyon alanının merkezine yerleştirildi; 116 ile düşey oranları kontrol edildi. Köşe profilleri ve kesitleri henüz doğrulanmadı.
- **Merdiven / P09 kısmi çalışma:** 021/022'de görülen üç geniş başlangıç basamağı PDF2016 vektörlerinden ayrı hacimler olarak çıkarıldı. Kapanış sınırı aynı paftadaki eğrisel merdiven duvarından alındı. Ana merdiven kolu henüz üretilmedi.

## Önemli yön düzeltmesi

Önceki P05 üst merdiven kılavuzunun başlangıç/bitiş kotları tersti. Üç geniş kıvrımlı basamağın bulunduğu uç **0 kotundaki başlangıç**, daralan kolun köprüye vardığı uç **+1 bağlantısıdır**. Eski kılavuz gizlenip düzeltilmiş kılavuz eklendi. Bu değişiklik **GH_UP** içindir. Kullanıcının daha önce düzelttiği **GH_DOWN / 049-050** kimliği ve aşağı inen yönü korunur.

Vektör paftadaki merdiven çizgileri tam uygulama basamak sayısı değildir. Şemadaki çizgiler sayılıp gerçek rıht sayısı ilan edilmedi. Fotoğrafta açıkça görülen üç başlangıç basamağı modellendi; 0,16 m rıht değeri ölçülmüş değil, değiştirilebilir çalışma parametresidir.

## Fotoğraf kontrolleri

| Fotoğraf | Kamera hesabı | Hesap dışında kalan kontrol | Sonuç |
| --- | --- | --- | --- |
| 119 | 7 çatı + 2 kanat ucu | 4 çatı omzu | Hesap RMS 8,47 px; omuz RMS 6,37 px |
| 087 | Aynı sabit geometri; ayrı kamera | 4 çatı omzu | Hesap RMS 8,85 px; omuz RMS 6,65 px |
| 116 | 4 çatı/kabuk köşesi + ana/pavyon tepeleri | 4 ana çatı noktası | Hesap RMS 6,35 px; kontrol RMS 10,05 px |

119/087 kanat uçları artık hesaba dahildir; bağımsız kontrol diye sunulmaz. 116 karşı taraftan ek sınama sağlar fakat köşe seçimi, bilinmeyen lens/kırpma ve koşullu kotların etkisini ortadan kaldırmaz. Kamera sayısal aktarımı ile binanın fiziksel doğruluğu ayrı konulardır. Atlasın doğrulanmış kamera sayısı değiştirilmedi.

Taş duvar uçları için alternatif köşe eşleşmesi de denendi; `P06_alternate_wall_corner_fit.json` içinde tutulur. Özgün köşe kimliği/duvar başlığı kalınlığı açık olduğu için hiçbir alternatif ölçülmüş gerçek olarak kabul edilmedi.

## Ölçülerin durumu

Plan/OSM dönüşümü ve XY ölçeği korunuyor. `entry_package.json` her elemanın kaynak ve varsayımını içerir. Saçak altı, kolon genişliği, duvar kalınlığı, pencere yükseklikleri, çerçeve kesitleri ve cam kalınlığı çalışma ölçüleridir; taşıyıcı veya imalat şartnamesi değildir.

Ana alt cam bandının çalışma alt kotu yaklaşık +9,72 m; alt saçak adayı +2,92 m. İlk değer 119/087'den, ikincisi yalnız 087'den hesaplandı. Bunlar kameradan sonra ayarlanan yükseklikler olduğundan aynı fotoğrafa uyum bağımsız doğrulama değildir. Önceki kesit kaynaklı kotların yerine genel, doğrulanmış kat kotu olarak yazılmadı.

## Dosya kontrolleri

P07 kaydı yeni Blender sürecinde açıldı: 164 yeni mesh, 67 kapalı hacim kontrol edildi. Kapalı hacimler manifold ve pozitif hacimli; sıfır alanlı yüz yok. Ortadaki kapı geçişine 0,15 / 1,40 / 2,50 m yüksekliklerde ışın gönderildi, yeni duvar/cam/çerçeve engeli bulunmadı. Üç kamera için Blender ile hesap betiği arasındaki en büyük projeksiyon farkı 0,009 pikselin altında.

P09'un ayrı yeniden açma kontrolü `P09_verification.json` içinde: üç basamağın hacmi, katman kotları, yukarı/aşağı yönlerin ayrılığı, kaynak fotoğrafların paketlenmesi ve giriş açıklıklarının korunması denetlenir. Bu testler bina doğruluğu veya imalat kabulü anlamına gelmez.

## Sıradaki işler

022 ve 024 yakın çekimlerinin ek kontrolü `config/stair_detail_evidence.json` içinde kayıtlıdır. Cam korkuluğun yuvarlak metal üst profili ile duvar tarafındaki taş renkli, yuvarlatılmış uçlu tutamak ayrı elemanlardır. Taş tarafındaki detayın oyma/monte yapısı, tam kesiti ve ölçüleri fotoğraftan kesinleşmez. 022'de başlangıçtaki kavisli cam dönüş ve alt metal bağlantı da görünür; düz panellerin tekrarıyla geçiştirilmeyecek.

Üretim sayfası tarayıcıda açıldı: Fotoğraf düğmesi görünürlüğü %0'a, Model düğmesi %100'e getiriyor; kaydırıcı %55'e döndürüldüğünde üst üste karşılaştırma yeniden oluşuyor. Yerel HTML bağlantıları ve üretim betiklerinin Python sözdizimi kontrolü geçti.

1. Üst merdivenin tam kolunda rıht sayısı, kavisli yan duvar ve +1 sahanlık bağlantısı; sonra ayrı GH_DOWN sistemi.
2. Giriş boşluklarının bağımsız yakın kamera kontrolü; döner kapının gerçek kanat/mekanizma düzeni.
3. Galeri duvar ve pencere envanterini altı giriş açıklığının dışına genişletmek.
4. Yan cam örtülerin uç birleşimleri, üst galeri ışıklık sayısı ve ana çatının panel/taşıyıcı düzeni.

P07-P09 bölgesel çalışmalar devam ediyor. Hiçbiri bütün bina için tamamlandı olarak kapatılmadı; P10-P22 detayları da tamamlanmış sayılmıyor. Rutin üretim ve kontroller kullanıcı onayı beklemeden sürdürülür.
