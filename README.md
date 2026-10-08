# MUDAM

Mudam mimari referans arşivi, OSM ile hizalanmış planlar, fotoğraf konum atlası ve ayrıntılı Blender modelleme planı.

## Başlangıç

- [Kaynak ve görsel kataloğu](KATALOG.html)
- [İnteraktif plan ve fotoğraf atlası](10_Olcekli_Plan_ve_Fotograf_Analizi/FOTOGRAF_ATLASI.html)
- [Blender modelleme ana planı](11_Blender_Modelleme_Plani/00_MODELLEME_ANA_PLANI.md)
- [Ölçek ve doğruluk raporu](10_Olcekli_Plan_ve_Fotograf_Analizi/KALIBRASYON_RAPORU.txt)
- [İletişim notları](iletisim.md)

HTML dosyalarını depoyu indirdikten sonra tarayıcıda açabilirsiniz. Alternatif olarak depo kökünde `python -m http.server 8765` çalıştırıp `http://localhost:8765/KATALOG.html` adresini ziyaret edin.

## İçerik

`00_Kaynaklar` kaynak envanteri ve toplama betiklerini; `01`–`08` plan, kesit, peyzaj, iç/dış mekân ve belge arşivini; `09_Onizlemeler` görsel katalog paftalarını içerir. `10_Olcekli_Plan_ve_Fotograf_Analizi` ölçekli çıktılar ve 105 fotoğrafın analizidir. `11_Blender_Modelleme_Plani` üretim planı, 23 iş paketi ve 35 başlangıç parametresidir.

Henüz Blender modeli üretilmedi. Planlar ölçülmüş uygulama projesi değildir; OSM eşleştirme farkları ve fotoğraf konumu tahminleri ilgili raporlarda açıklanır.

## Kaynaklar ve krediler

Görsellerin kaynakları, dosya bazında kredileri ve indirme kayıtları `00_Kaynaklar/envanter.json` içinde tutulur. Üçüncü taraf görselleri için bu depo yeni bir kullanım lisansı vermez. OSM verisi © OpenStreetMap contributors, ODbL kapsamındadır.

Yerel `.deps` bağımlılıkları ve Python önbellekleri sürüm kontrolüne dahil değildir. Üretim betikleri için gereken Python ortamı ayrıca kurulmalıdır; mevcut HTML ve görsel çıktıları görüntülemek bu bağımlılıkları gerektirmez.
