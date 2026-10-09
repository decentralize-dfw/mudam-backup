from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R113_build_report.json').read_text())
checks=['R113_verification.json','R113_global_audit.json','R113_inherited_verification.json','R113_ground_routes.json','R113_service_routes.json']
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures'],name
d=json.loads((B/'reports/R113_inherited_verification.json').read_text());assert d['new_objects']==r['closed_objects'] and not d['changed_inherited_objects']
note='Zemin katın iki galerisinde servis alanına bakan eksik uzun duvarlar kaynak plan konturunda oluşturuldu. Önceki 360 eksik yüzey örneği kapandı. Galeri ve servis geçişleri, genel geometri ve sahne farkı kontrolleri geçti; iki aynı kamera önce/sonra görüntüsü incelendi.'
limits='Bütün bina ve kullanıcının tüm ekran görüntüleri henüz kabul edilmedi. Duvar kalınlığı mevcut kaynak konturları arasında uzlaştırılmış adaydır; kotlar ölçülmüş değildir. Öncelik kalan büyük kabuk sorunlarıdır.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R113'];a.append(dict(id='R113',checks=checks,tasks=['P05','P07','P16'],report='R113_KONTROL_RAPORU.md',title='Galeri–servis uzun duvarları / R113',image='R113_after_west_service.png',description=note,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R113',last_reviewed_checkpoint='R113',last_reviewed_revision='R113',last_review_note=note,review_note=note,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8');p.write_text(s.rstrip()+'\n\n## R113 — Galeri–servis uzun duvarları\n\nR113: '+note+'\n\n'+limits+'\n\n[Önce/sonra ve kapsam](reports/R113_KONTROL_RAPORU.md).\n',encoding='utf8')
