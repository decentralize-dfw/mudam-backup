from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R112_build_report.json').read_text())
checks=['R112_verification.json','R112_global_audit.json','R112_inherited_verification.json','R112_ground_routes.json']
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures'],name
d=json.loads((B/'reports/R112_inherited_verification.json').read_text());assert d['new_objects']==r['closed_objects'] and not d['changed_inherited_objects']
note='Doğu galeri girişinin eksik üst örtüsü oluşturuldu. Önceki 81 örtüsüz örnek kapandı; geçitler ve yüksek atrium açıklığı korundu. Aynı kamera görsel karşılaştırması, sahne farkı, geometri ve geçiş kontrolleri geçti; altı merdiven ailesi taramasında yeni baş mesafesi engeli bulunmadı.'
limits='Öncelik büyük kabuk sorunları. Kalan büyük duvar/zemin/çatı açıklıkları bitmeden köşe veya malzeme detayına geçilmez. Örtü kotu mevcut 4,35 m galeri tavanı adayıdır; ölçülmüş uygulama detayı değildir.'
stair=json.loads((B/'reports/R112_stair_width_clearance.json').read_text());assert stair['file']==r['file'] and not stair['findings']
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R112'];a.append(dict(id='R112',checks=checks,tasks=['P05','P07','P16'],report='R112_KONTROL_RAPORU.md',title='Doğu galeri geçidi üst örtüsü / R112',image='R112_marked_east_ground.png',description=note,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R112',last_reviewed_checkpoint='R112',last_reviewed_revision='R112',last_review_note=note,review_note=note,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8');p.write_text(s.rstrip()+'\n\n## R112 — Doğu galeri giriş üst örtüsü\n\nR112: '+note+'\n\n'+limits+'\n\n[Önce/sonra ve kapsam](reports/R112_KONTROL_RAPORU.md).\n',encoding='utf8')
