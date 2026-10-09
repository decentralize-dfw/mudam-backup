"""Record the checked R97 package without inventing progress completion."""
from pathlib import Path
import json
B=Path(__file__).resolve().parents[1]
checks=['R97_verification.json','R97_R96_regression.json','R97_global_audit.json','R97_inherited_verification.json']
r=json.loads((B/'reports/R97_build_report.json').read_text())
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures']
description='Servis merdivenine 24 basamak/sahanlık parçası eklendi; yolu kesen alt kat tavanı ve giriş duvarı yerel olarak açıldı. Yedi kuyu duvarı iki kat arasında devam ettirildi. 110 yerel kontrol ve önceki duvar/cam düzeltmelerinin gerileme kontrolü geçti.'
limits='Plan sembolündeki 24 bölme ölçülmüş rıht sayısı değildir. Dönüş yönü, rıht yüksekliği ve sahanlık aday; korkuluk ve alt kata devam ilişkisi açık. Bütün bina kabulü yapılmadı.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R97'];a.append(dict(id='R97',checks=checks,tasks=['P07','P09','P17'],report='R97_KONTROL_RAPORU.md',title='Servis merdiveni ve kat bağlantısı / R97',image='R97_after_service_top.png',description=description,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R97',last_reviewed_checkpoint='R97',last_reviewed_revision='R97',last_review_note=description,review_note=description,current_priority='Kabuk bağlantılarının bölgesel kontrolü; merdiven ve sahanlıkların plan/kesit ilişkisi. Sonra kapı/pencere ve korkuluklar.');p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8');block='\n\n## R97 — Servis merdiveni ve pano\n\nR97: '+description+'\n\n[Kontrol görselleri ve kaynak sınırları](reports/R97_KONTROL_RAPORU.md). '+limits+'\n\nR97: Üretim panosunda tarihsiz R-sürüm kayıtlarının görünmemesi düzeltildi. Son doğrulanmış sürüm, son değişiklik ve öncelik ayrı gösteriliyor. Son kontrol saati üretim güncellemesi diye etiketlenmiyor. Yüzdeler gerçek iş adımı kabulü olmadan artırılmadı.\n';
if '## R97 —' not in s:p.write_text(s.rstrip()+block,encoding='utf8')
