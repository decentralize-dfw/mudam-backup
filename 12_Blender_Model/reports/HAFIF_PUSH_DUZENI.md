# Saatlik hafif yayın ve canlı model

Blender sahneleri ve sürümlü GLB arşivleri yalnız yerelde kalır. Canlı sitede modeli göstermek için tek istisna `exports/current.glb.gz`: son doğrulanmış GLB'nin kayıpsız gzip kopyasıdır. Bu dosya ve `config/model_release.json` birlikte yayımlanır. R69 için 89,20 MB GLB, 54,18 MB aktarım olur; geometri ve dokular bayt düzeyinde aynıdır. Eski modeller yeni Git ağacına eklenmez; normal Git geçmişi geçmiş yayınları tutmaya devam eder.

`prepare_web_model.py` en son sahne ile dışa aktarım ve geometri kontrol kayıtlarını eşleştirir; gzip açıldığında özgün GLB'nin birebir döndüğünü doğrular. Dosya karması ve kaynak sahne tek yayın kaydındadır. Güncel GLB doğrulanmadan yeni kayıt yayımlanmaz. `publish_current_checkpoint.py` doğrulanmış aktarım hazır olduğunda bu adımı çalıştırır. Saatlik `push_progress.ps1 -Publish` de aynı kontrolü zorunlu yapar.

Tüm 3D inceleme bağlantıları `MODEL_INCELEME.html` üzerinden `assets/model-release.mjs` kullanır. Manifest önbelleksiz okunur; GLB kayıpsız açılır ve SHA-256 doğrulanır. Açık görüntüleyici her 60 saniyede ve sekmeye dönüldüğünde güncelleme arar. Yeni model yüklenmeden mevcut model kaldırılmaz; yeni modelde kamera görünümü korunur. GLB indir bağlantısı açık olan güncel modelin sıkıştırılmamış dosyasını indirir. Blender kaynak dosyası webde yayımlanmaz.

Saatlik Codex görevi pano, renderlar, raporlar, kaynak kayıtları, betikler ve bu tek web önizlemesini normal origin/main push ile gönderir. Başka hazırlanmış değişiklikler, doğrulanmamış model veya uzak dal farkı varsa durur. Force push ve geçmiş yeniden yazımı yapmaz. UTC push sonucu MD'ye kaydedilir. `-Publish` olmadan yalnız hazırlık ve dosya listesi gösterilir.
