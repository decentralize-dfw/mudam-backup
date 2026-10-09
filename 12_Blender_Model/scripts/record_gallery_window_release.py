"""Record manually reviewed R52 v009, checking all numerical receipts first."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
build=read(B/'reports/R52_build_report.json');assert build['file'].endswith('_v009.blend')
checks=['R52_verification.json','R52_inherited_verification.json','R52_global_audit.json','R28_regression_on_R52.json','R33_regression_on_R52.json']
for name in checks:
 q=read(B/'reports'/name);assert q['file']==build['file'] and not q['failures'],name
sources=[s for s in read(B/'references/source_manifest.json') if s['id'] in ['004','061','062','102','116','PDF2016']]
assert len(sources)==6
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256'],s['id']
limits=['PDF2016 page5 room boundary sets candidate glazing planes; second width transferred from first, not measured.','061/062 exact camera and window identities unresolved; topology and wood/white gallery family only.','R27 facade opening spacing and splay remain conditional. R52 coordinates aperture volumes without changing source floor or cloakroom.','Frame, glass, reveal thicknesses and sill/head elevations are inherited visualization candidates.','A01 plan boundary discrepancy coordinated, source uncertainty remains open; not construction acceptance.']
write(B/'reports/R52_source_receipt.json',dict(sources=sources,limits=limits))
write(B/'reports/R52_visual_review.json',dict(file=build['file'],reviewed_images=['R52_inside_bay2.png','R52_inside_bay4.png','R52_two_windows.png','R52_photo116.png'],scope='conditional room-boundary coordination; not exact camera/metric acceptance',rejected_trials={'v001':'opaque R33 wall across glazing','v002':'missing interior wall sections','v003-v004':'full-height return boxes and pier cut produced projections','v005-v006':'inherited pier still obscured glazing','v007':'intermediate aperture adjustment, not released','v008':'threshold extended beyond recessed lower wall'},limits=limits,failures=[],construction_acceptance=False))
ext=read(B/'config/checkpoint_extensions.json');assert not any(e['id']=='R52' for e in ext)
ext.append(dict(id='R52',checks=checks+['R52_visual_review.json'],tasks=['P08','P12','P14'],report='R52_KONTROL_RAPORU.md',title='Galeri camı–plan sınırı koordinasyonu / R52',image='R52_inside_bay2.png',description='İki cam düzlemi plan sınırına taşındı; 22 parça, galeri duvarı boşluğu ve taş ayak birleşimi işlendi. Döşeme ve vestiyer korundu; yeniden açma ve dolaşım kontrolleri geçti.',limits='İkinci pencere genişliği, kaynak kamera eşlemesi, niş ölçüleri ve montaj detayları koşullu. Önceki sekiz deneme ana sürüme alınmadı.'))
write(B/'config/checkpoint_extensions.json',ext)
issues=read(B/'reports/architectural_open_issues.json');a=next(q for q in issues if q['id']=='A01');a.update(status='plan_boundary_coordinated_candidate_R52',detail='R52v009 moves both glazing backplanes to PDF2016 room steps; original floor and cloakroom unchanged. R33 aperture and R27 pier interference coordinated. Second window width transferred from first; exact061/062 camera identity and facade/reveal dimensions unresolved. Not metric or construction acceptance.');a['evidence']+=['R52_KONTROL_RAPORU.md','R52_verification.json','R52_visual_review.json'];write(B/'reports/architectural_open_issues.json',issues)
now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
with (B/'URETIM_DURUMU.md').open('a',encoding='utf8') as f:f.write(f'\n\n{now} — R52 v009: iki galeri camı plan sınırına bağlandı; 22 yeni kapalı parça, oda duvarı boşluğu ve taş ayak birleşimi koordine edildi. 7.072 görünür mesh; kapalı hacim, dolaşım ve önceki geometri kontrolleri geçti. İkinci genişlik ve kaynak kamera kimlikleri koşullu; A01 kısmen koordine edildi. Üretim sürüyor.\n')
print('R52 release receipts recorded')
