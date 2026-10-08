# P02 / P04 — kesit ve kot etüdü

8 Ekim 2026. Kaynak: `02_Kesitler/101_Mimari_kesit_ArchEyes.jpg` (1250×852), plan 102/104 ve fotoğraf 089/116/119. Orijinal dosyalar değiştirilmedi. İşaretli türev: `references/P04_section_height_study.png`; ölçü okuma ayrıntısı: `references/section_levels_detail.png`.

## Yöntem

Pavyon, ana örtü ve pavyon bağlantısının aday yatay genişlikleri planla karşılaştırıldı. Hesaplar ve ham piksel seçimleri `config/vertical_study.json` içindedir. Üç genişlik yaklaşık 0,0904–0,0942 m/kesit pikseli verir; medyan 0,09344 m/px çalışma ölçeği seçildi. Görüntüye yönden yöne farklı ölçek veya yerel deformasyon uygulanmadı.

Bu eşleşme, kesit düzlemini çözmez. Kesitin çizim tarihi, özgün pafta ölçeği, kesit izi ve mevcut bina ile tam uyumu bilinmiyor. Yatay ve düşey görüntü ölçeğinin aynı olduğu kabulü koşulludur. Renkli merkez pavyonunun kalıcı/geçici kimliği çözülmedi; geometriye alınmadı.

## İlk çalışma kotları

| Eleman | Çalışma kotu (m) | Seçim |
| --- | ---: | --- |
| Zemin | 0,00 | Yerel proje datumu; kesit y=436 |
| +1 adayı | +4,86 | Doğu spiral merdiven üst kapısının tabanı, y≈384 |
| Ana bina −1 adayı | −5,33 | Kesit y≈493 |
| Pavyon alt döşemesi adayı | −3,83 | Kesit y≈477; ana bina −1 kotundan ayrı |
| Ana çatı oturma adayı | +13,92 | Kesit y≈287 |
| Ana çatı tepe adayı | +30,37 | Kesit y≈111 |
| Pavyon duvar üstü | +5,42 | Kesit y≈378 |
| Pavyon fener altı / üstü | +9,06 / +12,80 | Kesit y≈339 / 299 |
| Pavyon tepe adayı | +14,58 | Kesit y≈280 |

Bunlar ölçülmüş veya onaylanmış kotlar değildir. `parametreler.json` içindeki `value` alanları boş bırakıldı; yalnızca `draft_value` ve yöntem kaydı dolduruldu. Aralıklar üç genişlik arasındaki farkı ve ±2 piksel okuma duyarlılığını gösterir. OSM, projeksiyon, çizim tarihi ve yanlış eşleştirme risklerini kapsamaz; istatistiksel güven aralığı değildir.

[Luxembourg Convention Bureau mekân kaydı](https://lcb.lu/en/partners/122?favorite=show), Grand Hall için 33 m, Foyer için 4,67 m, Passerelle için 6 m tavan yüksekliği yayımlıyor (8 Ekim 2026 erişimi). Bunlar katlar arası kot olarak aktarılmadı. Grand Hall değerinin tepe noktası ve referans döşemesi açık olmadığı için 30,37 m etüt değeriyle çelişki çözülmüş sayılmıyor.

## Blender etüdü

P03 sahnesinin bir kopyasında üç kat koşullu kotlarına taşındı. Pavyonun duvar kabuğu, eğimli çatı, fener ve tepe yüzeyleri ayrı mesh nesneleridir. Alt pavyon kotu ayrıca tutuldu. Turuncu çizgiler grafik kot işaretleridir; çelik profiller değildir. Cam geçit yalnız tel çerçevedir.

Bu, düşey oranları sınamak için bir hacim etüdüdür. Açıklıklar, duvar kalınlığı, cam panel örgüsü, taşıyıcı profiller, basamaklar, korkuluklar ve fiziksel malzemeler henüz üretilmedi. Bu geometri `90_UNCERTAIN_OR_PROXY` içinde tutulur; üretim koleksiyonlarına aktarılmaz.

## Kapanmadan önce yapılacaklar

1. 101 ile 084 kesitlerinin kimliği/tarihi ve plan izi ilişkisini çöz veya neden çözülemediğini belgeleyerek kapsamı sınırla.
2. +1 kapı tabanı adayını geniş merdivenin üst sahanlığı ve rıht zinciriyle karşılaştır.
3. Alt kat merdiveninin toplam yükselmesini bağımsız kontrol et; pavyon alt katını karıştırma.
4. 116/119 ile ana örtü silüetini çoklu görünüşte çöz; 33 m mekân verisinin datumunu araştır.
5. Bu sonuçlarla P05 bütün bina sade geometrisine geç. P02/P04 henüz tamamlanmış değildir.
