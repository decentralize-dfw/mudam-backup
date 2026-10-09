from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];checks=['R102_verification.json','R102_global_audit.json','R102_inherited_verification.json','R102_service_stair_regression.json'];r=json.loads((B/'reports/R102_build_report.json').read_text())
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures']
d='Üst servis odası ve merdiven kuyusunda 14 duvarın 12 dış köşesi birleştirildi. Önceden açık olan 10 köşe probu kapandı; iç plan çizgileri ve açıklıklar korundu. Servis merdiveninin 110 kontrolü yeniden geçti.'
limits='Bütün bina kabulü yok. Diğer üst kat duvar/örtü birleşimleri ve katlar arası devamlılık kontrolü sürüyor; ölçülmemiş kalınlık ve kotlar aday.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R102'];a.append(dict(id='R102',checks=checks,tasks=['P07','P17'],report='R102_KONTROL_RAPORU.md',title='Üst servis duvar köşeleri / R102',image='R102_after_service_wall_corners.png',description=d,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R102',last_reviewed_checkpoint='R102',last_reviewed_revision='R102',last_review_note=d,review_note=d,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8')
if '## R102 —' not in s:p.write_text(s.rstrip()+'\n\n## R102 — Üst servis duvar köşeleri\n\nR102: '+d+'\n\n[Kontrol ve önce/sonra görselleri](reports/R102_KONTROL_RAPORU.md). '+limits+'\n',encoding='utf8')
