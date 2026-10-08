# R04 — Üst merdivenin tam kol adayı

9 Ekim 2026, Europe/Paris. Sahne: `../scenes/MUDAM_R04_UST_MERDIVEN_v003.blend`.

021–026 fotoğrafları, 101 kesiti, 102/103 ziyaretçi şemaları ve PDF2016 ile üst merdiven için tam bir geometrik aday üretildi. Bu paket, üst bağlantı yorumunu veya rıht sayısını kesinleştirmez. Alt merdiven kaynakları 049/050 bu merdivene aktarılmadı.

## Yeni bileşenler

Üç başlangıç basamağının ardından 28 ana rıhtlı kol, üst sahanlık, taş yan yüzey, kavisli arka duvar, büyük merdiven oyuğunun sınırları, eğimli cam korkuluk ve küpeşte eklendi. Önceki R03 cam dönüşünün üst küpeştesiyle bağlantı aynı koordinatta kuruldu. Üst döşemede yalnız bu adayın yaklaşım/çıkış bölgesi açıldı; sahanlıktan çıkışı kapatan duvar bırakılmadı.

Fotoğraf 025, sahanlık ve oyuk ilişkisini bütün halinde gösteriyor; 021 kol ve taş yan yüzeyi, 022/023 alt birleşimi, 024 duvar tarafındaki taş tutamağı destekliyor. Duvar tarafına ikinci metal küpeşte eklenmedi. Taş tutamağın ayrıntılı profili hâlâ açık.

## Sayısal varsayımlar

- Üst kot: önceki 101 kesit etüdünün **koşullu** +4,859 m değeri.
- Başlangıç platformu: +0,480 m; üç mevcut rıht 0,160 m adayını koruyor.
- Yeni ana kol: **28 rıht adayı**, her biri yaklaşık 0,1564 m; yatay basamak adımı yaklaşık 0,3173 m.
- 26–31 ana rıht seçenekleri `R04_riser_candidates.json` içinde. 28, mevcut platform rıhtına yakın yükselme ve kaynakta izlenen yatay uzunlukla uyumlu bir çalışma seçimi; gerçek sayı veya mevzuat kabulü değildir.
- Korkuluk: 8 eğimli panel ve kısa yatay bağlantı adayı; gerçek panel bölünmesi doğrulanmadı.
- Oyuk başı: üst kottan 3,4 m yukarıda, fotoğraf oranından türetilmiş aday. Duvar ve başlık kalınlıkları görünüm içindir.

Basamak gövdeleri ve taş yan duvar **görünen hacim zarflarıdır**. Betonarme kesit, donatı, ankraj veya taşın taşıyıcılığı çıkarılmadı.

## Planın üst ucundaki açık yorum

PDF2016/102/103 çizgisindeki kavisli arka sınır yaklaşık (514,24; 551,02) noktasında yatay bir çizgiye bağlanıyor; basamak çizgileri burada daralan bir üçgen oluşturuyor. Bunun gerçek daralma mı, üst döşeme tarafından örtülme mi, ziyaretçi şeması sadeleştirmesi mi olduğu kaynaklarla kesinleşmedi.

Fotoğraflarda görülen geniş kolu sıfıra yakın genişliğe indirmemek için bu adayda arka eğri teğeti üst kata doğru uzatıldı. **Bu uzatma kaynakta izlenmiş değildir.** Üst döşemedeki yerel açıklık da aynı varsayıma bağlıdır. `../references/R04_plan.svg` içinde izlenen bölüm mavi, bu sınırdan sonraki kısım turuncu. Planın geneli esnetilmedi ve farklı eksenlerde ölçeklenmedi. Bu bölge kesin model olarak kabul edilmemeli; ölçülü çizim veya uygun üst sahanlık fotoğrafı geldiğinde değiştirilebilir.

## Kontrol ve düzeltmeler

v001 bileşen görünümünde alt oyuk yan sınırı cam dönüşüne fazla yakındı; oyuk başlangıcı ortak PDF duvar eğrisinin gerçek başlangıcına taşındı. v002 kontrolü, düz teğet bölgesinde bir sıfır alanlı üçgen ve üst sahanlıkta eski döşemeyle çakışan yüzeyi yakaladı. v003, doğrusal örnekleri üçgenlemeden önce temizliyor ve yerel döşeme açıklığını sahanlığın sonuna kadar sürdürüyor.

v003 dosyası yeniden açılarak denetlendi:

- 117 yeni kapalı hacim ve değişen üst döşemenin değerlendirilmiş geometrisi pozitif/manifold; sıfır alanlı yüz yok.
- 28 basamağın üç enine konumunda toplam 84 örnek: doğru basamak yüzeyinde destek ve 2 m düşey inceleme ışınında engel yok. Bu örnekleme, mevzuat veya bütün hacimde insan çarpışma sertifikası değildir.
- 27 basamaklar arası göz yüksekliği ışını ve üst sahanlık çıkış ışını açık.
- Mevcut cam dönüşü ile küpeşte bağlantısı sayısal tolerans içinde.
- R02 geçidinin 15 ışını ve R03 girintisinin 12 ışını bütün görünür sahnede yeniden geçti.

`R04_verification.json` tam sonuçları içerir. `../renders/qa/R04_upper_stair.png` çevresi gizlenmiş bileşen incelemesidir; fotoğrafla kalibre edilmiş tam iç mekân değildir. Taş derzleri, gerçek malzeme ve aydınlatma eşlemesi sonraki aşamalardadır.
