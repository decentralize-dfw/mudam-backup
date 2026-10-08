# Denetim çıktısı kontrolü — 8 Ekim 2026

- 105 kaynak fotoğraf, 105 ayrı gözlem/karar ve 105 güncel SVG paftası mevcut.
- SVG dosyalarının tamamı XML olarak açıldı; tümünde güncel kamera/ölçü onayı durumu var. 055 paftası ayrıca görüntülenerek kontrol edildi.
- 055 aşağı iniş sistemi ve −1; 043 üst sahanlık/+1; 042, 044, 050, 054, 066 ara kot; 067 pavyona bakış olarak veri kontrolünden geçti.
- 069, 070, 108, 116 için eski harita koordinatları kaldırılmış; 019'da kanıtsız merdiven ataması yok.
- 105 kaydın tamamında `camera_pose_verified=false`, `metric_geometry_approved=false`. Python kaynakları sözdizimi kontrolünden geçti.
- Tarayıcıda 049 seçiliyken çemberin altındaki 048 noktasına tıklandı; yakın fotoğraf listesinden 048 açıldı.
- 048 seçiliyken 047 noktasının seçili çember içinde olduğu DOM geometrisiyle kontrol edildi; `#focus` için `pointer-events:none` doğrulandı. Noktaya tıklayıp listeden, aynı konumdaki 046 fotoğrafı seçilebildi.
- Üst kat filtresi 043'ü, ara kot filtresi 5 fotoğrafı gösterdi. Denetim sayfasında 105 kart ve 055 aramasında 1/105 sonuç kontrol edildi.
- Geometri üretimi çalıştırılmadı. Bu kontroller fotoğraf pozlarının veya bina ölçülerinin doğrulandığı anlamına gelmez.

Arayüz kontrol görüntüsü: [çember içi seçim listesi](../04_Onizlemeler/atlas_cember_secim_kontrolu.jpg).
