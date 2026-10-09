from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R103_build_report.json').read_text());checks=['R103_verification.json','R103_global_audit.json','R103_inherited_verification.json','R103_gallery_regression.json','R103_enclosure_verification.json']
q=json.loads((B/'reports/KABUK_SIK_TARAMA.json').read_text());assert q['file']==r['file'];rows=[x for x in q['summaries'] if 'WEST_UPPER' in x['region']];assert len(rows)==3
fail=[x for x in rows if x['floor_missing'] or x['cover_missing'] or x['side_escape_samples']];(B/'reports/R103_enclosure_verification.json').write_text(json.dumps(dict(file=r['file'],regions=rows,failures=fail,construction_acceptance=False),indent=2))
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures'],name
d='Batı üst galeriye taşan dört duvar/tavan parçası mevcut plan sınırına kırpıldı. Servis odası birleşimindeki çıkıntı ve merdiven dönüşündeki yanlış tavan uzantısı kaldırıldı. Kapı ve koridor geçişleri korundu.'
limits='Bütün bina kabulü yok. Diğer kabuk birleşimleri ve kat ilişkileri kaynaklarla karşılaştırılmaya devam ediyor; ölçülmemiş kotlar ve kalınlıklar aday.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R103'];a.append(dict(id='R103',checks=checks,tasks=['P07','P17'],report='R103_KONTROL_RAPORU.md',title='Üst galeri iç yüz birleşimleri / R103',image='R103_after_gallery_stair_portal.png',description=d,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R103',last_reviewed_checkpoint='R103',last_reviewed_revision='R103',last_review_note=d,review_note=d,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8')
if '## R103 —' not in s:p.write_text(s.rstrip()+'\n\n## R103 — Üst galeri iç yüz birleşimleri\n\nR103: '+d+'\n\n[Önce/sonra ve kontrol raporu](reports/R103_KONTROL_RAPORU.md). '+limits+'\n',encoding='utf8')
