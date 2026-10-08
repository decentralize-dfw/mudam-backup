# R09 — Okuma mekânı, üç geçiş ve döşeme bağlantıları

9 Ekim 2026 Europe/Paris. `../scenes/MUDAM_R09_OKUMA_MEKANI_v001.blend`.

PDF2016 sayfa 5, 103 numaralı vektör yolundan oda iç çevresi ve üç açıklık ayrıldı. Üst kat çiziminin 251,865 PDF puanı düşey yer değiştirmesi önceki kalibrasyonla aynı kullanıldı. Kaynak köşeler ve her köşenin yol/öğe uç kimliği `reading_room.json` içinde saklanıyor.

Sekizgen oda için dik ve 45° yüzey adayı kaynak köşelere en küçük karelerle uyduruldu. En büyük fark 0.808339 kanonik piksel, yaklaşık 0.096 m. Bu yalnız şema çizgisine uyumdur; OSM/kot belirsizliğini ortadan kaldırmaz. Kaynak plan görüntüleri ve global dönüşüm değişmedi. Önceki R08 tavan alt çevresi bu daha iyi iç duvar konturuna taşındı; ışıklık konumu ve tavan kotları korundu. Teller yeni tavan yüzeylerine yeniden bağlandı.

## Açıklıklar

- NORTH: kaynak boşluğundan 2.208 m çalışma genişliği.
- EAST: kaynak boşluğundan 1.812 m çalışma genişliği.
- WEST: kaynak boşluğundan 1.812 m çalışma genişliği.

Açıklık başı üst kat döşemesinden 2,30 m; duvar görünüm kalınlığı 0,30 m. Bu iki değer ölçülmedi, değiştirilebilir adaydır. PDF'nin siyah çizgi kalınlığı gerçek duvar kalınlığı kabul edilmedi. 015'teki kapı görüntüsünün hangi plana ait olduğu kesinleşmediği için kanat/donanım atanmadı.

Üç kısa döşeme uzantısı, plandaki geçişleri mevcut üst kat döşemesine Boolean birleşimiyle ekler. Ortadaki boşluk ve cam korkuluk korunur. Kuzey bağlantısı köprü döşemesine, yanlar komşu kat bölgelerine ulaşır; önceki ayrı bölge modellerinin aradaki boşlukları kapatıldı.

## Kontroller

- Kaydedilmiş R09 tekrar açıldı; değişen döşeme manifold, pozitif hacimli ve sıfır alanlı yüzlerden temiz.
- Üç açıklıkta 9 yatay geçiş ışını ve 27 destek/2,10 m baş mesafesi örneği geçti.
- Sekiz köşede iki komşu duvar ve tavan alt köşesi ortak koordinatta.
- Tavan yüzeyleri, ışıklık görüşü, üst kat korkuluk çevresi ve 24 tel ucu yeniden denetlendi.
- Önceki 4342 mesh/eğri içinde sadece raporda izin verilen oda döşemesi, tavan, huni kesicisi ve tel uçları değişti. Çatı döşemesi/kaidesi aynı kesicinin yeni geometrisini kullanır; değerlendirilmiş hacimleri ayrıca tavan testinde geçti.

Görünüm yerel bileşen incelemesi; kalan galerilerin tamamını göstermiyor. Kapı kimlikleri, kesin kotlar, derzler, aydınlatma kalibrasyonu ve dış fener biçimi açık.
