from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R105_build_report.json').read_text());checks=['R105_verification.json','R105_global_audit.json','R105_inherited_verification.json','R105_gallery_regression.json']
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures'],name
delta=json.loads((B/'reports/R105_inherited_verification.json').read_text())
assert set(delta['changed_inherited_objects'])=={'P05_FLOOR_L00_W0','R28_W_FLAT_CEILING'} and not delta['new_objects'],'Geometry change must be demonstrated, not merely allowed.'
d='Batı zemin galerisinde mevcut duvar ile döşeme/tavan arasındaki yaklaşık 20 cm açıklık giderildi. Yalnız iki mevcut nesne genişletildi; 1.030 temas ve 108 giriş/güzergâh kontrolü geçti. Önce/sonra görüntüleri karşılaştırıldı.'
limits='Bütün bina tamamlanmadı. Diğer dar duvar–döşeme–tavan temasları kaynaklarla karşılaştırılıyor; mevcut kotlar ve kalınlıklar ölçülmemiş adaylardır.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R105'];a.append(dict(id='R105',checks=checks,tasks=['P05','P07','P16'],report='R105_KONTROL_RAPORU.md',title='Batı galeri döşeme/tavan teması / R105',image='R105_after_floor_contact.png',description=d,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R105',last_reviewed_checkpoint='R105',last_reviewed_revision='R105',last_review_note=d,review_note=d,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8')
if '## R105 —' not in s:p.write_text(s.rstrip()+'\n\n## R105 — Batı galeri döşeme/tavan teması\n\nR105: '+d+'\n\n[Önce/sonra ve kontrol raporu](reports/R105_KONTROL_RAPORU.md). '+limits+'\n',encoding='utf8')
