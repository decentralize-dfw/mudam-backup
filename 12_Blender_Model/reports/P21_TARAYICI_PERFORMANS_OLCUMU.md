# P21 — R144 tarayıcı performans ölçümü

Aynı R144 GLB, kamera ve 787 × 1008 CSS piksel görünümünde 2 saniye ısınma + 10 saniye örnekleme yapıldı. Yerel HTTP ve mevcut tarayıcı önbelleği kullanıldı.

| Görünüm | Kare/sn | p95 kare süresi | Örnek |
|---|---:|---:|---:|
| Çevre ve kenarlar açık | 10.47 | 139.3 ms | 104 |
| Çevre açık, kenarlar kapalı | 12.45 | 109.0 ms | 124 |

İlk yükleme 5.243 saniye; bunun 3.750 saniyesi sahne kurulumu ve ilk çizim çağrısıdır. GPU bitiş zamanını ölçmez. Yaklaşık 21310 çizim çağrısı tam görünümün ağır olduğunu gösterir. Akıcı çalışma veya tüm cihazlarda performans kabulü verilmedi.

Kaynak: P21_browser_performance_full.json ve P21_browser_performance_material.json; GLB SHA256 `3ab5a81fa72155501305887b940cb9fe448b462ba3a236a32f8516adcdc1476a`. Tarayıcı görünüm, çözünürlük ve kaynak bilgileri kayıtlardadır. Ölçüm sırasında görünüm kontrolleri kilitlenir; sekmenin gizlenmesi veya görünüm değişmesi ölçümü iptal eder. Kamera eski konumuna döner. İstatistik, iptal ve yetersiz örnek testleri geçti. Web aktarımı ve pano testleri geçti.

Bu çalışma yeni mimari geometri değildir. Genel ilerleme %74 olarak korundu; P21 hedef motor kabulü açık. Ara push yapılmadı.

Yeni GLB sürümü yüklenince ekrandaki eski ölçüm temizlenir; R144 ölçüm kayıtları tarihsel kanıt olarak saklanır. R145 malzeme yayınına R144 FPS sonucu atanmadı.
