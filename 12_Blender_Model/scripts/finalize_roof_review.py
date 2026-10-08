"""Refresh P06 review artifacts without changing source photographs or geometry."""
from pathlib import Path
import json
from PIL import Image
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
bg=Image.open(next((R/'05_Dis_Mekan').rglob('119_*'))).convert('RGBA')
fg=Image.open(B/'renders/qa/P06_119_roof_transparent.png').convert('RGBA')
fg.putalpha(fg.getchannel('A').point(lambda a:int(a*.48)))
Image.alpha_composite(bg,fg).convert('RGB').save(B/'renders/qa/P06_119_overlay.png')
path=R/'11_Blender_Modelleme_Plani/is_paketleri.json';data=json.loads(path.read_text(encoding='utf8'))
for t in data['tasks']:
 if t['id']=='P06':
  t['status']='in_progress';t['updated']='2026-10-08';t['execution_scope']='Conditional P05 diagnostic; dependent detailing acceptance remains open.'
  t['open_issues']=['119 kamera koşullu; dört omuz kontrolünde RMS 6,03 px, iki yan kanat ucunda yaklaşık 55/88 px uyumsuzluk.','116/087 bağımsız kamera eşleştirmesi yapılmadı; kesit tarihi/izi ve alt çatı yüzeyleri açık.']
  t['artifacts']=['12_Blender_Model/scenes/MUDAM_P06_CATI_KONTROL_v002.blend','12_Blender_Model/reports/P06_CAMERA_ROOF_REVIEW.md','12_Blender_Model/reports/P06_camera_fit_119.json','12_Blender_Model/reports/P06_verification.json']
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
path=B/'URETIM_DURUMU.md';txt=path.read_text(encoding='utf8')
if '## P06 güncellemesi' not in txt:
 txt+='\n## P06 güncellemesi\n\nGüncel çalışma [P06 çatı kontrolü v002](scenes/MUDAM_P06_CATI_KONTROL_v002.blend). Ana örtünün iki kotlu yüzey düzeni düzeltildi, fotoğraf 119 için koşullu kamera eklendi. [Karşılaştırma raporu](reports/P06_CAMERA_ROOF_REVIEW.md). 27 yeni mesh ve 32 birleşim köşesi kaydedilmiş dosyada denetlendi.\n\nKabuk kabul edilmedi: ana çatı omuz kontrolü iyileşirken yan kanat uçları yaklaşık 55/88 piksel sapıyor. Sonraki iş 116/087 ile kamera–kanat–alt örtü ilişkisini çözmek. P07 ve sonraki detay paketleri başlamadı.\n'
txt=txt.replace('| P06–P22 | Başlamadı | Ana plandaki sırayla devam edecek; hiçbir detay paketi tamamlanmış sayılmadı |','| P06 Kamera/kabuk kontrolü | Sürüyor | 119 kamera ve çatı revizyonu; yan kanat kontrolü başarısız, bağımsız fotoğraf eşleştirmesi açık |\n| P07–P22 | Başlamadı | Detay paketleri için bölgesel kabuk kabulü bekleniyor |')
path.write_text(txt,encoding='utf8')
path=B/'URETIM.html';txt=path.read_text(encoding='utf8')
txt=txt.replace('P05 · KABUK ETÜDÜ · v002','P06 · ÇATI / FOTOĞRAF KONTROLÜ · v002')
txt=txt.replace('scenes/MUDAM_P05_KABUK_v002.blend','scenes/MUDAM_P06_CATI_KONTROL_v002.blend').replace('reports/P05_KABUK_KONTROLU.md','reports/P06_CAMERA_ROOF_REVIEW.md')
txt=txt.replace('Ana kabuk, kat bölgeleri, merdiven boşluğu, cam örtüler ve pavyon bağlantısı. Görseller şematik modelin inceleme kameralarıdır; fotoğrafla kalibre edilmiş bakışlar değildir.','Ana örtüdeki iki saçak seviyesi ayrıldı; fotoğraf 119 ile koşullu kamera kontrolü kuruldu. Kabuk kabulü açık: yan kanat uçları aynı kamerada uyuşmuyor. Kapı, çelik profil ve diğer detaylara henüz geçilmedi.')
txt=txt.replace('renders/qa/P05_01_entry.png','renders/qa/P06_01_entry.png').replace('renders/qa/P05_02_glazed.png','renders/qa/P06_02_glazed.png')
if 'id="p06-check"' not in txt:
 block='''<section id="p06-check"><h2>Fotoğrafla karşılaştırma</h2>
<p>Model saydam olarak kaynak fotoğrafın üzerine bindirildi. Yalnız ana örtü gösteriliyor; alt kabuk ve kanatlar bu örtüşmeyle doğrulanmış sayılmıyor.</p>
<figure><img src="renders/qa/P06_119_overlay.png" alt="119 fotoğrafı üzerinde Blender çatı örtüşmesi"><figcaption>119 / koşullu kamera. Fotoğrafın özgün dosyası korunuyor.</figcaption></figure>
<figure><img src="renders/qa/P06_119_cross_system.png" alt="Ana çatı ve yan kanat uçlarının hata kontrolü"><figcaption>Çemberler fotoğraf seçimleri, kırmızı çaprazlar model izdüşümleri. Çatıdaki 4 hesap dışı omuz noktası RMS: 6,03 px. Yan kanat uçları: yaklaşık 55 / 88 px — açık uyuşmazlık.</figcaption></figure>
<details><summary>Plan, kesit ve karşı yöndeki fotoğraf kontrolü</summary><div class="grid">
<figure><img src="renders/qa/P06_plan_check.png" alt="102 üzerinde ana çatı aday izi"><figcaption>102 / kırmızı ana örtü, mavi fener adayı. Çatı izdüşümü için ölçülü pafta değildir.</figcaption></figure>
<figure><img src="references/section101_grid.png" alt="101 kesiti"><figcaption>101 / iki saçak ve omuz seviyesi. Kesit izi/tarihi henüz çözülmedi.</figcaption></figure>
<figure><img src="references/P06_116_roof_grid.png" alt="116 karşı yönden çatı detayı"><figcaption>116 / yüksek taraftaki örtü ve cam şerit. İkinci kamera hesabı henüz yapılmadı.</figcaption></figure>
<figure><img src="renders/qa/P06_119_legacy_landmarks.png" alt="Önceki tek seviyeli çatı kontrolü"><figcaption>Önceki aday / omuz noktaları RMS 39,22 px. Eski kamera çözümü arama sınırına dayanıyor.</figcaption></figure>
</div></details></section>'''
 txt=txt.replace('</nav>','</nav>'+block)
txt=txt.replace('Plan sınırları ve çatı açıklıkları.','P05 arşiv üst görünüşü: plan sınırları ve çatı açıklıkları; P06 çatı revizyonunu içermez.')
path.write_text(txt,encoding='utf8')
print('P06 review and task status updated')
