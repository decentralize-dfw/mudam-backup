# Saatlik hafif yayın

Blender sahneleri ve GLB/model dışa aktarımları yerelde kalır. `.gitignore` ve `scripts/push_progress.ps1` bunları yeni Git kayıtlarından dışlar. Mevcut dosyalar diskten silinmez. Önceden yayımlanan model dosyaları Git geçmişinde kalır; geçmiş yeniden yazılmaz.

Mevcut saatlik Codex görevi güncellenmiştir. Doğrulanmış paket tamamlandığında `./12_Blender_Model/scripts/push_progress.ps1 -Publish` pano, render, rapor, kaynak kayıtları, dokular ve üretim betiklerini gönderir. `-Publish` olmadan yalnız dosya listesini gösterir. En son paketin kontrol raporlarını denetler; hazırlanmış başka değişiklik, model dosyası içeren yayımlanmamış commit veya uzak dal farkı varsa durur. Force push ve otomatik dosya silme yapmaz. Başarılı pushun UTC kaydını MD'ye ekler ve ayrıca gönderir.

Üretim yüzdeleri config/production_progress.json içindeki beş eşit iş adımından hesaplanır. Her kabul edilmiş pakette ilgili adımlar gözden geçirilir. Yerel sahne/GLB bağlantıları aynı bilgisayarda çalışır; yeni klonda model dosyaları ayrıca aktarılmalıdır.
