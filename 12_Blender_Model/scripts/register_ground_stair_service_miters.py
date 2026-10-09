from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R109_build_report.json').read_text())
checks=['R109_verification.json','R109_global_audit.json','R109_inherited_verification.json','R109_service_stair_regression.json']
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures'],name
delta=json.loads((B/'reports/R109_inherited_verification.json').read_text());assert set(delta['changed_inherited_objects'])==set(r['changed_inherited_objects']) and not delta['new_objects'] and not delta['allowed_but_unchanged']
d='Servis merdiveni altındaki üç mevcut duvarın iki köşesi birleştirildi. Önceki dört boşluk örneği kapandı; mevcut kapı kesisi ve merdiven korundu. Sekiz köşe örneği, genel geometri ve merdiven geçiş kontrolleri geçti; önce/sonra görüntüleri incelendi.'
limits='Bütün bina tamamlanmadı. Diğer kabuk birleşimleri, merdiven/kapı detayları ve bütünleşik kaynak kontrolü açık; ölçülmemiş kalınlık ve kotlar aday.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R109'];a.append(dict(id='R109',checks=checks,tasks=['P07','P16'],report='R109_KONTROL_RAPORU.md',title='Servis merdiveni altı duvar köşeleri / R109',image='R109_after_service_stair_wall_corner.png',description=d,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R109',last_reviewed_checkpoint='R109',last_reviewed_revision='R109',last_review_note=d,review_note=d,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8')
if '## R109 —' not in s:p.write_text(s.rstrip()+'\n\n## R109 — Servis merdiveni altı duvar köşeleri\n\nR109: '+d+'\n\n[Önce/sonra ve kontrol raporu](reports/R109_KONTROL_RAPORU.md). '+limits+'\n',encoding='utf8')
