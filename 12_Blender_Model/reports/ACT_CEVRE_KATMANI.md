# ACT çevre katmanı

Ana `MODEL_INCELEME.html` görüntüleyicisine **Arazi ve çevreyi aç** denetimi eklendi. Aynı görüntü alanında ACT 2020 dokulu çevresi gösterilir; bina ve çevre bağımsız açılıp kapanır. Bina incelemesine dönünce mevcut kesit, kat ve parça seçimi araçları korunur.

Kaynak: ACT Luxembourg, mesh3D 2020, CC0. Google API veya Cesium Ion hesabı gerekmez. Görünür çevre parçaları doğrudan resmî ACT sunucusundan yüklenir; internet bağlantısı gerekir.

Yayın varsayılanı `config/model_release.json` ile doğrulanmış **R149** bina modelidir. Ayrı yerel **R151 v011** yerleştirme dosyası ve onun önizlemesi bu yayınla kabul edilmiş bina sürümü ilan edilmez. Yerel deneme `CEVRE_ADAY.html?candidate=1` yolundadır; bu parametre yerel, Git dışında tutulan sürümlü GLB gerektirir.

Kaynak çevredeki müze, çalışma sınır poligonu ile görüntüden kesilir. Yayın görünümünde arazi–bina birleşimleri hâlâ çalışma niteliğindedir. Tam sınır doğruluğu veya Google Earth ile ayrıntı eşdeğerliği iddia edilmez. Üretim puanı değişmedi: 85/115, %73,913 (yuvarlak %74).

Dokunulmamış kaynak `scenes/MUDAM_ACT2020_DOKUNULMAMIS.blend` olarak yerelde korunur. R151 v011 bağlantı döşemesinin taşınması sonrası 362 yerel zemin desteği örneği geçti; bu test yalnız ilgili geçit kapsamındadır.
