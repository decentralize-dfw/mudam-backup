# Mudam Virtual Experience — web demo

Kök `index.html` bu klasörden derlenir. Angora 21 görüntüleyicisinin
(`decentralize-dfw/angora`, `viewer/`) arayüz dilini ve kesit/tarama yaklaşımını
Mudam'a taşır: **Çevre · Bina · Sergiler** üçlemesi, kat kat kesit, katları
ayırma (patlatılmış aksonometri), malzemelere ayırma (dikey ve yarım küre), plan ve izometrik görünüm, eser eser ve oda
oda gezinti, gerçek zamanlı gün ışığı.

## Ne nerede

| Yol | İçerik |
| --- | --- |
| `../index.html`, `../demo/app/` | Derlenmiş sayfa ve paketler (elle düzenlenmez) |
| `../demo/model/` | `building.glb`, `site.glb`, `trees.glb` — Draco + WebP |
| `../demo/model/cevre2/` | Çevre 2 (R151 web v002): bina, yakın ve uzak çevre — Draco + WebP |
| `../demo/data/` | Kesit kapakları, odalar, eser yerleşimi, çevre verisi, malzeme parçaları (JSON) |
| `../demo/art/` | Yer tutucu eser görselleri (WebP, büyük + küçük) |
| `../demo/context/ground.webp` | OSM'den çizilen vaziyet zemini |
| `../demo/draco/` | Draco çözücü (aynı kaynaktan servis edilir) |
| `src/engine/` | Sahne, ışık, kesit bantları, kamera, eserler, odalar |
| `src/content/` | Bina ve çevre noktaları, sergiler (TR/EN) |
| `scripts/` | Model, veri ve görsel üretimi; derlemeyi köke taşıma |

## Yeniden üretim

Kaynak model `12_Blender_Model/exports/current.glb.gz` (şu an R149).

```sh
cd web
npm ci
npm run model   # current.glb.gz -> demo/model/*.glb  (birleştirme, sadeleştirme, Draco, WebP)
                #                 + demo/data/pieces.json (malzeme katmanları)
                #                 + demo/data/walk.json (yürüme zemini, npm run walk)
npm run data    # kesitler, odalar, duvarlar, eser yerleşimi, OSM çevresi -> demo/data/
npm run art     # yer tutucu eser görselleri -> demo/art/
npm run build   # Vite -> dist, sonra kök index.html + demo/app/
```

`npm run data` ve `npm run art` için Python 3 ile `trimesh`, `shapely`,
`scipy`, `mapbox_earcut`, `numpy`, `Pillow` gerekir. `data` eser
yerleşimini değiştirirse `art` yeniden çalıştırılmalıdır.

Model güncellendiğinde: `model` → `data` → `art` → `build`.

### Çevre 1 / Çevre 2

Işık panelindeki **Model** düğmesi iki model takımı arasında geçiş yapar
(bağlantı: `?cevre=2`).

- **Çevre 1** — `current.glb.gz` (R149): bina, model sahası, ağaçlar, OSM
  çevre kütleleri ve vaziyet çizimi.
- **Çevre 2** — `12_Blender_Model/exports/web_current/` (R151 web clean v002,
  `config/r151_web_lod.json`): `building.glb.gz` (Mudam, hendek ve arazi
  dahil), `near_context.glb.gz` (temizlenmiş yakın çevre, ACT 2020),
  `far_context.glb.gz` (uzak çevre).

```sh
npm run model:cevre2   # web_current -> demo/model/cevre2/*.glb, demo/data/cevre2.json, pieces-cevre2.json
npm run build
```

R151 binası tek düğümde, malzeme başına birleşmiş gelir. Kesit, kat ayırma
ve malzeme katmanları için üçgenleri R149 parçalarına geri izlenir: her
bağlı parça köşeleriyle (1 cm) hangi R149 düğümünden geldiğini oylar
(üçgenlerin %94'ü eşleşir); eşleşmeyenler (yeniden üçgenlenmiş çubuklar,
ACT zemin geçişi) kendilerini içeren R149 parçasını, o da yoksa malzeme
adını izler. Hendek ve arazi böylece binadan ayrılır (`site.glb`). Yakın ve
uzak çevre ACT fotogrametri ağlarıdır: çizim çağrıları birleştirilir, ağ
kenarları kilitli olarak sadeleştirilir (yakın %94, uzak %88 kalır), dokular
WebP, geometri Draco olur. Uzak çevre en son, arka planda yüklenir. Kesit
kapakları, odalar ve eser yerleşimi Çevre 1 verisinden gelir.

## Kararlar

- **Kesit:** her kat kendi kotunun ~3 m üstünden kesilir (−1: −2,35 m; 0: +3,00 m;
  +1: +7,95 m). Asılı eserlerin üstünde, tavanların altında kalır. Kesilen dolu
  hacimler `prepare_data.py` içinde düzlemle dilimlenir; kapaklar 45° taramalı
  koyu poşe olarak çizilir (Angora `section.js` gölgelendiricisi). Kaynak
  modelde tek yüzey olarak kalan duvarlar çizgi olarak gösterilir.
- **Malzemelere ayır:** bina beş katmana ayrılır: döşemeler, duvarlar (taş
  kabuk), tavanlar ve çatılar, çelik ve cam çerçeveleri, camlar. "Diğer" yoktur:
  üzerinde yürünen döşemedir, duran duvardır, yukarıda asılı olan tavan ya da
  çatıdır. Cam ve çelik malzemeden ve eleman türlerinin bir kerelik
  sınıflandırmasından (`scripts/layers.json`) gelir; döşeme, duvar ve tavan
  her parçanın kendi geometrisiyle belirlenir (`build-model.mjs` →
  `classify`): yüzeyinin ne kadarının yukarı/aşağı baktığı, kalınlığı ve
  katındaki yüksekliği. `AUDIT=dosya.tsv npm run model` parça başına sonucu
  yazar. Aynı katman ve kattaki komşu parçalar 8 m'lik hücrelerde tek parça
  gibi hareket eder; her köşeye parçanın merkezi ve katmanı yazılır
  (`_PIECE`), kayma GPU'da (binanın gölgelendirici kancası), gölge geçişinde
  ve kesik iz çizgilerinde aynı formülle hesaplanır (`src/engine/explode.js`).
  *Dikey*: katmanlar ~30 m arayla üst üste kademelenir, camlar en üstte.
  *Yarım küre*: döşemeler çekirdekte kalır, diğer katmanlar binanın altındaki
  bir noktanın çevresinde 32 m arayla eşmerkezli yarım küre kabuklarına
  yerleşir. Kesik çizgiler katmanların nereden nereye gittiğini gösterir. Katlar
  ya da malzemeler ayrıldığında çevre modeli %20 opaklığa iner.
- **Bantlar ve geçişler:** bina dört bantta çizilir (−1, 0, +1, çatı). Bir bant,
  ÖZGÜN yüksekliği (bant kaldırılmadan ve malzeme görünümü parçayı taşımadan
  önceki) kendi aralığında kalan parçaları gösterir; sınama malzemelerin
  gölgelendiricisinde piksel başına yapılır. Böylece bantlar parçalarını
  kesilmeden her yere taşıyabilir: kat kesitleri, katları ayırma ve
  malzemelere ayırma aynı anda, tek hareketle birbirine geçer.
- **Katları ayır:** katlar 36 / 74 / 116 m kaldırılır; her odada planlardaki
  adını taşıyan dikey bir ok durur (`src/engine/arrows.js`).
- **İçeride gez:** dock'taki adam bir katın üstüne sürüklenip bırakılır (ya da
  tıklanır: Büyük Salon'dan başlar); göz hizasında, sürükleyerek bakılır, W A S D
  / oklar / ekrandaki oklarla yürünür, Shift hızlandırır, Esc çıkar. Zemin
  `scripts/build-walk.mjs` ile web modelinden çıkarılır: döşemeler katmanının
  yukarı bakan yüzleri 0,25 m ızgarada ayak kotlarını verir, dizden başa kadar
  vücudu kesen her şey (duvar, cam, korkuluk, alçak kiriş) o kotu kapatır,
  omuz payı bir hücre. Merdivenler basamak basamak değil, her biri tek eğimli
  bir rampa olarak yürünür: alt kattan üst kata, sahanlıklar dahil tek düz
  eğim (kaynak modeldeki basamak, burun, koridor ve köşe sahanlığı parçaları
  adlarından bulunur; 8 merdiven: Büyük Salon, foyer, batı, doğu, servis,
  pavyon sarmalı, oditoryumun iki koridoru). Böylece −1, 0 ve +1 birbirine
  bağlıdır; serbest duran eserler engeldir (`src/engine/walk.js`). Zemin
  hücre hücre değil, pürüzsüz bir alan olarak okunur: her ayak kotu en yakın
  geçilmez hücreye uzaklığını (açıklık) bilir, açıklık ve kot dört komşu hücre
  merkezi arasında doğrusal ara değerle hesaplanır. Böylece 45° duvarlar
  basamaklı değil düz bir kenardır, duvara giren adım duvar boyunca kayar
  (dik yürününce durur) ve rampada göz kare başına birkaç santimden fazla
  sıçramaz. Gölge haritası yürüyüşte bir kez, bütün binaya oturtulur.
- **Işık:** Lüksemburg için NOAA güneş konumu (yaz saati dahil), Preetham gökyüzü,
  gökten türetilen ortam ışığı, 4K gölge, GTAO. Ortam kırpılmış katları
  karartmasın diye AO, sahnenin kendi derinliğinden hesaplanır.
- **Odalar:** modelin döşeme plakalarından türetilir ve resmî 102/103/104
  planlarıyla (`kat_*_4000px.pgw`) çakıştırılarak kontrol edilmiştir.
- **Sergiler:** başlık, tarih, küratör ve açıklamalar mudam.com ve sergi
  duyurularından (10 Ekim 2026). Oda okumaları demo önerisidir; resmî bölüm
  başlıkları değildir. Duvarlardaki bütün görseller yer tutucudur.

## Diller

Açılış İngilizcedir; Fransızca, Almanca ve Lüksemburgca seçilebilir (`?lang=fr`,
`de`, `lb`). Türkçe şimdilik sunulmuyor (metinleri `src/strings.js` içinde
duruyor). Arayüz metinleri `src/strings.js` (İngilizce kaynak), içerik
`src/content/*.js`; çeviriler `src/content/i18n/{fr,de,lb}.json` dosyalarında
ve yüklemede içeriğe eklenir (`src/content/translations.js`).
`node scripts/i18n-source.mjs` İngilizce kaynağı `en.source.json` olarak yazar
ve her dilde eksik ya da fazla girdiyi listeler.

## Hızlı kontrol

Kökte `python3 -m http.server 8765` çalıştırıp `http://localhost:8765/` açın.
Bağlantılar: `#bina`, `#cevre`, `#sergi`, `#sergi/kaiho`,
`#sergi/kaiho/galerie-est-1`, `#eser/kaiho-012`, `#bina/canopy`,
`#bina/katlar`, `#bina/malzeme-dikey`, `#bina/malzeme-kure`.
`?lang=fr|de|lb` dili, `?q=low` düşük kalite profilini seçer.
