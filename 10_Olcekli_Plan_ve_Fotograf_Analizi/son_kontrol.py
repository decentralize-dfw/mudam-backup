from pathlib import Path
import json
B=Path(__file__).resolve().parent
p=B/'FOTOGRAF_ATLASI.html';s=p.read_text(encoding='utf-8').replace('>N<br','>N (UTM)<br');p.write_text(s,encoding='utf-8')
p=B/'uret.py';s=p.read_text(encoding='utf-8').replace("'HEADER','9','$INSUNITS'","'HEADER','9','$ACADVER','1','AC1015','9','$INSUNITS'").replace('>N</text>','>N (UTM)</text>');p.write_text(s,encoding='utf-8')
for p in (B/'02_Harita').glob('*.svg'):
    s=p.read_text(encoding='utf-8').replace('>N</text>','>N (UTM)</text>');p.write_text(s,encoding='utf-8')
p=B/'02_Harita/OSM_bina_ve_kamera_tahminleri_metre.dxf';s=p.read_text().replace('HEADER\n9\n$INSUNITS','HEADER\n9\n$ACADVER\n1\nAC1015\n9\n$INSUNITS');p.write_text(s,encoding='ascii')
p=B.parent/'KATALOG.html';s=p.read_text(encoding='utf-8')
link='<p><a href="10_Olcekli_Plan_ve_Fotograf_Analizi/FOTOGRAF_ATLASI.html">Ölçekli plan ve fotoğraf konum atlasını aç</a></p>'
if link not in s:s=s.replace('</h1>','</h1>'+link,1);p.write_text(s,encoding='utf-8')
d=json.loads((B/'atlas_data.json').read_text(encoding='utf-8'))
assert len(d['photos'])==105
for p in d['photos']:
    assert (B.parent/p['path']).exists()
    assert (B/'05_Fotograf_Paftalari'/f'foto_{p["id"]}.svg').exists()
    if p['quality']=='unresolved':assert p['x_m'] is None and p['heading_deg'] is None
    if p['quality']=='region':assert p['heading_deg'] is None
assert (B/'KALIBRASYON_RAPORU.txt').exists()
print('105 fotoğraf: kaynak, pafta, koordinat/yön durumları ve rapor doğrulandı.')
