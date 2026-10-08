# R05 — Grand Hall aşağı merdiveni

9 Ekim 2026, Europe/Paris. Sahne: `../scenes/MUDAM_R05_ALT_MERDIVEN_v004.blend`.

049/050, aşağı inen merdivenin zemin/ara kot görünümleridir. 051/052 ve 115 alt kattan aynı sistemi gösterir. Bu paket bunları üst merdivenle karıştırmadan ayrı GH_DOWN sistemi olarak kullanır.

## Kaynak ve biçim

PDF2016 sayfa 5, 219–229 yollarının dış ve iç eğrilerine ortak merkezli daireler uyduruldu. Kanonik merkez yaklaşık (636,802; 387,643), dış/iç yarıçaplar 36,669 / 21,796 piksel. Mevcut yaklaşık yatay ölçekte bunlar 4,356 / 2,589 m; kol genişliği yaklaşık 1,767 m. Eğri uyum artıklarının 0,009 pikselden küçük olması yalnız çizgiye sayısal uyumu gösterir, yapının milimetrik ölçüldüğü anlamına gelmez.

114, 055 ve 045 fotoğrafları zemin kenarının ortasında **kıvrımlı bir döşeme uzantısı**, iki yanında düz korkuluk kanatları gösteriyor. 102 şeması arkada üçgen köşe boşluğunu destekliyor. PDF 218 iç eğrisi bu uzantının çalışma konturu olarak kullanıldı; 217 yalnız merdiven zarfı ve üst basamak kenarıdır. v003'teki tam yarım daire boşluğu ve tek düz korkuluk yorumu bu karşılaştırmada reddedildi. v004 döşeme uzantısını korur, arkasındaki köşe boşluğunu açar ve eğrisel camı yerleştirir. Kaynaklar arasındaki ayrıntılı eğri eşleşmesi ve kısa birleşimler hâlâ koşulludur. 104 alt fuayenin yerini destekler, rıht geometrisini vermez.

051/052 fotoğrafları kademeli alt yüzü gösteriyor. Modelin altında düz rampa yüzeyi üretilmedi: ayrı kama biçimli basamaklar sabit, koşullu görünüm kalınlığıyla kademeli alt yüz oluşturuyor. İki tarafta kıvrımlı camlar, yuvarlak metal küpeşteler, taban kanalları ve taş kenar zarfları var. Fotoğraftaki koyu burun çizgileri dar yüzey şeritleriyle temsil edildi.

## Üst ve alt uç

İlk yarım daire adayının 45° üst ucu kaynak döşeme kenarının yaklaşık 0,28 m içinde kalıyordu. v002/v003, iç ve dış uçları 217 yolunun gerçek düz kapanışına ayrı ayrı oturtuyor. Uç açısı iç ve dış yarıçapta farklı; yalnız daireyi keyfî büyüterek boşluğa uydurulmadı. v004 zemin korkuluğu iç uzantının eğrisini ve düz kanatları izler; üst merdiven ağzı açık bırakıldı ve her panel tabanı denetlendi. Tam köşe/geçiş profili hâlâ koşullu.

## Değiştirilebilir adaylar

- Kot: önceki kesit çalışmasının koşullu −5,326 m değeri.
- **34 rıht adayı**: 33 görünür basamak gövdesi ve zemin döşemesine son yükselme. Sayı fotoğraftan kesin sayılmış değildir; yaklaşık 0,1567 m yükselme, üst merdiven adayının ortalama yükselmesine yakın olduğu için seçildi.
- Alt uç yönü: mevcut −135° kanonik yön adayı; fotoğrafın metrik konumu çözülmedi.
- Her tarafta 12 cam panel, 16 mm cam, 1,05 m korkuluk, 42 mm küpeşte çapı; bunların hepsi temsilî detay ölçüleridir.
- Basamak görünüm kalınlığı 0,28 m, taş kenar ve taban profilleri koşullu. Fotoğraf alt yüz biçimini gösterir; gerçek taşıyıcı kesit/donatı sistemini vermez.
- 16 zemin kenarı cam paneli koşullu bölünmedir. Bütün korkuluk sisteminin bağlantı kabulü yapılmadı.

## Yeniden açma kontrolü

`R05_verification.json` sonuçları:

- Yeni kapalı hacimler ve değişen Grand Hall zemin döşemesi manifold, pozitif hacimli ve sıfır alanlı yüzlerden temiz.
- 33 basamağın üç enine konumunda 99 destek/baş mesafesi kontrolü; 32 basamaklar arası göz yüksekliği geçişi açık.
- Alt ve üst bağlantıların üçer noktası gerçek sahne döşemelerine oturuyor. Zemin kenarı korkuluğunun 16 tabanı döşeme üzerinde; iç uzantının üç noktası dolu, arka köşe örneği boştur.
- Görünebilen basamak altları ayrı ayrı denetlendi.
- Helisel küpeşteler yol teğetine dik dairesel kesitle üretildi; profil çemberi ve düzlemi tüm örneklerde denetlendi.
- R04 üst merdiveni ile R02/R03 açıklık kontrolleri **R05 sahnesi üzerinde** tekrar geçti: `R04_regression_on_R05.json`.

İlk ince şerit örneklemesi bazı burun şeritlerinde sıfır alanlı üçgen üretiyordu; v003, bu 18 mm genişlikteki şeritleri tek küçük dörtgen olarak kurarak kusuru giderdi. v001/v002/v003 yayımlanan sürüm değildir. v003 sayısal geometri kontrollerini geçmiş olsa da 114/055 ile mimari karşılaştırmada döşeme topolojisi bakımından reddedildi; bu nedenle yeni döşeme/boşluk testleri eklendi.

`../renders/qa/R05_lower_stair.png` çevresi gizlenmiş bileşen görünümü; `../renders/qa/R05_ground_opening.png` doğrulanmış sahneden zemin boşluğu/merdiven ilişkisi. Kaynak kameralarıyla kalibre edilmiş bitmiş iç mekân görüntüleri değiller. Alt fuaye duvarları, kapılar, tavan/aydınlatma ve malzeme detayları devam ediyor.
