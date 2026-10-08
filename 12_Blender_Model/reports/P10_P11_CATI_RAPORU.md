# Ana ve yan cam örtü üretimi

8 Ekim 2026 gece üretimi. Güncel sahne `P11_build_report.json` ve yeniden açma kontrolü `P11_verification.json` içinde kayıtlıdır.

P10 ana örtü, fener ve tepeyi oluşturan 24 yüzeyde 359 ayrı cam panel ve ayrı profil hacimleri üretir. Üçgen kenarlar dikdörtgen modülle kesilir; yüzeyler rastgele bir merkez noktasına yelpaze gibi bölünmez. 119'daki ön fenerin üç sütunu ve altı yüksekliği sayılabilir; geniş yüzeylerin toplam modül sayıları ile öteki yönlere aktarımı hâlâ adaydır. Cam/profil kalınlıkları ölçülmüş değildir.

P11'de 435 ek cam panel bulunur: doğu/batı örtüleri, ana örtünün alt eğimli yüzleri ve düşey cam bandı, orta şerit ve pavyona giden cam geçit. Doğu ile batı farklı kaynak konturlarından üretilir. 093 ve 034'ün yeniden incelenmesi sonucunda yan salonlarda önceki alt cam kuşağın yerine opak taş kuşak getirildi. Kuşağın yüksekliği önceki koşullu kotlardan gelir; saha ölçüsü değildir.

Doğuda profil düzleminin altında ayrı dikmeler ve ince gergi çubukları eklendi. Çubuklar camın ortasında bitmez, profil kesişimlerine bağlanır. Bu, 034/036'da gözlenen katmanların temsilî geometrisidir; özel bağlantı parçalarının tam şekli ve bütün gergi ağının gerçek topolojisi henüz doğrulanmış değildir. Cam geçitte 067'nin gösterdiği üst çaprazlar ayrı nesnelerdir; toplam açıklık sayısı adaydır.

## Kontroller ve sınırlar

- P10: 1.291 kapalı hacim; bütün yüzeylerin bölünmüş alanı kaynak alanıyla sayısal tolerans içinde aynı. Eski bütün yüzeyler gizli, ayrı paneller görünür.
- P11 ile birlikte yeniden açılan toplam 3.203 kapalı hacimde pozitif hacim, manifold kenarlar ve sıfır alanlı yüz denetimi geçti.
- 380 doğu gergisinin uçları modeldeki profil kesişimlerine en çok 0,0000022 m sayısal sapmayla bağlanıyor. Bu, yazılım bağlantı kontrolüdür; gerçek bina doğruluğu değildir.
- Batı örtüsünün koşullu eğrisel biçiminde dörtgen panel düzlemsellik sapması en çok yaklaşık 0,0198 m. Paneller görselleştirme için üçgenlenir. Düz cam imalat çözümü olarak kabul edilmez; çatı eğrisiyle birlikte düzeltilmesi gerekir.
- Girişteki altı açıklık, merdivenin üç başlangıç basamağı ve üç fotoğraf kamerası korundu.
- Pavyonun kendi cam örtüsü, küçük okuma fenerinin panelleri, ana çatının iç gergileri ve gölgelemesi henüz bu pakette yok.

`P11_internal_east.png` ek iç geometri kontrolüdür; fotoğraf eşlenmiş kamera değildir. Nötr çevrede Cycles/OptiX ile alınır. Gökyüzü, peyzaj ve son malzeme ayarı içermez.

## Sonraki adım

Giriş kapısının görünen düz cam kanatları ve metal bağlantıları; mekanizma kimliğinin varsayım olarak düzeltilmesi. Ardından merdivenler ve tüm kat açıklıkları. P10/P11 tamamlanmış bütün sistem kabulüyle kapatılmadı.
