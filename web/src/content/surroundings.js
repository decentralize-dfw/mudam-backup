// Surroundings hotspots. Positions are the OSM features in the repository's
// extract (10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri), converted to the
// model frame. Places in the valley lie well below the plateau; their pins
// mark direction and position, not height.
export const SURROUNDING_HOTSPOTS = [
  {
    id: 'thungen',
    at: [-53, 14, 44],
    view: { target: [-30, 2, 25], bearing: 210, tilt: 34, zoom: 1.3 },
    tr: {
      title: 'Thüngen Kalesi · Musée Dräi Eechelen',
      kicker: 'Komşu · 18. yüzyıl',
      body: [
        'Mudam’ın hemen yanındaki kale 1732’de, Avusturya yönetimi döneminde inşa edildi. Kulelerin tepesindeki palamut biçimli taşlar ona Lüksemburgca “Dräi Eechelen”, yani “Üç Palamut” adını verir.',
        'Kale bugün kale, tarih ve kimlik üzerine kurulu Musée Dräi Eechelen’e ev sahipliği yapıyor. Mudam bu kalenin tabyası üzerinde yükselir.',
      ],
    },
    en: {
      title: 'Fort Thüngen · Musée Dräi Eechelen',
      kicker: 'Neighbour · 18th century',
      body: [
        'The fort right next to Mudam was built in 1732, under Austrian rule. The acorn-shaped stones on its towers give it the Luxembourgish name “Dräi Eechelen”: three acorns.',
        'Today it houses the Musée Dräi Eechelen, devoted to the fortress, history and identity. Mudam rises on this fort’s bastion.',
      ],
    },
  },
  {
    id: 'park',
    at: [-105, 2, 112],
    view: { target: [-50, 0, 60], bearing: 200, tilt: 42, zoom: 0.75 },
    tr: {
      title: 'Dräi Eechelen Parkı',
      kicker: 'Peyzaj · Michel Desvigne',
      body: [
        'Peyzaj mimarı Michel Desvigne’in tasarladığı park, 2011’de Lüksemburg Mimarlık Ödülü’nü aldı. Kentsel Place de l’Europe’tan kalenin doğal çevresine doğru hafifçe alçalır.',
        'Derzleri çimle dolu kaplamalar, ağaç kümeleri ve yeniden açılan geniş düzlük, Vauban’dan bu yana üç yüzyıllık askerî mühendisliğin katmanlarını okunur kılar.',
      ],
    },
    en: {
      title: 'Dräi Eechelen Park',
      kicker: 'Landscape · Michel Desvigne',
      body: [
        'Designed by landscape architect Michel Desvigne, the park received the Luxembourg Prize for Architecture in 2011. It slopes gently from the urban Place de l’Europe toward the natural setting of the fort.',
        'Grass-jointed paving, clusters of trees and a re-opened clearing make three centuries of military engineering, since Vauban, legible.',
      ],
    },
  },
  {
    id: 'moat',
    at: [36, 2, -50],
    view: { target: [30, 0, -40], bearing: 40, tilt: 36, zoom: 1.6 },
    tr: {
      title: 'Hendek ve köprüler',
      kicker: 'Varış yolu',
      body: [
        'Müzeye Place de l’Europe yönünden, tarihî hendeği aşan köprülerle varılır; giriş okun ucundadır.',
        'Hendek ve duvarlar, bir zamanlar Avrupa’nın en tahkimli kentlerinden biri olan Lüksemburg’un savunma sisteminin parçasıdır.',
      ],
    },
    en: {
      title: 'Moat and bridges',
      kicker: 'Approach',
      body: [
        'The museum is reached from Place de l’Europe over bridges that cross the historic moat; the entrance is at the tip of the arrow.',
        'The moat and walls belong to the defences of Luxembourg, once one of the most heavily fortified cities in Europe.',
      ],
    },
  },
  {
    id: 'europe',
    at: [150, 2, -108],
    view: { target: [90, 0, -80], bearing: 50, tilt: 40, zoom: 0.8 },
    tr: {
      title: 'Place de l’Europe',
      kicker: 'Meydan · Ricardo Bofill',
      body: [
        'Müzenin önündeki çam ve kayınlarla düzenlenmiş meydan, Ricardo Bofill’in tasarladığı Place de l’Europe’a bağlanır.',
        'Philharmonie ile birlikte Kirchberg’in kültür kapısını oluşturur; park buradan kaleye doğru açılır.',
      ],
    },
    en: {
      title: 'Place de l’Europe',
      kicker: 'Square · Ricardo Bofill',
      body: [
        'The forecourt in front of the museum, planted with pines and beeches, opens onto Place de l’Europe, designed by Ricardo Bofill.',
        'Together with the Philharmonie it forms Kirchberg’s cultural gateway; from here the park opens toward the fort.',
      ],
    },
  },
  {
    id: 'philharmonie',
    at: [181, 26, -170],
    view: { target: [120, 5, -120], bearing: 60, tilt: 34, zoom: 0.75 },
    tr: {
      title: 'Philharmonie Luxembourg',
      kicker: 'Konser salonu · Christian de Portzamparc',
      body: [
        'Christian de Portzamparc’ın tasarladığı konser salonu 2005’te açıldı. Beyaz çelik sütunlardan oluşan, filtre gibi işleyen cephesi Place de l’Europe’u çevreler.',
        'Mudam’ın taş ve cam kütlesinin hemen komşusu olarak Kirchberg’deki kültür kümesinin öteki ucudur.',
      ],
    },
    en: {
      title: 'Philharmonie Luxembourg',
      kicker: 'Concert hall · Christian de Portzamparc',
      body: [
        'Christian de Portzamparc’s concert hall opened in 2005. Its façade of white steel columns, working like a filter, wraps Place de l’Europe.',
        'A close neighbour of Mudam’s stone-and-glass mass, it marks the other end of Kirchberg’s cultural cluster.',
      ],
    },
  },
  {
    id: 'kirchberg',
    at: [5, 24, -330],
    view: { target: [10, 5, -270], bearing: 25, tilt: 34, zoom: 0.55 },
    tr: {
      title: 'Kirchberg: Avrupa mahallesi',
      kicker: 'Plato',
      body: [
        'Mudam’ın girişi Avrupa kurumlarının yer aldığı Kirchberg platosuna yönelir. Avrupa Birliği Adalet Divanı’nın altın renkli kuleleri ve Avrupa Yatırım Bankası bu yöndedir.',
        'Müzenin yerleşimi, kale ve tarihî kent ile Avrupa mahallesi arasında, geçmiş ile bugün ve gelecek arasında bir bağ kurar.',
      ],
    },
    en: {
      title: 'Kirchberg: the European district',
      kicker: 'Plateau',
      body: [
        'Mudam’s entrance faces the Kirchberg plateau and its European institutions: the golden towers of the Court of Justice of the European Union and the European Investment Bank lie in this direction.',
        'The museum’s orientation links the fortress and the historic city with the European district: past, present and future.',
      ],
    },
  },
  {
    id: 'tram',
    at: [181, 2, -294],
    view: { target: [160, 0, -260], bearing: 40, tilt: 40, zoom: 0.65 },
    tr: {
      title: 'Tramvay: Philharmonie – Mudam',
      kicker: 'Ulaşım',
      body: [
        'Kirchberg’i kent merkezine bağlayan tramvay hattının “Philharmonie – Mudam” durağı Avenue John F. Kennedy üzerindedir.',
        'Duraktan Place de l’Europe ve park üzerinden müzeye birkaç dakikada yürünür.',
      ],
    },
    en: {
      title: 'Tram: Philharmonie – Mudam',
      kicker: 'Getting here',
      body: [
        'The “Philharmonie – Mudam” stop of the tram line linking Kirchberg with the city centre is on Avenue John F. Kennedy.',
        'From the stop it is a short walk across Place de l’Europe and the park to the museum.',
      ],
    },
  },
  {
    id: 'funicular',
    at: [-505, 2, -253],
    view: { target: [-430, 0, -215], bearing: 300, tilt: 40, zoom: 0.55 },
    tr: {
      title: 'Pfaffenthal–Kirchberg füniküleri',
      kicker: 'Vadiye iniş',
      body: [
        'Kirchberg platosunu Alzette vadisindeki Pfaffenthal tren durağına bağlayan füniküler 2017’de açıldı.',
        'Vadinin karşı yamacında, Pfaffenthal’i yukarı kente bağlayan panoramik asansör bulunur. Vadideki mahalleler platonun onlarca metre altındadır; işaretler yükseklik değil konum gösterir.',
      ],
    },
    en: {
      title: 'Pfaffenthal–Kirchberg funicular',
      kicker: 'Down to the valley',
      body: [
        'Opened in 2017, the funicular links the Kirchberg plateau with the Pfaffenthal rail stop in the Alzette valley.',
        'On the opposite slope a panoramic lift connects Pfaffenthal with the upper town. The valley quarters lie tens of metres below the plateau; pins mark position, not height.',
      ],
    },
  },
  {
    id: 'redbridge',
    at: [-595, 2, -127],
    view: { target: [-500, 0, -110], bearing: 290, tilt: 38, zoom: 0.55 },
    tr: {
      title: 'Kırmızı Köprü',
      kicker: 'Pont Grande-Duchesse Charlotte',
      body: [
        '1966’da açılan kırmızı çelik köprü, Pfaffenthal vadisinin üzerinden kent merkezini Kirchberg’e bağlar.',
        'Kirchberg’in Avrupa mahallesi olarak gelişmesinin simgelerinden biridir.',
      ],
    },
    en: {
      title: 'The Red Bridge',
      kicker: 'Pont Grande-Duchesse Charlotte',
      body: [
        'Opened in 1966, the red steel bridge spans the Pfaffenthal valley between the city centre and Kirchberg.',
        'It is one of the symbols of Kirchberg’s growth into the European district.',
      ],
    },
  },
  {
    id: 'oldtown',
    at: [-198, 2, 541],
    view: { target: [-175, 0, 450], bearing: 215, tilt: 36, zoom: 0.55 },
    tr: {
      title: 'Tarihî kent ve tahkimatlar',
      kicker: 'UNESCO Dünya Mirası',
      body: [
        'Mudam’ın camlı güneybatı cephesi, 1994’ten beri UNESCO Dünya Mirası listesinde olan “Lüksemburg Kenti: Eski Mahalleleri ve Tahkimatları”na bakar.',
        'Kentin kurulduğu Bock kayalığı bu manzaranın merkezindedir; Alzette vadisinin karşısındaki yukarı kent ile Mudam aynı tahkimat hikâyesinin iki ucudur.',
      ],
    },
    en: {
      title: 'Historic city and fortifications',
      kicker: 'UNESCO World Heritage',
      body: [
        'Mudam’s glazed south-west front looks toward “City of Luxembourg: its Old Quarters and Fortifications”, on the UNESCO World Heritage list since 1994.',
        'The Bock promontory, where the city began, is at the centre of that view; the upper town across the Alzette valley and Mudam are two ends of one fortress story.',
      ],
    },
  },
  {
    id: 'grunewald',
    at: [-184, 3, 159],
    view: { target: [-110, 0, 100], bearing: 230, tilt: 40, zoom: 0.7 },
    tr: {
      title: 'Grünewald cephesi tahkimatları',
      kicker: 'Kale kalıntıları',
      body: [
        'Parkın içindeki Fort Obergrünewald ve aşağıdaki Fort Niedergrünewald’ın kalıntıları, kentin doğusundaki savunma hattının parçalarıdır.',
        'Yerinde bilgi panolarıyla anlatılan bu kalıntılar, Thüngen Kalesi ve Mudam ile birlikte platonun üç yüzyıllık askerî mühendisliğini gösterir.',
      ],
    },
    en: {
      title: 'Grünewald front fortifications',
      kicker: 'Fortress remains',
      body: [
        'The remains of Fort Obergrünewald in the park and Fort Niedergrünewald below belong to the defensive line on the city’s eastern front.',
        'Explained on site by information panels, they show, together with Fort Thüngen and Mudam, three centuries of military engineering on the plateau.',
      ],
    },
  },
];
