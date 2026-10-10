# MUDAM

Mudam mimari referans arşivi, OSM ile hizalanmış planlar, fotoğraf konum atlası ve ayrıntılı Blender modelleme planı.

## Sanal deneyim demosu

Sitenin kökü ([`index.html`](index.html)) Mudam Virtual Experience demosunu açar (İngilizce; Fransızca, Almanca ve Lüksemburgca seçilebilir): **Surroundings · Building · Exhibitions**. Bina kat kat kesilir, kesilen duvarlar taranır, katlar ayrılır; bina malzemelerine (döşeme, duvar, tavan ve çatı, çelik-cam çerçeve, cam) dikey ya da yarım küre biçiminde ayrılır, katlar ayrıldığında her odada plan adıyla bir ok durur; plan ve izometrik kesitte oda oda, birinci şahıs görünümünde eser eser gezilir; gün ışığı ve iç ışıklar değiştirilebilir; Çevre 1 (R149 modeli ve OSM çevresi) ile Çevre 2 (R151 web clean v002: bina ve ACT 2020 yakın/uzak çevre) arasında geçilir. Güncel sergiler (10 Ekim 2026): alt katta *Video Killed the Radio Star*, pavyonda *Christine Sun Kim: FOR EVER*, zemin ve üst katta *Kaihō: Japanese Women Artists after 1945*. Duvarlardaki görseller yer tutucudur. Kaynak, model/veri üretimi ve derleme: [`web/README.md`](web/README.md).

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

Blender üretimi P05 ana kabuk etüdüne ilerledi. [Görsel inceleme](12_Blender_Model/URETIM.html) · [İş durumu ve güncel dosyalar](12_Blender_Model/URETIM_DURUMU.md). Üç kat, ana cephe ve çatı kütleleri, pavyon ve geçit düzenlenebilir nesnelerdir. Açıklıklar, ana çatı alt yüzeyleri ve detaylar sürüyor. Planlar ölçülmüş uygulama projesi değildir; OSM eşleştirme farkları ve fotoğraf konumu tahminleri ilgili raporlarda açıklanır.

8 Ekim 2026 denetiminde 105 fotoğraf tek tek incelendi, 42 kayıtta atama/açıklama revizyonu yapıldı. Güncel durum: 35 konum/yön hipotezi, 45 aday bölge, 25 harita noktası olmayan görüntü. Doğrulanmış metrik kamera pozu yoktur. `12_Blender_Model` içindeki yeni P03/P04 betikleriyle üretim sürüyor. Eski `build_mudam.py`, şema çizgi kalınlıklarını duvar kabul ettiği ve çözülmemiş çatı/pencere varsayımları içerdiği için kapalı tutuluyor. Yeni etüt kotları da doğrulanmış ölçü değildir.

## Kaynaklar ve krediler

Görsellerin kaynakları, dosya bazında kredileri ve indirme kayıtları `00_Kaynaklar/envanter.json` içinde tutulur. Üçüncü taraf görselleri için bu depo yeni bir kullanım lisansı vermez. OSM verisi © OpenStreetMap contributors, ODbL kapsamındadır.

Yerel `.deps` bağımlılıkları ve Python önbellekleri sürüm kontrolüne dahil değildir. Üretim betikleri için gereken Python ortamı ayrıca kurulmalıdır; mevcut HTML ve görsel çıktıları görüntülemek bu bağımlılıkları gerektirmez.
