from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];checks=['R101_verification.json','R101_global_audit.json','R101_inherited_verification.json'];r=json.loads((B/'reports/R101_build_report.json').read_text())
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures']
d='Okuma odası–doğu servis odası bağlantısının planda çizili fakat eksik bırakılmış iki yan duvarı eklendi. 15 eksik duvar probu düzeldi; dokuz geçiş ve sekiz zemin/tavan kontrolü geçti. Diğer mevcut geometri değişmedi.'
limits='+1 Studio, asansör ve diğer katlar arası kabuk ilişkileri hâlâ inceleniyor. Geçit duvarının yüksekliği ve kalınlığı aday; bütün bina kabulü yok.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R101'];a.append(dict(id='R101',checks=checks,tasks=['P07','P17'],report='R101_KONTROL_RAPORU.md',title='Okuma odası yan geçidi / R101',image='R101_after_east_reading_link.png',description=d,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R101',last_reviewed_checkpoint='R101',last_reviewed_revision='R101',last_review_note=d,review_note=d,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8')
if '## R101 —' not in s:p.write_text(s.rstrip()+'\n\n## R101 — Okuma odası yan geçidi\n\nR101: '+d+'\n\n[Kontrol ve önce/sonra görselleri](reports/R101_KONTROL_RAPORU.md). '+limits+'\n',encoding='utf8')
