# P21 — Aynı veri bloklarının kayıpsız paylaşılması

R128 sahnesinin 8.477 model parçası korunarak GLB içindeki 2.664 yinelenen buffer veri bloğu ortak konuma bağlandı. Ham aktarım 91.415.240 bayttan 81.686.612 bayta, yayımlanan gzip 54.619.398 bayttan 52.537.621 bayta indi. Geometri sadeleştirilmedi; nesne adları, düğümler, dönüşümler, malzemeler, dokular ve öznitelikler aynı kaldı.

12.532 bufferView için kaynak ve sonuç baytları tek tek eşit doğrulandı. Belge yalnız bufferView.byteOffset ve buffers[0].byteLength alanlarında değişebilir; diğer alanların tamamı karşılaştırıldı. Mevcut glTF doğrulaması da geçti. Desteklenmeyen yeni buffer uzantıları sessizce dönüştürülmez; betik bunları reddeder.

Özgün GLB yerel arşivde korunur; kompakt GLB ayrı dosyadır. Bundan sonraki Blender aktarımlarında aynı işlem otomatik uygulanır. prepare_web_model.py doğrulanmış kompakt dosyayı yine bayt kaybı olmadan gzip yapar. Bu aktarım iyileştirmesidir; yeni mimari geometri veya tamamlanmış bina kabulü değildir. FPS ya da hedef motor kabulü ölçülmedi; genel oran değiştirilmedi.
