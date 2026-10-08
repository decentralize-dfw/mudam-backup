# MUDAM

Mudam mimari referans arşivi, OSM ile hizalanmış planlar, fotoğraf konum atlası ve ayrıntılı Blender modelleme planı.

## Başlangıç

- [Kaynak ve görsel kataloğu](KATALOG.html)
- [İnteraktif plan ve fotoğraf atlası](10_Olcekli_Plan_ve_Fotograf_Analizi/FOTOGRAF_ATLASI.html)
- [105 fotoğrafın tek tek denetimi](10_Olcekli_Plan_ve_Fotograf_Analizi/06_Tek_Tek_Denetim/DENETIM.html)
- [Denetim raporu ve düzeltmeler](10_Olcekli_Plan_ve_Fotograf_Analizi/06_Tek_Tek_Denetim/FOTOGRAF_DENETIMI.md)
- [Blender modelleme ana planı](11_Blender_Modelleme_Plani/00_MODELLEME_ANA_PLANI.md)
- [Ölçek ve doğruluk raporu](10_Olcekli_Plan_ve_Fotograf_Analizi/KALIBRASYON_RAPORU.txt)
- [İletişim notları](iletisim.md)

HTML dosyalarını depoyu indirdikten sonra tarayıcıda açabilirsiniz. Alternatif olarak depo kökünde `python -m http.server 8765` çalıştırıp `http://localhost:8765/KATALOG.html` adresini ziyaret edin.

## İçerik

`00_Kaynaklar` kaynak envanteri ve toplama betiklerini; `01`–`08` plan, kesit, peyzaj, iç/dış mekân ve belge arşivini; `09_Onizlemeler` görsel katalog paftalarını içerir. `10_Olcekli_Plan_ve_Fotograf_Analizi` ölçekli çıktılar ve 105 fotoğrafın analizidir. `11_Blender_Modelleme_Plani` üretim planı, 23 iş paketi ve 35 başlangıç parametresidir.

Henüz Blender modeli üretilmedi. Planlar ölçülmüş uygulama projesi değildir; OSM eşleştirme farkları ve fotoğraf konumu tahminleri ilgili raporlarda açıklanır.

8 Ekim 2026 denetiminde 105 fotoğraf tek tek incelendi, 42 kayıtta atama/açıklama revizyonu yapıldı. Güncel durum: 35 konum/yön hipotezi, 45 aday bölge, 25 harita noktası olmayan görüntü. Doğrulanmış metrik kamera pozu yoktur. `12_Blender_Model` başlangıç betiklerini içerir; yanlış referanslarla ilerlememesi için üretim, `config/reference_gate.json` tarafından durdurulmuştur. Taslak yükseklikler ve geometri henüz onaylı değildir.

## Kaynaklar ve krediler

Görsellerin kaynakları, dosya bazında kredileri ve indirme kayıtları `00_Kaynaklar/envanter.json` içinde tutulur. Üçüncü taraf görselleri için bu depo yeni bir kullanım lisansı vermez. OSM verisi © OpenStreetMap contributors, ODbL kapsamındadır.

Yerel `.deps` bağımlılıkları ve Python önbellekleri sürüm kontrolüne dahil değildir. Üretim betikleri için gereken Python ortamı ayrıca kurulmalıdır; mevcut HTML ve görsel çıktıları görüntülemek bu bağımlılıkları gerektirmez.
