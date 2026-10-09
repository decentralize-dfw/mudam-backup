# R92 — gereksiz bağımsız galeri bölmelerinin kaldırılması

Kullanıcının işaretlediği zemin kat batı galerisindeki diyagonal hat, `R28_W_DETACHED_ENTRY_WALL` ile eşleşiyor. Kalıcı bina elemanı olduğu doğrulanmadan bu çizgiden 4,35 m yüksekliğinde bağımsız duvar üretilmişti. Aynı yorumla eklenen `R28_E_DETACHED_ENTRY_WALL` da kapsam dışına çıkarıldı. **İki nesne yeni sahneden kaldırıldı; isteğe bağlı sergi katmanı olarak saklanmadı.** Eski sürümler geçmiş kaydı olarak yerelde durur.

102/PDF çizgisinin varlığı inkâr edilmiyor. Hata, bu çizgiyi kalıcı mimari duvar kabul etmekti. Geçici sergi bölmelerini kapsam dışı bırakan kullanıcı talimatı ve işaretli düzeltme uygulandı. Mevcut dış duvarlar, zemin, tavan ve üst kat duvarları korunuyor.

## Doğrulama

- Kaldırılan iki nesne kaydedilip yeniden açılan R92 sahnesinde yok.
- Eski diyagonal duvar hatlarında 0,3 / 1,2 / 2,1 m kotlarında toplam 54 geçiş ışını engelsiz.
- Dolaşım döşemeleri ve galeri tavanları mevcut.
- Bütün sahne ve önceki nesne farkı denetimi geçti; bu pakette yalnız iki bölme kaldırıldı.
- 33 bölgenin zemin/örtü/yan kapanış taramasında yeni eksiklik bulunmadı.
- Aynı kamera ve geçici inceleme ışığıyla önce/sonra iç görünüşler üretildi; ışık sahneye kaydedilmedi.

[Önce](../renders/qa/R92_before_west_gallery.png) · [Sonra](../renders/qa/R92_after_west_gallery.png) · [Geçiş kontrolü](R92_verification.json).

R91 batı uç duvar–cam çatı düzeltmesi bu sahneye dahildir. Bu paket bütün idari/teknik alanların veya bütün yapı ölçülerinin kabulü değildir.
