# R89 — yerel çatı yüzeyi ve saçak kontrolü

9 Ekim 2026, UTC 14:00 civarı. Son doğrulanmış R89 sahnesi Blender'da yeniden açıldı. Bu çalışma bir geometri üretim paketi değil, kapsamı genişletilmiş kontroldür; yeni sahne veya GLB sürümü oluşturulmadı.

## Sonuç

- Ana çatı, fener ve tepe örtüsünün 24 referans yüzünde **330.913** örnek: yerel örtü kaybı yok.
- Doğu/batı yan çatılarındaki **228** cam hücresinin kenar bantlarında **256.816** geçerli örnek: yerel örtü kaybı yok.
- Ana saçakların altındaki dar düşey bantta 25 geometrik kaçış adayı kaydedildi. Tamamı eğimli geçiş camının alt sınırı olan alçak saçak kotunun altında kaldı. Geçiş camının kendi kot aralığında kaçış yok. Alttaki komşu hacimlerde bu tanısal düzlemin üzerinde ayrıca duvar bulunması gerekmiyor; bu noktalar rastgele duvarla kapatılmadı. Bu sınıflandırma bütün komşu hacimlerin kesin kabulü değildir.

## Kontrolün önceki oda taramasından farkı

Çatı yüzeyindeki ışınlar yüzeye dik ve yalnız 0,4–0,6 m uzunlukta. Uzaktaki bir duvara veya başka bir kata çarpmak bu kontrolden geçmeye yetmez. Gizli kaynak yüzeyleri ışınlara engel olarak eklenmedi; ana çatı testinde gölgelik katmanları da kullanılmadı.

Ana yüzeylerde 5 cm ağ ve 0/1/3/6 cm kenar bantları; yan hücrelerde 5 cm boyunca örnekler ve 0/1/2/3/4/6/8 cm kenar bantları kullanıldı. Bunlar **sayısal örnekleme aralıklarıdır, ölçüm doğruluğu değildir**. Yan hücrelerin dışına taşan köşe örnekleri çokgen sınırı testiyle elendi.

Negatif kontrol: bir ana çatı camı yalnız tanısal ışın ağından çıkarıldığında, merkezindeki eksiklik bulundu. Aynı nokta normal sahnede kapalı. Kaydedilmiş sahnede nesne silinmedi veya gizlenmedi.

## Kaynak karşılaştırması ve sınırlar

116 hava fotoğrafı, 026 Grand Hall fotoğrafı ve 101 kesiti yeniden görsel incelendi. Taş yüksek duvarlar, cam çatı ve değişen saçak seviyeleri ayrı sistemler olarak korunuyor. 026'daki sergi eseri modelleme kapsamına alınmadı.

116'da merkezi üst cam şeridinin çerçeve düzeni modeldeki sade temsilden daha ayrıntılı; bu fark açık. Çatı kotları, panel sayıları ve kesit izi hâlâ koşullu. Küçük batı hacminin kesin çatı biçimi, idari alanlar ve alt teknik kat kapsamı bu test tarafından doğrulanmış sayılmaz.

Yan hücre alanları P11'in belgeli küçültme işleminden geri elde edildi. Batı için R12 düzleştirmesinden önceki kayıtlar kullanıldı ve alanlar mevcut cam düzlemine izdüşürüldü. Bu bir yeni çatı biçimi önerisi değildir.

## Tekrar üretme

- `scripts/audit_local_roof_skin.py`: doğrulanmış güncel sahneyi seçer; ana yüzey ve saçak JSON raporlarını üretir.
- `scripts/audit_side_roof_skin.py`: varsayılan güncel sahne; isteğe bağlı `-- <repo-göreli-sahne>` ile başka sürüm. R89 kaynak hücre alanları ayrı dosyada korunur.

Veri: [Ana yüzeyler](R89_local_roof_skin.json), [Saçak bandı](R89_local_eave_band.json), [Yan yüzeyler](R89_side_roof_skin.json), [Yan kaynak hücreleri](R89_side_roof_domains.json).

**Bütün bina kabuğu tamamlandı sonucu çıkarılmadı. Yüzdeler artırılmadı.**

## Üst galeri çevre birleşimleri — devam kontrolü

İki üst galerinin kayıtlı çatı dış çevreleri boyunca, çatı altından 10/30/60 cm düşülerek 1,2 m uzunlukta yatay ışınlar kullanıldı. **9.558 örnekte kaçış yok**. Sonuç dosyasında çarpılan duvar, çatı veya profil nesnelerinin isimleri ve sayıları tutuluyor: [Çevre kontrolü](R89_gallery_roof_wall_joint.json).

R24'ün mevcut 71 ışıklık panelinin her birinde kullanılan gökyüzü doğrultusu güncel R89 opak geometrisine karşı yeniden denetlendi; **71 doğrultunun tamamı açık**. Bu bir aydınlık düzeyi hesabı değildir: [Işıklık kontrolü](R89_gallery_daylight_path.json).

Sahne değiştirilmeden dört iç görünüş üretildi ve UG02/UG03 fotoğraflarıyla karşılaştırıldı. Kavisli örtü/ışıklık ailesi okunuyor; tam kesit biçimi, ışıklık modülleri, doğu/batı alan sayısı ve ışık şiddeti hâlâ koşullu. Renderların koyu görünümü kalibre edilmiş aydınlık ölçümü olarak yorumlanmaz. Bütün mevcut çevre görünür bırakıldı, duvar gizleyerek görüntü açılmadı.

- [Doğu galeri](../renders/qa/R89_east_gallery.png)
- [Batı galeri](../renders/qa/R89_west_gallery.png)
- [Doğu ışıklıkları](../renders/qa/R89_east_clerestory.png)
- [Batı ışıklıkları](../renders/qa/R89_west_clerestory.png)
