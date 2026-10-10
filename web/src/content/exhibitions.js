// Mudam's programme on 10 October 2026, from mudam.com and the exhibition
// announcements (e-flux, Visit Luxembourg). Titles, dates, curators, places
// and the descriptions are the museum's; the per-room readings below are a
// demo proposal for how a room-by-room visit could be told, NOT the
// exhibitions' official sections. Every image on the walls is a placeholder.
export const EXHIBITIONS = [
  {
    id: 'kaiho',
    colour: 0xc8432b,
    css: '#c8432b',
    floors: ['L00', 'LP1'],
    start: 'L00',
    title: 'Kaihō',
    subtitle: { tr: 'Japanese Women Artists after 1945', en: 'Japanese Women Artists after 1945' },
    dates: { tr: '25.09.2026 – 14.02.2027', en: '25.09.2026 – 14.02.2027' },
    place: { tr: 'Zemin kat ve üst kat galerileri', en: 'Ground and upper-floor galleries' },
    credits: {
      tr: 'Küratör: Florence Ostende; asistanlar: Anaël Daoud, Yurika Imaseki. Lenbachhaus (Münih) ve Guggenheim Museum Bilbao ile birlikte.',
      en: 'Curator: Florence Ostende, assisted by Anaël Daoud and Yurika Imaseki. Organised with the Lenbachhaus, Munich, and the Guggenheim Museum Bilbao.',
    },
    intro: {
      tr: [
        'Savaş sonrası Japon kadın sanatçılara ayrılmış ilk kapsamlı Avrupa sergisi. Otuzu aşkın sanatçının 120’yi aşkın eseri tematik bölümler hâlinde bir araya geliyor; Atsuko Tanaka, Yayoi Kusama, Yoko Ono, Fujiko Nakaya, Tomie Ohtake ve Ruth Asawa öne çıkan isimler arasında.',
        'Sergi, Japonya’da kalanlar kadar ülkeyi göçmen olarak terk eden ya da hiç orada yaşamamış sanatçıları da kapsar. Mudam’dan sonra Münih ve Bilbao’ya gidecek.',
      ],
      en: [
        'The first European survey of Japanese women artists after 1945. More than 120 works by over thirty artists are brought together in thematic sections; featured names include Atsuko Tanaka, Yayoi Kusama, Yoko Ono, Fujiko Nakaya, Tomie Ohtake and Ruth Asawa.',
        'It includes artists who stayed in Japan as well as those who left as migrants or never lived there. After Mudam it travels to Munich and Bilbao.',
      ],
    },
    rooms: [
      { id: 'galerie-est-0', tr: { title: 'Eylem ve malzeme', text: 'Savaş sonrası avangardın bedenle, jestle ve malzemeyle kurduğu ilişkiye odaklanan bir okuma. Gutai çevresinin eylem resmi ve elektrikli devre çizimleri bu odanın referans noktaları olarak düşünülebilir.' }, en: { title: 'Action and material', text: 'A reading centred on the post-war avant-garde’s engagement with body, gesture and material. The action painting and electric-circuit drawings of the Gutai circle are its points of reference.' } },
      { id: 'grand-hall', tr: { title: 'Eşik', text: 'Kanopinin altında, ışığın ve havanın kendisinin malzemeye dönüştüğü büyük ölçekli yerleştirmeler için önerilen alan. Ziyaretçi sergiye buradan, mekânın bütününü kapsayan işlerle girer.' }, en: { title: 'Threshold', text: 'Under the canopy, a space proposed for large installations where light and air become material. Visitors enter the exhibition here, through works that take in the whole space.' } },
      { id: 'galerie-ouest-0', tr: { title: 'Talimatlar ve partisyonlar', text: 'Fluxus ve kavramsal pratiklerin talimat parçaları, partisyonları ve eylem önerileri. Eser burada bir nesneden çok, izleyicinin tamamlayacağı bir yönerge olarak düşünülür.' }, en: { title: 'Instructions and scores', text: 'Instruction pieces, scores and propositions from Fluxus and conceptual practice. Here the work is less an object than a direction for the viewer to complete.' } },
      { id: 'jardin-sculptures', tr: { title: 'Hava, ışık, çevre', text: 'Parka açılan cam salonda çevre bilincini ve doğayla kurulan ilişkiyi işleyen heykel ve yerleştirmeler. Gün boyunca değişen ışık işlerin bir parçası olur.' }, en: { title: 'Air, light, environment', text: 'In the glazed hall that opens to the park, sculptures and installations on environmental awareness and our relationship with nature. Changing daylight becomes part of the works.' } },
      { id: 'galerie-est-1', tr: { title: 'Renk ve ritim', text: 'Soyutlamanın farklı coğrafyalarda aldığı biçimler: büyük renk alanları, eğriler ve ritmik yüzeyler. Tepe ışığı altında renk, galerinin mimarisiyle birlikte okunur.' }, en: { title: 'Colour and rhythm', text: 'The forms abstraction took across geographies: large fields of colour, curves and rhythmic surfaces. Under the top light, colour reads together with the gallery’s architecture.' } },
      { id: 'galerie-ouest-1', tr: { title: 'Göç ve ağlar', text: 'Japonya’dan ayrılan ya da hiç orada yaşamamış sanatçıların New York’tan São Paulo’ya, Kaliforniya’dan Avrupa’ya uzanan ağları. Örgü, tel ve ağ biçimleri bu odanın görsel dilini kurar.' }, en: { title: 'Migration and networks', text: 'The networks of artists who left Japan or never lived there, from New York to São Paulo, California to Europe. Knotted, woven and wire forms set the room’s visual language.' } },
      { id: 'petite-galerie-ouest', tr: { title: 'Pedagoji ve arşiv', text: 'Feminist yayınlar, öğretim pratikleri ve belgeler için küçük bir oda. Sergi kataloğunun izlediği temalar (feminizm, pedagoji, çevre bilinci) burada belgeler üzerinden okunur.' }, en: { title: 'Pedagogy and archive', text: 'A small room for feminist publications, teaching practices and documents. Themes traced by the catalogue (feminism, pedagogy, environmental awareness) are read here through documents.' } },
    ],
  },
  {
    id: 'forever',
    colour: 0xb8862b,
    css: '#b8862b',
    floors: ['L00'],
    start: 'L00',
    title: 'Christine Sun Kim',
    subtitle: { tr: 'FOR EVER', en: 'FOR EVER' },
    dates: { tr: '25.09.2026 – 10.01.2027', en: '25.09.2026 – 10.01.2027' },
    place: { tr: 'Henry J. ve Erna D. Leir Pavyonu', en: 'Henry J. and Erna D. Leir Pavilion' },
    credits: {
      tr: 'Mudam için üretilmiş mekâna özgü komisyon. Ses tasarımı: müzisyen Matt Karmil ile birlikte.',
      en: 'A site-specific commission for Mudam. Soundscape made with musician Matt Karmil.',
    },
    intro: {
      tr: [
        'Christine Sun Kim pavyonda “sonsuza dek” kavramı üzerine düşünen bir anıt kuruyor: Sağır kültürünün sürekliliğine ve direncine adanmış bir yapıt. Dört duvardaki heykelsi tuvaller “forever” sözcüğünü Amerikan İşaret Dili’nde (ASL) gösterir.',
        'Sergi, sanatçının isteğiyle tamamen pavyonun zemin katında; alt kat basamaksız erişime sahip olmadığı için kullanılmıyor.',
      ],
      en: [
        'In the pavilion Christine Sun Kim builds a monument reflecting on the idea of “forever”, dedicated to the longevity and resilience of Deaf culture. Sculptural canvases on four walls depict the word “forever” in American Sign Language (ASL).',
        'At the artist’s request the show is presented entirely on the pavilion’s ground floor, because the lower level has no step-free access.',
      ],
    },
    rooms: [
      { id: 'pavillon', tr: { title: 'Dört duvar', text: 'Sekizgen pavyonun dört duvarında dört heykelsi tuval. Tuvaller pavyonun simetrisine yerleşir; ses manzarası mekânı bir bütün olarak doldurur.' }, en: { title: 'Four walls', text: 'Four sculptural canvases on four walls of the octagonal pavilion. They follow its symmetry while the soundscape fills the space as a whole.' } },
      { id: 'pavillon-m1', closed: true, tr: { title: 'Alt kat (kullanılmıyor)', text: 'Pavyonun alt katı bu sergide kullanılmıyor: sanatçı, alt kata basamaksız erişim olmadığı için sergiyi tamamen zemin katta kurmayı tercih etti.' }, en: { title: 'Lower level (not in use)', text: 'The pavilion’s lower level is not used for this show: the artist chose to present it entirely on the ground floor, as the lower level has no step-free access.' } },
    ],
  },
  {
    id: 'vktrs',
    colour: 0x2f5d9b,
    css: '#2f5d9b',
    floors: ['LM1'],
    start: 'LM1',
    title: 'Video Killed the Radio Star',
    subtitle: { tr: 'The 1980s and their Cultural Echoes', en: 'The 1980s and their Cultural Echoes' },
    dates: { tr: '12.06 – 11.10.2026 · son günler', en: '12.06 – 11.10.2026 · closing' },
    place: { tr: 'Alt kat galerileri (−1)', en: 'Lower-level galleries (−1)' },
    credits: {
      tr: 'Küratör: Bettina Steinbrügge; Caroline Honorien ve Alexine Taddeï ile. Mudam Koleksiyonu’ndan eserler ve yeni ödünçler.',
      en: 'Curator: Bettina Steinbrügge, with Caroline Honorien and Alexine Taddeï. Works from the Mudam Collection and new loans.',
    },
    next: { tr: 'Sıradaki: Ana Vaz, A câmera é o corpo · 13.11.2026’dan itibaren', en: 'Next: Ana Vaz, A câmera é o corpo · from 13.11.2026' },
    intro: {
      tr: [
        'Mudam’ın 20. yılında bir koleksiyon sunumu: 1970’lerin sonundan 1990’ların başına uzanan “uzun 1980’ler”e geri dönüş. Kırk iki sanatçının yaklaşık elli eseri, büyük bölümü Mudam Koleksiyonu’ndan.',
        'Sergi iki bölümden oluşur: ilki, evrensel ve Batı merkezli bakışı sorgulayan savaş sonrası kuşakların 1980’lerin başındaki estetik devrimleri; ikincisi, on yılın toplumsal ve siyasal bağlamı, bugün hâlâ yankılanan kırılmaları ve süreklilikleri.',
      ],
      en: [
        'A collection presentation for Mudam’s twentieth year, revisiting the “long 1980s” from the late 1970s to the early 1990s: about fifty works by forty-two artists, many from the Mudam Collection.',
        'It unfolds in two parts: the aesthetic revolutions of the early 1980s, driven by post-war generations questioning universal and Western-centric perspectives; and the decade’s social and political context, its ruptures and continuities that still resonate.',
      ],
    },
    rooms: [
      { id: 'galerie-est-m1', tr: { title: 'Bölüm I · Estetik devrimler', text: 'Resme dönüş, yeni dışavurumculuk ve imgenin yeniden sahiplenilmesi: 1980’lerin başında evrensel ve Batı merkezli bakışı sorgulayan kuşakların biçim dili.' }, en: { title: 'Part I · Aesthetic revolutions', text: 'The return to painting, new expressionism and the reclaiming of the image: the visual language of generations questioning universal, Western-centric perspectives in the early 1980s.' } },
      { id: 'foyer', tr: { title: 'Ekran ve yayın', text: 'Serginin adı, 1979’da yayımlanan ve MTV’nin 1981’deki açılışında ilk gösterilen klip olan şarkıdan gelir. Bu oda video, televizyon ve yayın kültürünün sanata girişine odaklanan bir geçiş olarak önerilir.' }, en: { title: 'Screen and broadcast', text: 'The title comes from the 1979 song whose video was the first shown when MTV launched in 1981. This room is proposed as a passage on video, television and broadcast culture entering art.' } },
      { id: 'galerie-ouest-m1', tr: { title: 'Bölüm II · Kırılmalar ve süreklilikler', text: 'On yılın toplumsal ve siyasal bağlamı: el koyma, imge politikası ve bugün hâlâ yankılanan kırılmalar ile süreklilikler.' }, en: { title: 'Part II · Ruptures and continuities', text: 'The decade’s social and political context: appropriation, the politics of the image, and ruptures and continuities that still resonate today.' } },
    ],
  },
];

// Spaces that are not exhibition rooms, described when clicked in plan or section.
export const OTHER_ROOMS = {
  cafe: { tr: { title: 'Mudam Café', text: 'Batı cam salonundaki kafe-restoran; sergi alanı değildir. Chiche! tarafından işletilir: ev yapımı yemek, göçmen ve mültecilerin istihdam ve entegrasyonunu destekleyen bir girişim.' }, en: { title: 'Mudam Café', text: 'Café-restaurant in the west glazed hall; not an exhibition space. Run by Chiche!, home-made food supporting employment and integration for migrants and refugees.' } },
  entree: { tr: { title: 'Giriş', text: 'Okun ucundaki giriş: karşılama, bilet, vestiyer, mağaza ve tuvaletler.' }, en: { title: 'Entrance', text: 'The entrance at the tip of the arrow: welcome desk, tickets, cloakroom, shop and toilets.' } },
  passage: { tr: { title: 'Camlı geçit', text: 'Jardin des Sculptures’ü kale kalıntılarının üzerinden pavyona bağlayan geçit.' }, en: { title: 'Glazed passage', text: 'The passage linking the Jardin des Sculptures with the pavilion over the fortress remains.' } },
  studio: { tr: { title: 'Studio', text: 'Atölye ve eğitim programları için ayrılmış oda.' }, en: { title: 'Studio', text: 'The room for workshops and learning programmes.' } },
  documentation: { tr: { title: 'Espace de documentation', text: 'Okuma ve belge alanı; ortadaki ışıklı boşluk üst kattan aşağıya görüş açar.' }, en: { title: 'Espace de documentation', text: 'Reading and documentation space; the lit void at its centre opens a view down through the floor.' } },
  pont: { tr: { title: 'Passerelle', text: 'Üst kattaki iki galeriyi birbirine bağlayan köprü.' }, en: { title: 'Passerelle', text: 'The bridge connecting the two upper galleries.' } },
  auditorium: { tr: { title: 'Auditorium', text: 'Alt kattaki oditoryum: konuşmalar, gösterimler ve performanslar için.' }, en: { title: 'Auditorium', text: 'The lower-level auditorium, for talks, screenings and performances.' } },
};
