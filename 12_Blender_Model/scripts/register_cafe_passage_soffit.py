from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R111_build_report.json').read_text())
checks=['R111_verification.json','R111_global_audit.json','R111_inherited_verification.json','R111_ground_routes.json']
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures'],name
d=json.loads((B/'reports/R111_inherited_verification.json').read_text());assert d['new_objects']==r['closed_objects'] and not d['changed_inherited_objects']
note='Kafe–batı galeri geçidinde eksik üst örtü oluşturuldu. Aynı kamera karşılaştırmasında yatay yarık kapandı; zemindeki açık geçit korunuyor. Yeniden açılan sahnede önceki 132 örtüsüz örnek kapandı; genel geometri ve galeri geçiş kontrolleri geçti.'
limits='Öncelik büyük kabuk sorunları. Doğu merdiveni–duvar birleşimi ve kalan büyük açıklıklar bitmeden köşe veya malzeme detayına geçilmez. Örtü kotu mevcut 4,35 m galeri tavanı adayıdır; ölçülmüş uygulama detayı değildir.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R111'];a.append(dict(id='R111',checks=checks,tasks=['P05','P07','P16'],report='R111_KONTROL_RAPORU.md',title='Kafe geçidi eksik üst örtüsü / R111',image='R111_marked_cafe_ground.png',description=note,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R111',last_reviewed_checkpoint='R111',last_reviewed_revision='R111',last_review_note=note,review_note=note,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8');p.write_text(s.rstrip()+'\n\n## R111 — Kafe geçidinin büyük üst örtü açıklığı\n\nR111: '+note+'\n\n'+limits+'\n\n[Önce/sonra ve kapsam](reports/R111_KONTROL_RAPORU.md).\n',encoding='utf8')
