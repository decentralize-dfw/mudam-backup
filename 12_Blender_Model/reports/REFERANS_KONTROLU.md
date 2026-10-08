# Merdiven referansı düzeltmesi

8 Ekim 2026. Kullanıcının işaretlediği planla karşılaştırmada iki ana merdivenin önceki konum eşleştirmesinin karıştığı doğrulandı. Kuzey yukarı haritada soldaki yarım daire 0 → −1, sağdaki geniş merdiven 0 → +1 bağlantısıdır. Bunlar özgün plan görüntüsünde farklı yönlerde görünür; harita dönüşümü dikkate alınmalıdır.

049 ve 050 aşağı iniş merdivenidir. 046–048 aynı boşluğun düz/eğrisel cam korkuluk detaylarıdır. 051–053 ile 115 bunun alt görünüşleri; 054 ise iniş boşluğundan karşıdaki yukarı çıkışa bakış için çapraz kontroldür. 045'in baktığı boşluk da düzeltildi. Atlas, CSV/JSON/GeoJSON ve ilgili 11 fotoğraf paftası güncellendi.

Merdiven kimlikleri `config/stair_systems.json` içinde kayıtlıdır. Tam çekim noktaları ve yönler yeniden tahmin edildi; ölçülmüş kabul edilmez. 054'ün ara basamak kotu açık kalır. Diğer fotoğrafların önceki koordinatları da otomatik olarak doğrulanmış model girdisi sayılamaz.

Model oluşturma betiğinin ilk denemesi geometri aşamasında hata verdi ve `.blend` dosyası üretmedi. Fotoğraf düzeltmesi sırasında geometri üretimi durduruldu. Betik ve referans hazırlığı mevcut; model henüz teslim edilmiş veya tamamlanmış değildir. Tekrar üretimden önce bütün kritik dolaşım, açıklık ve çatı referansları gözden geçirilecektir.

Arayüz düzeltmesi: seçili fotoğrafın çemberi, yön fanı ve etiketleri artık tıklama yakalamıyor. Çok yakın veya üst üste binen noktalar için fotoğraf seçim listesi eklendi. Tarayıcıda 049 seçiliyken çember içindeki 050 noktasına tıklanıp listeden 050 açılarak kontrol edildi.


## 105 fotoğrafın tam denetimi

105/105 fotoğraf tek tek incelendi. 42 kayıtta atama/açıklama değişti. Güncel ayrım: 35 konum/yön hipotezi, 45 aday bölge, 25 harita noktası olmayan fotoğraf. Doğrulanmış kamera pozu yok.

055 de aşağı iniş sistemindedir; 019'un merdiven kimliği desteklenmediği için kaldırıldı. 043 üst spiral sahanlığıdır; 042/044/050/054/066 için kesin döşeme kotu atanmadı. 066 ve 097 basamaklı cam merdiven adayıdır, 067 düz pavyon geçididir ve bakış yönü pavyona doğrudur. Diğer bulgular ve 105 ayrı gözlem [tam denetim raporundadır](../../10_Olcekli_Plan_ve_Fotograf_Analizi/06_Tek_Tek_Denetim/FOTOGRAF_DENETIMI.md).

`config/reference_gate.json` üretim geometrisini devre dışı tutar. Görsel denetim tamamlandı; taslak betikteki yükseklikler, çizgi kalınlığından türetilen duvarlar ve açıklıklar doğrulanmış değildir. Sonraki modelleme çalışmasında bu varsayımlar düzeltilmeden üretim açılmamalıdır. Bu denetimde yeni geometri veya .blend üretilmedi.
