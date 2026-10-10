# R118 — Köprü döşemesi ve galeri eşikleri

R117 bağlantıları eksik yan şeritleri kapatırken mevcut R23 eşiklerinin alanına da giriyordu. Bu iki döşemenin üst üste gelmesi giderildi. Doğuda 0,617614 m³, batıda 0,450508 m³ yinelenen hacim çıkarıldı; mevcut eşiklerin geometrisi ve bitmiş üst kotları değiştirilmedi.

Yalnız R117_E_BRIDGE_FLOOR_JOIN ve R117_W_BRIDGE_FLOOR_JOIN değişti. Yeni nesne eklenmedi. Kaynak, mevcut plan103 köprü/eşik geometrisidir; yeni boyut veya kaynak dışı bölme eklenmedi.

Yeniden açılan sahnede önce/sonra 78 konum örneği karşılaştırıldı: önce 62 konumda iki üst yüzey varken sonra bütün 78 konumda tek üst yüzey bulunuyor. Önceki boş yan şeritler kapalı kaldı. Genel mesh kontrolü ve miras nesne farkı kontrolü bulgusuz geçti. Aynı kameranın önce/sonra renderları açılarak zemin sürekliliği incelendi. Bu kapsam bina bütünü için kabul değildir.

Sahne: MUDAM_R118_KOPRU_ESIK_CAKISMA_v001.blend. Saatlik push sırası beklenir; son main yayını R117, 2026-10-09 23:46:28 UTC.
