"""Register the checked R100 local repair; retain open architectural issues."""
from pathlib import Path
import json
B=Path(__file__).resolve().parents[1]
checks=['R100_verification.json','R100_global_audit.json','R100_inherited_verification.json','R100_R99_regression.json']
r=json.loads((B/'reports/R100_build_report.json').read_text())
for name in checks:
    q=json.loads((B/'reports'/name).read_text()); assert q['file']==r['file'] and not q['failures']
description='İki galeri tavanının dokuz plan noktası mevcut giriş duvarlarının iç yüzüne bağlandı. En büyük yerel uyumsuzluk 0,337 m idi; kontrol edilen 18 alt/üst köşe artık aynı sınırda. Batı galeri duvarı ve iki girişin geçiş kontrolleri yeniden geçti.'
limits='Bu yerel çizim uzlaştırması ölçülmüş imalat geometrisi değildir. Gerçek giriş boşlukları ve fotoğraf 026’daki yüksek merdiven yanı geçidi korunur. +1 Studio/servis/asansör çevresinin bütün kat ilişkileri ve diğer kabuk birleşimleri açık.'
p=B/'config/checkpoint_extensions.json';a=json.loads(p.read_text());a=[x for x in a if x['id']!='R100'];a.append(dict(id='R100',checks=checks,tasks=['P07','P16'],report='R100_KONTROL_RAPORU.md',title='Galeri tavan–duvar temasları / R100',image='R100_after_east_ceiling_corner.png',description=description,limits=limits));p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'config/production_progress.json';a=json.loads(p.read_text());a.update(as_of_revision='R100',last_reviewed_checkpoint='R100',last_reviewed_revision='R100',last_review_note=description,review_note=description,current_priority=limits);p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8')
if '## R100 —' not in s:p.write_text(s.rstrip()+'\n\n## R100 — Galeri tavan–duvar temasları\n\nR100: '+description+'\n\n[Önce/sonra ve kontrol raporu](reports/R100_KONTROL_RAPORU.md). '+limits+'\n',encoding='utf8')
