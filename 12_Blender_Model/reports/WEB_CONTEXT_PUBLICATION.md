# Güncel GLB çevre yayını

Kullanıcının güncel görünümü main üzerinde görme isteğiyle, üç aktif GLB katmanı exports/web_current altında yayımlanır. Sürümlü GLB ve Blender arşivleri yerelde kalır. Her dosyanın gzip açılım SHA256 değeri config/r151_web_lod.json ile doğrulandı.

Eski Cesium sayfası güncel GLB görünümüne yönlendirilir. Bina, temizlenmiş yakın çevre ve isteğe bağlı uzak çevre bağımsız katmanlardır. Ana ayrıntılı bina inceleme modeli R149 olarak korunur; bu çevre görünümü R151 çalışma sahnesinden türetilmiştir ve bütün mimarinin nihai kabulü değildir.

Yakın çevrede 7704 üçgen kesimden etkilenmiş, sınır bölmeleri sonrasında net4140 üçgen azalmıştır. Bina geometrisi ve doku baytları korunmuştur. GLB sınır/indeks/doku kontrolleri ve tarayıcı yüklemesi geçti. Bina izdüşümünün2mm iç sınırında çevre yüzeyi kalmadı. Yüksek cephe kalıntıları için1m yerel çalışma bandı kullanıldı. Pavyon kaynak köşe RMSsapması0.647m olarak sürer.
