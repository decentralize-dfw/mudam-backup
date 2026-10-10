# Yakın çevre görünürlüğü

Yakın çevre anahtarı artık revizyon adından bağımsız bölge kimliğini kullanır. R130 ağaç taçları (14), R132 bitkili zemin (1), R56 diğer taçlar (24) ve R68 pavyon hendeği (7) çevreyle birlikte gizlenir. Eski ad önekleri uyumluluk için korunur. Güncel R136 GLB içindeki gerçek nesne metaverisinde bu 46 parça ve görünür kalması gereken 234 R10/R19 bina parçası sınandı. Kesit/kat/seçim birim kontrolleri geçti. Bu test GPU performansı veya bütün görüntüleyici kabulü değildir.

Doğrulama: scripts/verify_site_visibility.mjs ve reports/P20_site_visibility_verification.json. Ara push yapılmadı.
