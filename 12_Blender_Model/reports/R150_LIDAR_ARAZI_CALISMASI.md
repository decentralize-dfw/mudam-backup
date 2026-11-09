# R150 — LiDAR arazi çalışması, henüz kabul edilmedi

Resmî ACT 2024 verisinin Mudam çevresindeki 198×217 m kesiti arşivlendi. Kaynak raster 0.5 m çözünürlükte, EPSG:2169; model EPSG:32632. Kaynak SHA256 ve indirme penceresi references/terrain_lidar2024/manifest.json içindedir.

https://data.public.lu/fr/datasets/lidar-2024-releve-3d-du-territoire-luxembourgeois/

Mevcut iki hendek sınırı değiştirilmeden 2,750.389 + 257.895 = 3,008.284 m² yatay kapsama sahip iki eğimli kapalı gövde üretildi. 1 m üçgenleme kullanıldı. Giriş yaklaşımındaki 12 noktadan alınan medyan ulusal yükseklik 316.151 m model sıfırına bağlandı; noktalar arasındaki 0.186 m fark ve mevcut plan/OSM yatay belirsizliği nedeniyle bu bağ rölöve değildir.

R150 v001 yalnız R35_MOAT_GROUND ve R68_MOAT_GROUND nesnelerini değiştirdi. Diğer 9,365 miras nesne karşılaştırması geçti. İki gövdede manifold/pozitif hacim/sıfır alan kontrolleri temizdir; bu üretim kabulü sağlamaz.

**v001 kabul edilmedi:** önce/sonra görsellerinde rasterin köprü altına taşıdığı yüksek yüzeyler köprü kaplamasından çıkıyor. Pavyon kolunda gerçek arazi adayı eski duvar tabanının yaklaşık 5 m altına iniyor; duvar altı bağlantısı da açık. Bu sahne config/checkpoint_extensions.json içine eklenmedi, GLB ve web R149 olarak korundu.

Sonraki işlem: aynı resmî COPC nokta bulutundan class 2 zemin ve class 13 köprü ayrımı; köprü altında gerçek zemin örneklerinin kapsamını ölçmek. Eksik örnekler varsa bunları ölçülmüş saymadan açıkça ayırmak. Ardından duvar altı sınırlarını gerçek zeminle eşlemek; mevcut bina kotunu topluca değiştirmemek.

Araçlar: fetch_local_terrain_crop.py, prepare_lidar_moat.py, build_lidar_moat_candidate.py, render_lidar_moat_candidate.py; geçici GIS bağımlılıkları .local_source_cache/gis_runtime içinde. Kaynak noktalar için inspect_lidar_tile_archive.py ve fetch_lidar_ground_points.py kullanılır. Büyük ZIP tamamen indirilmez; sıkıştırılmamış COPC üyelerinden HTTP byte aralıkları okunur. Tam ZIP SHA1 doğrulanmadığı ayrıca kaydedilir.

Bu çalışma kaynak ve aday geometri ilerlemesidir. Kabul edilmiş mimari kapsam puanı %73.913 / %74 olarak kaldı. Yeni push yapılmadı.

Nokta bulutu indeksi: Lidar2024_C020_R013 arşivindeki 77500_76000.laz ve 78000_76000.laz COPC üyeleri hedef alanı kapsar. Üyeler ZIP_STORED olduğundan COPC aralıklarına doğrudan erişilebilir. İlk iki boyutlu laspy sorgusu sonsuz Z sınırlarının tamsayı dönüşümünden dolayı boş çıktı; 200–400 m açık Z sınırlarıyla düzeltildi. Boş sonuç doğrulanmış kaynak değildir.

Nokta sorgusu tamamlandı: 2,229,465 nokta; 1,068,508 class 2 zemin noktası. 26 MB yerel sıkıştırılmış kaynak ve SHA256 points_manifest.json ile kaydedildi. Son başarılı deneme önbellekten okudu; downloaded_range_bytes=0 yalnız o denemenin yeni ağ baytıdır.

İlk boş sonuç hatasının asıl sayısal sebebi karonun çok küçük LAS ölçeğidir (~1.16e-7 m XY, ~3–5e-8 m Z). Karo dışındaki sorgu sınırları int32 aralığını aşıyordu. Sorgu her karonun kendi min/max sınırına kırpılınca dolu sonuç alındı; kaynakta nokta yokluğu iddiası geçersizdir.

Köprü poligonu içindeki class 2 noktalarının sayısı 24,474, medyan ulusal kotu 316.14 m: bunların çoğu gerçek köprü kaplamasıdır. Aynı poligonda class 13 bulunmadı. Bu nedenle yalnız class 2 seçmek yeterli değildir; modelin köprü sınırı ve yerel kaplama kotuyla yüksek noktalar maskelenmeli. Köprü altındaki düşük noktaların kapsamı ve komşu gerçek zemin mesafesi ölçülmeden interpolasyon kabul edilmemeli. reports/R150_bridge_point_evidence.json sınıf ve kot dağılımını tutar.
