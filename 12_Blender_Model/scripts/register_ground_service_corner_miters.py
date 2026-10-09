from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R108_build_report.json').read_text())
checks=['R108_verification.json','R108_global_audit.json','R108_inherited_verification.json','R108_service_routes.json']
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures'],name
delta=json.loads((B/'reports/R108_inherited_verification.json').read_text());assert set(delta['changed_inherited_objects'])==set(r['changed_inherited_objects']) and not delta['new_objects'] and not delta['allowed_but_unchanged']
d='WC, vestiyer ve dükkânda 15 mevcut duvarın 11 ortak köşesi birleştirildi. Önceki 22 boşluk örneği kapandı; kaynak eksenleri, kalınlık, kotlar ve kapı uçları korundu. 44 köşe ve 96 servis geçiş/destek kontrolü geçti; yakın önce/sonra görüntüleri incelendi.'
limits='Bütün bina tamamlanmadı. Diğer kabuk birleşimleri, merdiven/kapı detayları ve bütünleşik kaynak kontrolü açık; ölçülmemiş kalınlık ve kotlar aday.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R108'];a.append(dict(id='R108',checks=checks,tasks=['P07','P16'],report='R108_KONTROL_RAPORU.md',title='Zemin servis duvar köşeleri / R108',image='R108_after_service_wall_corner.png',description=d,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R108',last_reviewed_checkpoint='R108',last_reviewed_revision='R108',last_review_note=d,review_note=d,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8')
if '## R108 —' not in s:p.write_text(s.rstrip()+'\n\n## R108 — Zemin servis duvar köşeleri\n\nR108: '+d+'\n\n[Önce/sonra ve kontrol raporu](reports/R108_KONTROL_RAPORU.md). '+limits+'\n',encoding='utf8')
