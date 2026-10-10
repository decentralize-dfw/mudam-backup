# Mudam Virtual Experience — web demo

Kök `index.html` bu klasörden derlenir. Angora 21 görüntüleyicisinin
(`decentralize-dfw/angora`, `viewer/`) arayüz dilini ve kesit/tarama yaklaşımını
Mudam'a taşır: **Çevre · Bina · Sergiler** üçlemesi, kat kat kesit, katları
ayırma (patlatılmış aksonometri), plan ve izometrik görünüm, eser eser ve oda
oda gezinti, gerçek zamanlı gün ışığı.

## Ne nerede

| Yol | İçerik |
| --- | --- |
| `../index.html`, `../demo/app/` | Derlenmiş sayfa ve paketler (elle düzenlenmez) |
| `../demo/model/` | `building.glb`, `site.glb`, `trees.glb` — Draco + WebP |
| `../demo/data/` | Kesit kapakları, odalar, eser yerleşimi, çevre verisi (JSON) |
| `../demo/art/` | Yer tutucu eser görselleri (WebP, büyük + küçük) |
| `../demo/context/ground.webp` | OSM'den çizilen vaziyet zemini |
| `../demo/draco/` | Draco çözücü (aynı kaynaktan servis edilir) |
| `src/engine/` | Sahne, ışık, kesit bantları, kamera, eserler, odalar |
| `src/content/` | Bina ve çevre noktaları, sergiler (TR/EN) |
| `scripts/` | Model, veri ve görsel üretimi; derlemeyi köke taşıma |

## Yeniden üretim

Kaynak model `12_Blender_Model/exports/current.glb.gz`.

```sh
cd web
npm ci
npm run model   # current.glb.gz -> demo/model/*.glb  (birleştirme, sadeleştirme, Draco, WebP)
npm run data    # kesitler, odalar, duvarlar, eser yerleşimi, OSM çevresi -> demo/data/
npm run art     # yer tutucu eser görselleri -> demo/art/
npm run build   # Vite -> dist, sonra kök index.html + demo/app/
```

`npm run data` ve `npm run art` için Python 3 ile `trimesh`, `shapely`,
`scipy`, `mapbox_earcut`, `numpy`, `Pillow` gerekir. `data` eser
yerleşimini değiştirirse `art` yeniden çalıştırılmalıdır.

Model güncellendiğinde: `model` → `data` → `art` → `build`.

## Kararlar

- **Kesit:** her kat kendi kotunun ~3 m üstünden kesilir (−1: −2,35 m; 0: +3,00 m;
  +1: +7,95 m). Asılı eserlerin üstünde, tavanların altında kalır. Kesilen dolu
  hacimler `prepare_data.py` içinde düzlemle dilimlenir; kapaklar 45° taramalı
  koyu poşe olarak çizilir (Angora `section.js` gölgelendiricisi). Kaynak
  modelde tek yüzey olarak kalan duvarlar çizgi olarak gösterilir.
- **Katları ayır:** bina dört bantta çizilir (−1, 0, +1, çatı); her bandın
  kırpma düzlemleri bant kaldırıldıkça onunla birlikte taşınır.
- **Işık:** Lüksemburg için NOAA güneş konumu (yaz saati dahil), Preetham gökyüzü,
  gökten türetilen ortam ışığı, 4K gölge, GTAO. Ortam kırpılmış katları
  karartmasın diye AO, sahnenin kendi derinliğinden hesaplanır.
- **Odalar:** modelin döşeme plakalarından türetilir ve resmî 102/103/104
  planlarıyla (`kat_*_4000px.pgw`) çakıştırılarak kontrol edilmiştir.
- **Sergiler:** başlık, tarih, küratör ve açıklamalar mudam.com ve sergi
  duyurularından (10 Ekim 2026). Oda okumaları demo önerisidir; resmî bölüm
  başlıkları değildir. Duvarlardaki bütün görseller yer tutucudur.

## Hızlı kontrol

Kökte `python3 -m http.server 8765` çalıştırıp `http://localhost:8765/` açın.
Bağlantılar: `#bina`, `#cevre`, `#sergi`, `#sergi/kaiho`,
`#sergi/kaiho/galerie-est-1`, `#eser/kaiho-012`, `#bina/canopy`.
`?lang=en` İngilizce, `?q=low` düşük kalite profilini zorlar.
