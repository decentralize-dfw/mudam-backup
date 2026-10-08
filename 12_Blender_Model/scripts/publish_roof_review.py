"""Extend the production review only after the current P11 scene passed reload QA."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
def publish():
 r=json.loads((B/'reports/P11_build_report.json').read_text());q=json.loads((B/'reports/P11_verification.json').read_text());assert r['file']==q['file'];assert not q['failures']
 p=R/'11_Blender_Modelleme_Plani/is_paketleri.json';data=json.loads(p.read_text(encoding='utf8'))
 for t in data['tasks']:
  if t['id'] in ['P10','P11']:
   t['status']='in_progress';t['updated']='2026-10-08';t['dependency_mode']='regional_study_only_no_global_acceptance';t['artifacts']=[r['file'],'12_Blender_Model/reports/P10_P11_CATI_RAPORU.md']
   t['open_issues']=['Ana örtüde 359 ayrı panel; tüm profil ölçüleri ve bazı modül sayıları koşullu. İç gergi/gölgeleme ve birleşimler açık.'] if t['id']=='P10' else ['435 yan/alt örtü ve geçit paneli; opak alt kuşak düzeltildi. Batı camında ~20 mm düzlemsellik sapması, pavyon ve birleşimler açık.']
 data['latest_scene']=r['file'];data['current_tasks']=[t['id'] for t in data['tasks'] if t['status']=='in_progress'];p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 latest=Path(r['file']).relative_to('12_Blender_Model').as_posix();p=B/'URETIM.html';s=p.read_text(encoding='utf8')
 s=re.sub(r'href="scenes/[^\"]+\.blend"',f'href="{latest}"',s);s=s.replace('P06 - P09 / BÖLGESEL ÜRETİM','P06 - P11 / BÖLGESEL ÜRETİM');s=s.replace('renders/qa/P07_116.png','renders/qa/P11_116.png').replace('renders/qa/P07_087.png','renders/qa/P11_087.png')
 s=s.replace('Merdivenin tam kolu, birçok cephe açıklığı, arazi ve çatı taşıyıcıları henüz tamamlanmadı.','Merdivenin tam kolu, birçok cephe açıklığı ve arazi henüz tamamlanmadı. Çatı modül sayıları ve gergi ayrıntılarının bir bölümü koşullu.')
 block='''<section class="panel" id="roof-progress"><h2>Cam örtü üretimi / P10–P11</h2><p>Ana çatıda 359; yan ve alt örtüler ile geçitte 435 ayrı cam panel. Ayrı yüzey profilleri, doğuda temsilî gergi katmanı ve geçitte üst çaprazlar. Yan salonların alt kuşağı 093/034 kontrolüyle taş olarak düzeltildi.</p><p>3.203 kapalı hacim ve 380 çubuk ucu denetlendi. Batıdaki eğrisel camlarda yaklaşık 20 mm düzlemsellik sapması açık sorun olarak tutuluyor.</p><p><a href="reports/P10_P11_CATI_RAPORU.md">Çatı üretim raporu</a> · <a href="reports/P11_verification.json">Yeniden açma kontrolü</a></p><img src="renders/qa/P11_internal_east.png" alt="Doğu örtüsünün temsilî profil ve gergi katmanı"><p class="small">İç geometri kontrolü; fotoğraf eşlenmiş kamera değildir. Gergi ayrıntıları ve ölçüler koşullu.</p></section>'''
 s=re.sub(r'<section class="panel" id="roof-progress">.*?</section>','',s,flags=re.S);s=s.replace('<section class="panel"><h2>Paket takibi</h2>',block+'<section class="panel"><h2>Paket takibi</h2>');p.write_text(s,encoding='utf8')
 p=B/'URETIM_DURUMU.md';s=p.read_text(encoding='utf8');s=re.sub(r'\[MUDAM_[^\]]+\.blend\]\(scenes/[^)]+\)',f'[{Path(latest).name}]({latest})',s);s=s.replace('| P10-P22 | Başlamadı | Detay paketleri tamamlanmış sayılmıyor |','| P10-P11 | Bölgesel üretim | 794 ayrı cam panel, profiller, doğu gergi katmanı ve geçit; ayrıntılar koşullu |\n| P12-P22 | Başlamadı | Detay paketleri tamamlanmış sayılmıyor |')
 if 'P10_P11_CATI_RAPORU' not in s:s+='\n[Çatı üretim raporu](reports/P10_P11_CATI_RAPORU.md): 3.203 kapalı hacim ve 380 çubuk bağlantısı denetlendi. Pavyon/okuma feneri panelizasyonu, ana iç gergi/gölgeleme ve batı panel düzlemselliği açık.\n'
 p.write_text(s,encoding='utf8');print('Current verified release',r['file'])
if __name__=='__main__':publish()
