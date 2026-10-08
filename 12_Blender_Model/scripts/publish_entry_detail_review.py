"""Publish verified P12 as the current combined scene."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
def publish():
 r=json.loads((B/'reports/P12_build_report.json').read_text());q=json.loads((B/'reports/P12_verification.json').read_text());assert r['file']==q['file'] and not q['failures']
 p=R/'11_Blender_Modelleme_Plani/is_paketleri.json';data=json.loads(p.read_text(encoding='utf8'));data['latest_scene']=r['file']
 for t in data['tasks']:
  if t['id']=='P12':t.update(status='in_progress',updated='2026-10-08',dependency_mode='regional_study_only_no_global_acceptance',artifacts=[r['file'],'12_Blender_Model/reports/P12_GIRIS_DETAY_RAPORU.md'],open_issues=['Girişte cam kanatlar, çekme kolları, yuvarlak dikmeler ve bağlantı adayları. Mekanizma kesin değil; korkuluk ve galeri pencere örneği açık.'])
 data['current_tasks']=[t['id'] for t in data['tasks'] if t['status']=='in_progress'];p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 p=B/'config/entry_openings.json';openings=json.loads(p.read_text(encoding='utf8'))
 for o in openings:
  if o['id']=='ENT-02-L00':o['type']='glazed_vestibule_flat_leaf_candidate';o['mechanism_verified']=False;o['superseded_type']='revolving_door_with_fixed_surround';o['type_note']='013/014 yakın çekimlerinde iki sıra düz kanat görünür; döner mekanizma tanımı kesinleşmediği için geri çekildi. P12 üst kot düzeltmesi config/entry_door_detail.json içinde.'
 p.write_text(json.dumps(openings,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 latest=Path(r['file']).relative_to('12_Blender_Model').as_posix();p=B/'URETIM.html';s=p.read_text(encoding='utf8');s=re.sub(r'href="scenes/[^\"]+\.blend"',f'href="{latest}"',s);s=s.replace('P06 - P11 / BÖLGESEL ÜRETİM','P06 - P12 / BÖLGESEL ÜRETİM');s=s.replace('renders/qa/P07_entry_detail.png','renders/qa/P12_entry_detail.png');s=s.replace('Döner kapı kanatları ve mekanizma henüz yok.','Düz cam kanatlar ve ayrı donanım adayları eklendi; gerçek mekanizma kesinleşmedi.');s=s.replace('Diğer katlar ve döner kapı mekanizması','Diğer katlar ve giriş kapısının gerçek mekanizması')
 block='''<section class="panel" id="entry-detail-progress"><h2>Giriş yakın detayı / P12 pilotu</h2><p>013 yakın çekimindeki düz cam kanatlar, metal kenarlar, çekme kolları, yuvarlak dikmeler ve noktasal bağlantılar ayrı nesneler. Önceki döner kapı tanımı geri çekildi; iki pivotlu kanat yalnız düzenlenebilir mekanizma adayıdır.</p><p>008/013 kontrolüyle cam giriş kutusu üst kotu ana alt pencere başlığına yaklaştırıldı. 4,10 m kutu / 3,60 m kanat başlığı çalışma ölçüsüdür.</p><p><a href="reports/P12_GIRIS_DETAY_RAPORU.md">Giriş detay raporu</a> · <a href="reports/P12_verification.json">Geometri ve hareket kontrolü</a></p></section>'''
 s=re.sub(r'<section class="panel" id="entry-detail-progress">.*?</section>','',s,flags=re.S);s=s.replace('<section class="panel"><h2>Paket takibi</h2>',block+'<section class="panel"><h2>Paket takibi</h2>');p.write_text(s,encoding='utf8')
 p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8');s=re.sub(r'\[MUDAM_[^\]]+\.blend\]\(scenes/[^)]+\)',f'[{Path(latest).name}]({latest})',s);s=s.replace('| P12-P22 | Başlamadı | Detay paketleri tamamlanmış sayılmıyor |','| P12 | Giriş pilotu | Düz kanatlar, donanımlar, giriş kutusu oran düzeltmesi; mekanizma belirsiz |\n| P13-P22 | Başlamadı | Kalan detay paketleri |')
 if 'P12_GIRIS_DETAY_RAPORU' not in s:s+='\n[Giriş detay raporu](reports/P12_GIRIS_DETAY_RAPORU.md): kapı mekanizması kesinleşmedi; görünen düz cam kanatlar ve donanımlar ayrı üretildi. Rutin onay beklenmez.\n'
 p.write_text(s,encoding='utf8');print('Current verified release',r['file'])
if __name__=='__main__':publish()
