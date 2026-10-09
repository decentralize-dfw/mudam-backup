from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R104_build_report.json').read_text());checks=['R104_verification.json','R104_global_audit.json','R104_inherited_verification.json','R104_gallery_regression.json']
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures'],name
d='Alt batı galeri girişindeki kısa duvarın 5 cm geride kalan arka yüzü, komşu merdiven duvarıyla hizalandı. Ön yüz, giriş ucu ve kotlar korundu; alt galeri geçiş kontrolleri geçti.'
limits='Bütün bina kabulü yok. Diğer kabuk birleşimleri ve kat ilişkileri kaynaklarla karşılaştırılıyor; komşudan devralınan kalınlık ve kotlar ölçülmemiş adaylardır.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R104'];a.append(dict(id='R104',checks=checks,tasks=['P07','P16'],report='R104_KONTROL_RAPORU.md',title='Alt merdiven duvar devamı / R104',image='R104_after_lower_wall_join.png',description=d,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R104',last_reviewed_checkpoint='R104',last_reviewed_revision='R104',last_review_note=d,review_note=d,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8')
if '## R104 —' not in s:p.write_text(s.rstrip()+'\n\n## R104 — Alt merdiven duvar devamı\n\nR104: '+d+'\n\n[Önce/sonra ve kontrol raporu](reports/R104_KONTROL_RAPORU.md). '+limits+'\n',encoding='utf8')
