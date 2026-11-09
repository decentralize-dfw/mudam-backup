# R151 web optimizasyonu

Özgün `MUDAM_R151_ACT_CEVRE_ADAY_v011.blend` değiştirilmedi (1.894.316.996 bayt). Ayrı `MUDAM_R151_WEB_LOD_v002.blend`: 207.157.862 bayt.

- Temel mesh üçgenleri: 16.225.338 → 3.290.137 (%79,7 azalma). GLB modifier uygulanmış üçgenleri bu sayıdan farklıdır.
- Doku çözünürlüğü mesafeye göre 1024/512/256; mimari renk 1024, veri haritaları 512. Fotoğraf dokuları JPEG82; alpha/veri dokuları PNG. Görsel LOD kayıplıdır.
- 38 aşırı sadeleşen çevre parçasının özgün geometrisi geri alındı. Yeniden açma kontrolünde 8.429 değişmemiş mesh ve 79.518 yüzey örneği geçti. Örnekli test tam Hausdorff garantisi değildir.
- Statik materyal grupları birleştirildi; dokulu çevrenin siyah taban + emisyon malzemeleri unlit karşılığına dönüştürüldü. Kullanılmayan normaller çıkarıldı; aynı vertex kayıtları paylaşıldı. Çevre konumları 1 mm basamağına yuvarlandı. Mimari konumlara bu yuvarlama uygulanmadı.
- Bina, yakın çevre, uzak çevre bağımsız katmanlar. Uzak çevre talep üzerine indirilir.
- Üç GLB: sonlu accessor, indeks sınırları, üçgen sayıları, dokuların açılabilirliği ve kaynak export ile doku bayt eşitliği doğrulandı. Gzip SHA256 tarayıcıda kontrol edildi.
- Tarayıcıda bina/yakın çevre ve tüm çevre görünümü açıldı. Yakın görünüm ölçümü 49,7 FPS (10 saniye, bu bilgisayar/1280×720 görünüm); cihazlar geneline performans garantisi değildir.

| Katman | Aktarım MB | Üçgen |
|---|---:|---:|
| building | 14.63 | 905236 |
| near_context | 46.00 | 1049843 |
| far_context | 56.59 | 1548050 |

İlk aktarım 60,63 MB. Tam ZIP 117,05 MB. WEB_HAFIF.html HTTP üzerinden açılır. Kaynak ACT Luxembourg mesh3D2020, CC0.

Bu kabul web optimizasyonuyla sınırlıdır. R151 mimari yerleşim belirsizlikleri sürer; üretim ana modeli R149 ve genel ilerleme yaklaşık %74 olarak korunur.

Tüm katmanlar açık genel görünüm: 35,2 FPS; ölçüm reports/R151_WEB_LOD_browser_all.json içinde. Yakın ve uzak katmanların görünürlük anahtarları çalıştı. ZIP bütünlük testi geçti.
