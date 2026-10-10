// Building hotspots. Facts follow the sources archived in this repository
// (00_Kaynaklar: mudam.com architecture page, WikiArquitectura, ArchEyes,
// Great Gardens / Michel Desvigne). Positions are model coordinates (x east,
// y up, z south); `view` frames the camera: target, compass bearing the
// camera stands at, tilt above the horizon, zoom, and the floor state.
export const BUILDING_HOTSPOTS = [
  {
    id: 'form',
    at: [-14, 15, -33], n: [0, 1, 0],
    view: { target: [4, 4, -6], bearing: 30, tilt: 68, zoom: 1.25, state: 'all' },
    tr: {
      title: 'Ok ucu: kaleden doğan plan',
      kicker: 'Tasarım',
      body: [
        'I. M. Pei müzeyi, 1732’de inşa edilen Thüngen Kalesi’nin ok ucu biçimli tabyasının üzerine oturttu. V biçimli kütle tabya duvarlarının izini sürer; planın geometrisi 45°’lik açılar üzerine kuruludur.',
        'Okun ucu, girişiyle Kirchberg’e ve Place de l’Europe’a yönelir; camlı güneybatı cephesi ise tarihî kente bakar. Bina böylece kale ile Avrupa mahallesi, geçmiş ile bugün arasında bir yön çizgisi kurar.',
      ],
    },
    en: {
      title: 'The arrowhead: a plan drawn from the fort',
      kicker: 'Design',
      body: [
        'I. M. Pei set the museum on the arrowhead-shaped bastion of Fort Thüngen, built in 1732. The V-shaped volume follows the bastion walls, and the plan is built on 45° angles.',
        'The tip, holding the entrance, points to Kirchberg and Place de l’Europe; the glazed south-west front faces the historic city. The building draws a line between the fortress and the European district, between past and present.',
      ],
    },
  },
  {
    id: 'canopy',
    at: [5.9, 28, -11.4], n: [0, 1, 0],
    view: { target: [4, 17, -10], bearing: 228, tilt: 32, zoom: 2.4, state: 'all' },
    tr: {
      title: 'Cam kanopi ve fener',
      kicker: 'Cam örtü',
      body: [
        'Grand Hall’ü örten cam ve çelik kanopi, kare tepeli bir fenerle taçlanır; yapının en yüksek noktası burasıdır.',
        'Üçgen cam panellerin arasına yerleştirilen ince metal tüpler güneşi süzer ve salonun akustiğine katkı verir. Kanopinin iki yanında, iki cam salonu örten daha alçak ve yatık cam çatılar uzanır.',
      ],
    },
    en: {
      title: 'Glass canopy and lantern',
      kicker: 'Glass roof',
      body: [
        'A glass-and-steel canopy covers the Grand Hall, crowned by a square-topped lantern: the highest point of the building.',
        'Thin metal tubes set between the triangular panes filter the sunlight and help the hall’s acoustics. On either side, lower and flatter glass roofs cover the two glazed halls.',
      ],
    },
  },
  {
    id: 'grandhall',
    at: [-3.7, 7.5, -2.5], n: [-0.73, 0.1, 0.68],
    view: { target: [5, 0, -10], bearing: 222, tilt: 48, zoom: 2.6, state: 'L00' },
    tr: {
      title: 'Grand Hall',
      kicker: 'Mekân',
      body: [
        'Girişten sonra ziyaretçi ışıkla dolu, kolonsuz Grand Hall’e ulaşır. Müzenin kalbi olan salon bir dağıtıcıdır: galerilere, iki cam salona ve alt kata buradan geçilir.',
        'Cam yüzeyler eski kaleye ve parka bakar. Salon, ziyaret saatleri dışında müze kabulleri ve resmî törenler için de kullanılır.',
      ],
    },
    en: {
      title: 'Grand Hall',
      kicker: 'Space',
      body: [
        'Past the entrance, visitors arrive in the column-free, light-filled Grand Hall. The heart of the museum, it distributes the visit: galleries, the two glazed halls and the lower level are all reached from here.',
        'Its glass looks out to the old fort and the park. Outside opening hours the hall hosts museum receptions and official functions.',
      ],
    },
  },
  {
    id: 'jardin',
    at: [9.3, 8.5, 17.7], n: [-0.6, 0.55, 0.55],
    view: { target: [10, 3, 16], bearing: 235, tilt: 34, zoom: 2.3, state: 'all' },
    tr: {
      title: 'Jardin des Sculptures',
      kicker: 'Cam salon · doğu',
      body: [
        'Grand Hall’ün doğusundaki cam örtülü salon, heykel ve mekâna özgü işler için kurgulanmış bir iç bahçedir. Eğimli cam çatı gün boyunca değişen bir ışık verir.',
        'Salonun ucundaki camlı geçit, kale kalıntılarının üzerinden pavyona bağlanır.',
      ],
    },
    en: {
      title: 'Jardin des Sculptures',
      kicker: 'Glazed hall · east',
      body: [
        'The glass-roofed hall east of the Grand Hall is an indoor garden for sculpture and site-specific work. Its sloping glass roof gives a light that changes through the day.',
        'At its far end, a glazed passage crosses the fortress remains to the pavilion.',
      ],
    },
  },
  {
    id: 'cafe',
    kind: 'cafe',
    at: [-23.4, 8.5, -15.5], n: [-0.6, 0.55, 0.55],
    view: { target: [-22, 3, -16], bearing: 222, tilt: 36, zoom: 2.4, state: 'all' },
    tr: {
      title: 'Mudam Café',
      kicker: 'Cam salon · batı · bilgi noktası',
      body: [
        'Grand Hall’ün batısındaki cam salon (kış bahçesi) müzenin kafesidir; burada sergi yer almaz.',
        'Kafe-restoranı Chiche! işletiyor: ev yapımı yemeği sosyal uyumla buluşturan, Lüksemburg’daki göçmen ve mültecilerin istihdam, eğitim ve topluma katılımını destekleyen bir girişim. Cam cepheden kale duvarlarına ve parka bakılır.',
      ],
    },
    en: {
      title: 'Mudam Café',
      kicker: 'Glazed hall · west · info point',
      body: [
        'The glazed hall west of the Grand Hall (the winter garden) is the museum café; there is no exhibition here.',
        'It is run by Chiche!, a restaurant bringing together home-made food and social cohesion while supporting access to employment, education and integration for migrants and refugees in Luxembourg. The glass looks out to the fortress walls and the park.',
      ],
    },
  },
  {
    id: 'stone',
    at: [36.6, 7.5, -9.5], n: [1, 0, 0.1],
    view: { target: [34, 5, -9], bearing: 80, tilt: 22, zoom: 2.6, state: 'all', hour: 9.3 },
    tr: {
      title: 'Magny Doré kireçtaşı',
      kicker: 'Malzeme',
      body: [
        'Cepheler bal rengi Fransız kireçtaşı Magny Doré ile kaplıdır; aynı taş kamusal iç mekânlarda da sürer. Taşın sıcak tonu saat ve mevsimle değişen ışık ve gölgeyle canlanır.',
        'Açık renkli mimari beton ve dolgulu derzlerle birlikte yapıya monolitik bir ifade verir. Bu nokta açıldığında ışık, doğu cephesine sabah güneşinin vurduğu saate alınır; gün ışığı kaydırıcısıyla taşın tonunu siz de değiştirebilirsiniz.',
      ],
    },
    en: {
      title: 'Magny Doré limestone',
      kicker: 'Material',
      body: [
        'The façades are clad in Magny Doré, a honey-coloured French limestone that continues into the public interiors. Its warm tone comes alive with light and shadow that shift through the hours and seasons.',
        'With light architectural concrete and filled joints, it gives the building a monolithic expression. Opening this point sets the light to the morning, when the sun reaches this east front; use the daylight slider to see the stone change.',
      ],
    },
  },
  {
    id: 'entrance',
    at: [29.7, 5.5, -35.5], n: [0.73, 0, -0.68],
    view: { target: [28, 3, -33], bearing: 45, tilt: 26, zoom: 2.6, state: 'all' },
    tr: {
      title: 'Giriş: okun ucu',
      kicker: 'Varış',
      body: [
        'Ziyaretçi Place de l’Europe yönünden gelir, tarihî hendeği köprülerle aşar ve okun ucundaki girişe ulaşır.',
        'Taş kütlenin içine çekilmiş camlı rüzgârlık ve üstündeki saçak girişi korunaklı kılar; sivri köşe ise kütlenin keskinliğini korur.',
      ],
    },
    en: {
      title: 'Entrance: the tip of the arrow',
      kicker: 'Arrival',
      body: [
        'Visitors arrive from Place de l’Europe, cross the historic moat on bridges and reach the entrance at the tip of the arrow.',
        'A glazed vestibule set back into the stone mass, with a canopy above, shelters the way in, while the sharp corner keeps the volume crisp.',
      ],
    },
  },
  {
    id: 'corner',
    at: [37.7, 10.5, -23.9], n: [0.85, 0, -0.5],
    view: { target: [36, 6, -23], bearing: 60, tilt: 18, zoom: 3.4, state: 'all' },
    tr: {
      title: 'Köşe detayı: taş kütle',
      kicker: 'Detay',
      body: [
        'Galeri kanatlarının dış köşeleri okun keskinliğini taşır. Köşede buluşan taş yüzeyler ve dolgulu derzler kütleyi ince bir kaplama gibi değil, som bir blok gibi okutur.',
        'Pei’nin 45°’lik geometrisi en açık biçimde bu köşelerde hissedilir; açıklıklar köşeden geri çekilir, köşe sağır ve net kalır.',
      ],
    },
    en: {
      title: 'Corner detail: the stone mass',
      kicker: 'Detail',
      body: [
        'The outer corners of the gallery wings carry the sharpness of the arrow. Stone faces meeting at the corner, with filled joints, read as a solid block rather than a thin cladding.',
        'Pei’s 45° geometry is felt most clearly here: openings step back from the corner, which stays blind and precise.',
      ],
    },
  },
  {
    id: 'glasscorner',
    at: [-32.6, 11, -23.4], n: [-0.65, 0.15, -0.74],
    view: { target: [-30, 6, -24], bearing: 300, tilt: 22, zoom: 2.9, state: 'all' },
    tr: {
      title: 'Köşe detayı: cam ile taş',
      kicker: 'Detay',
      body: [
        'Batı uçta camla kaplı merdiven kulesi taş kanadın ucuna eklenir. İnce çerçeveli cam yüzey ile kireçtaşının ağır kütlesi aynı köşede yan yana gelir; iki malzemenin sınırı açıkça okunur.',
        'Merdiveni kullanan ziyaretçi, katlar arasında dışarıyı görür.',
      ],
    },
    en: {
      title: 'Corner detail: glass and stone',
      kicker: 'Detail',
      body: [
        'At the west end a glazed stair tower is added to the tip of the stone wing. The finely framed glass and the heavy limestone meet at one corner, and the line between the two materials stays legible.',
        'Climbing the stair, visitors see outside between floors.',
      ],
    },
  },
  {
    id: 'skylights',
    at: [27, 14.2, -4], n: [0, 1, 0],
    view: { target: [22, 9, -8], bearing: 120, tilt: 52, zoom: 2.2, state: 'all' },
    tr: {
      title: 'Üst galeriler: tepe ışığı',
      kicker: 'Işık',
      body: [
        'Üst kattaki iki büyük galeri doğal ışıkla sergilemeye olanak verir: çatıdaki ışıklıklar gün ışığını galeri duvarlarına süzer.',
        'Bazı salonların çatıları duvar seviyesinin altında kaldığı için dışarıdan görünmez; kütle dışarıdan sakin, içeride aydınlıktır.',
      ],
    },
    en: {
      title: 'Upper galleries: top light',
      kicker: 'Light',
      body: [
        'The two large upper galleries allow exhibitions in natural light: roof lights filter daylight onto the gallery walls.',
        'Some roofs sit below the parapet and are invisible from outside, so the volume stays calm outside and bright within.',
      ],
    },
  },
  {
    id: 'pavilion',
    at: [29.2, 16, 42.9], n: [0, 1, 0],
    view: { target: [27, 4, 40], bearing: 160, tilt: 30, zoom: 2.6, state: 'all' },
    tr: {
      title: 'Henry J. ve Erna D. Leir Pavyonu',
      kicker: 'Pavyon',
      body: [
        'Ana binanın arkasındaki sekizgen pavyona, kale kalıntılarının üzerinden geçen camlı bir geçitle ulaşılır. Cam bir fenerle taçlanan pavyon parka bir pencere daha açar.',
        'İki katlıdır; alt kata merdivenle inilir. Şu anda Christine Sun Kim’in FOR EVER sergisi zemin katında.',
      ],
    },
    en: {
      title: 'Henry J. and Erna D. Leir Pavilion',
      kicker: 'Pavilion',
      body: [
        'The octagonal pavilion behind the main building is reached by a glazed passage crossing the fortress remains. Crowned with a glass lantern, it opens another view onto the park.',
        'It has two levels; the lower one is reached by stair. Christine Sun Kim’s FOR EVER is currently on its ground floor.',
      ],
    },
  },
  {
    id: 'passage',
    at: [19.3, 5, 32.2], n: [0, 1, 0.2],
    view: { target: [19, 1, 32], bearing: 200, tilt: 30, zoom: 3.2, state: 'all' },
    tr: {
      title: 'Camlı geçit',
      kicker: 'Bağlantı',
      body: [
        'Geçit, Jardin des Sculptures’ün ucundan pavyona uzanır ve 18. yüzyıl tabya kalıntılarının üzerinden geçer.',
        'Yürürken bir yanda kalenin taş duvarları, diğer yanda park görünür: yeni yapı eski kalenin izini kesmeden onun üzerinden geçer.',
      ],
    },
    en: {
      title: 'Glazed passage',
      kicker: 'Link',
      body: [
        'The passage runs from the end of the Jardin des Sculptures to the pavilion, crossing the remains of the 18th-century bastion.',
        'Walking through, the fortress walls lie on one side and the park on the other: the new building passes over the old trace without breaking it.',
      ],
    },
  },
  {
    id: 'bastion',
    at: [8, -1.5, 44], n: [-0.3, 0.6, 0.75],
    view: { target: [14, -3, 38], bearing: 190, tilt: 30, zoom: 2.4, state: 'all' },
    tr: {
      title: 'Tabya duvarları ve hendek',
      kicker: 'Kale',
      body: [
        'Ok biçimli müze, 18. yüzyıl tabyasının seddine ve duvarlarına dışarıdan biner. Eski duvarlar yeni yapıyla birleşerek yerin tarihini sürdürür.',
        'Binayı çevreleyen hendek, Avrupa’nın en tahkimli kentlerinden biri olan Lüksemburg’un savunma düzeninden kalmıştır.',
      ],
    },
    en: {
      title: 'Bastion walls and moat',
      kicker: 'Fortress',
      body: [
        'The arrow-shaped museum rides over the embankment and walls of the 18th-century bastion. The old walls merge with the new building and carry the history of the place forward.',
        'The moat around it is a remnant of the defences of Luxembourg, once one of the most heavily fortified cities in Europe.',
      ],
    },
  },
  {
    id: 'stairs',
    at: [-5.9, 1.4, -11.8], n: [0, 1, 0],
    view: { target: [0, 0, -10], bearing: 230, tilt: 56, zoom: 3.0, state: 'L00' },
    tr: {
      title: 'Merdivenler',
      kicker: 'Beton',
      body: [
        'Müzenin bütün merdivenleri başlı başına mimari işlerdir. Katları bağlayan merdivenler, Oregon çamı kalıpla ince bir doku verilen açık renkli mimari betondan dökülmüştür.',
        'Grand Hall’den alt kata inen geniş merdiven ile doğu uçtaki döner merdiven, katlar arasındaki iki farklı karakteri temsil eder.',
      ],
    },
    en: {
      title: 'Stairs',
      kicker: 'Concrete',
      body: [
        'Every stair in the museum is a piece of architecture in its own right. They are cast in light architectural concrete, given a fine texture by Oregon pine formwork.',
        'The broad stair down from the Grand Hall and the spiral stair at the east end give the movement between floors two distinct characters.',
      ],
    },
  },
  {
    id: 'lowerwindows',
    at: [36.4, -2, -6.9], n: [1, 0, 0.15],
    view: { target: [34, -2, -7], bearing: 75, tilt: 16, zoom: 3.0, state: 'all' },
    tr: {
      title: 'Hendeğe açılan pencereler',
      kicker: 'Cephe',
      body: [
        'Sergi galerilerinin toplandığı yüz, duvara gömülü açıklıklarla delinir; alt kattaki pencereler hendeğe bakar.',
        'Tamamen camla kaplı güneybatı cephesinin aksine bu yüz kapalı ve ölçülüdür: eserler için korunaklı, kale için sessiz.',
      ],
    },
    en: {
      title: 'Windows onto the moat',
      kicker: 'Façade',
      body: [
        'The side where the galleries are concentrated is pierced by recessed openings; on the lower level the windows look into the moat.',
        'Unlike the fully glazed south-west front, this side is closed and measured: sheltering for the works, quiet toward the fort.',
      ],
    },
  },
];
