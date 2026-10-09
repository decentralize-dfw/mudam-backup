"""Publish completed roof QA renders without promoting a new geometry revision."""
from pathlib import Path
import json,re,html
B=Path(__file__).resolve().parents[1]
release=json.loads((B/'config/model_release.json').read_text());rev=release['revision']
receipt=json.loads((B/'reports'/f'{rev}_gallery_render_receipt.json').read_text())
assert receipt['file']==release['source_scene']
images=receipt['images'];assert len(images)==4
for row in images:assert (B/'renders/qa'/row['image']).is_file()
report=f'{rev}_YEREL_CATI_KONTROLU.md';assert (B/'reports'/report).is_file()
cards=''.join(f'<a href="renders/qa/{html.escape(row["image"])}"><img src="renders/qa/{html.escape(row["image"])}" alt="{html.escape(row["image"].removesuffix(".png"))}" loading="lazy"></a>' for row in images)
section=f'<section class="panel" id="current-roof-qa"><h2>{rev} · Üst galeri kabuk kontrolü</h2><p>9.558 çatı–duvar çevre örneği kapalı; 71 ışıklık kontrol doğrultusu açık. Dört güncel iç görünüş. Kesin çatı profili ve bütün bina kabulü açık; geometri sürümü değişmedi.</p><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px">{cards}</div><a href="reports/{report}">Kaynaklar, yöntem ve açık konular</a></section>'
p=B/'URETIM.html';s=p.read_text(encoding='utf8');s=re.sub(r'<section class="panel" id="current-roof-qa">.*?</section>','',s,flags=re.S)
anchor='<section class="panel"><h2>Paket takibi</h2>';assert anchor in s
p.write_text(s.replace(anchor,section+anchor,1),encoding='utf8');print('Published gallery roof QA',rev)
