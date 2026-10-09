from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R107_build_report.json').read_text());checks=['R107_verification.json','R107_global_audit.json','R107_inherited_verification.json']
for name in checks:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'] and not q['failures'],name
delta=json.loads((B/'reports/R107_inherited_verification.json').read_text());assert delta['changed_inherited_objects']==['P17_READING_FLOOR'] and not delta['new_objects']
d='Okuma odasının eski döşeme kenarı mevcut PDF2016 duvar konturuyla uzlaştırıldı; duvar dibindeki açık şerit giderildi. Merkez boşluk ve üç geçit korundu. 1.313 döşeme/boşluk ve 36 geçiş kontrolü geçti; önce/sonra görüntüleri incelendi.'
limits='Bütün bina tamamlanmadı. Diğer küçük odaların üst örtüleri, kalan çelik/cam birleşimleri ve bina son kontrolü açık; kesin kot ve malzeme ölçüleri hâlâ aday.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R107'];a.append(dict(id='R107',checks=checks,tasks=['P05','P17'],report='R107_KONTROL_RAPORU.md',title='Okuma odası döşeme teması / R107',image='R107_after_reading_floor_edge.png',description=d,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R107',last_reviewed_checkpoint='R107',last_reviewed_revision='R107',last_review_note=d,review_note=d,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8')
if '## R107 —' not in s:p.write_text(s.rstrip()+'\n\n## R107 — Okuma odası döşeme teması\n\nR107: '+d+'\n\n[Önce/sonra ve kontrol raporu](reports/R107_KONTROL_RAPORU.md). '+limits+'\n',encoding='utf8')
