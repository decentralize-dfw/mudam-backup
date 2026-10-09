# R90 — güney atrium cam şeridinin üretimi

## Düzeltilen eksik

116 hava fotoğrafında yüksek taş duvarların arasında bölünmüş, çerçeveli cam şerit görülüyor. R89'da `P06_HIGH_EAVE_UPSTAND_4` hâlâ tek, çerçevesiz renkli temsil yüzeyiydi. R90 bu eski temsili gizleyip aynı açıklıkta **12 cam panel, dört düşey ve beş yatay metal çerçeve parçası** üretti.

Yeni yerel sahne: `scenes/MUDAM_R90_GUNEY_ATRIUM_CAM_CERCEVE_v001.blend`.

## Korunan sınırlar ve belirsizlikler

R72 açıklık tabanı ve P06 çatı kenarı, mevcut plan konumu ve çatı biçimi korundu. Diğer duvar, zemin ve çatı nesneleri değiştirilmedi. Üç sütun bitişik dar çatı şeridinin akslarıyla ilişkilendirildi. Dört sıra, 75 mm yüz genişliği, 140 mm profil derinliği ve 18 mm cam kalınlığı **ölçülmemiş görselleştirme adaylarıdır**. Fotoğraf çerçeveli sistemin varlığını destekler; bu değerleri doğrulamaz. Gizli ankraj, conta veya yalıtım katmanı uydurulmadı.

## Kaydedilmiş sahnenin kontrolü

- 21 yeni parça kapalı, pozitif hacimli mesh.
- 51.914 yerel cam/çerçeve yüzey örneğinde açıklık yok.
- Sahnenin 7.850 görünür mesh'inde genel geometri kontrolü geçti.
- Önceki sahne karşılaştırmasında yalnız eski cam temsilinin görünürlüğü değişti; diğer mevcut nesnelerde beklenmeyen fark yok.
- Aynı kamera ve ışıkla önce/sonra renderları incelendi; çevre nesneleri gizlenmedi. Öndeki okuma feneri cam şeridin bir bölümünü doğal olarak örter.

[Önce](../renders/qa/R90_before_south_glazing.png) · [Sonra](../renders/qa/R90_after_south_glazing.png) · [Yeniden açma testi](R90_verification.json) · [Genel geometri](R90_global_audit.json) · [Sahne farkı](R90_inherited_verification.json).

Bütün bina kabuğu ve bütün çelik birleşim detayları tamamlanmış değildir. İdari/teknik alanlar ve kesin çatı biçimi kabulü açıktır. Bu paket gerçek bir geometri değişikliğidir; önceki R89 kontrol paketinden ayrıdır.
