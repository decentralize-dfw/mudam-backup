"""Publish current local modeling review after saved-scene checks pass."""
from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
build=json.loads((B/'reports/P09_build_report.json').read_text());qa=json.loads((B/'reports/P09_verification.json').read_text());assert build['file']==qa['file']
latest=Path(build['file']).relative_to('12_Blender_Model').as_posix();filename=Path(latest).name
tasks_path=R/'11_Blender_Modelleme_Plani/is_paketleri.json';tasks=json.loads(tasks_path.read_text(encoding='utf8'))
updates={
 'P05':['Üçgen giriş saçağı ve ana örtü altı revize edildi. Yan salon uç birleşimleri, cephe açıklıkları, üst galeri ışıklık sayısı ve alt kabuk sürüyor.'],
 'P06':['087/119/116 için üç koşullu kamera. 116 karşı görünüşte kontrol RMS 10,05 px. İç kamera ve tam metrik doğrulama açık.'],
 'P07':['Giriş bölgesinde 67 kapalı hacimli pilot; duvar/döşeme/başlıklar ayrı. Bütün bina ve taşıyıcı/kaplama ayrımı tamamlanmadı.'],
 'P08':['Girişte 6 açıklık kimliği üretildi. Bütün katların kapı/pencere envanteri henüz tamamlanmadı.'],
 'P09':['Üst merdivenin yönü düzeltildi; 3 gözlenen başlangıç basamağı modellendi. Tam kol/rıht zinciri, sahanlıklar ve GH_DOWN geometrisi açık.']}
for t in tasks['tasks']:
 if t['id'] in updates:
  t['status']='in_progress';t['open_issues']=updates[t['id']];t['updated']='2026-10-08';t['dependency_mode']='regional_study_only_no_global_acceptance';t.setdefault('artifacts',[])
  for a in [build['file'],'12_Blender_Model/reports/P07_P09_URETIM_RAPORU.md']:
   if a not in t['artifacts']:t['artifacts'].append(a)
tasks['latest_scene']=build['file']
tasks['current_tasks']=[t['id'] for t in tasks['tasks'] if t['status']=='in_progress']
tasks_path.write_text(json.dumps(tasks,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
status='''# Mudam - üretim durumu

8 Ekim 2026. Blender 4.2 / metre / EPSG:32632 yerel koordinatlar.

## Güncel teslim

'''+f'[{filename}]({latest}) giriş, çatı ve merdiven çalışmalarını birlikte içerir. [Görsel inceleme](URETIM.html) · [Üretim raporu](reports/P07_P09_URETIM_RAPORU.md).\n'+'''
| Paket | Durum | Somut çıktı / açık konu |
| --- | --- | --- |
| P00-P01 | Tamam / eksikler belgeli | Kaynak manifesti, üst kat kanıtları |
| P02 | Sürüyor | Kesit tarihi ve izi açık |
| P03 | Tamam | Plan/OSM koordinat aktarımı; ölçme doğruluğu değildir |
| P04 | Sürüyor | Koşullu kat kotları; rıht zinciri açık |
| P05 | Sürüyor | Kabuk ve örtü etütleri; giriş saçağı ve alt cam örtü revize |
| P06 | Sürüyor | 087 / 119 / 116 koşullu kameraları; iç kamera açık |
| P07 | Bölgesel pilot | Girişte ayrı kapalı duvar/saçak/döşeme hacimleri |
| P08 | Bölgesel pilot | Girişte altı açıklık kimliği; cam/çerçeve ayrımı |
| P09 | Kısmi üretim | Üç geniş başlangıç basamağı ve düzeltilmiş üst merdiven yönü |
| P10-P22 | Başlamadı | Detay paketleri tamamlanmış sayılmıyor |

## Kontrol sonuçları

P07: 164 yeni mesh / 67 kapalı hacim kontrol edildi; sıfır alanlı yüz yok. Kapı geçişi üç yükseklikte açık. Üç kamera aktarımı 0,009 px altında. [P07 yeniden açma kontrolü](reports/P07_verification.json).

P09: üç başlangıç basamağı, kot katmanları, yukarı/aşağı yönlerinin ayrılması ve paketli fotoğraflar yeni Blender sürecinde denetlendi. [P09 yeniden açma kontrolü](reports/P09_verification.json).

Üst merdivenin eski P05 kılavuz yönü tersti; düzeltildi. 049/050 ile ilişkili aşağı merdiven ayrı tutuluyor. Ziyaretçi şemasının çizgi sayısı gerçek rıht sayısı sayılmadı.

## Ölçü durumu

Ana kabuk henüz bütün bina düzeyinde kabul edilmedi. OSM uyum RMS'si yaklaşık 1,02 m, iki bağımsız kontrol RMS'si 1,91 m; source-plan ölçeği bu sınırlarla kullanılıyor. Kat kotları, saçak, profil ve kalınlık parametreleri koşullu. Sahnedeki büyük bölüm `90_UNCERTAIN_OR_PROXY` altında; fiziksel imalat doğruluğu iddiası yok.

## Sıradaki üretim

Üst merdiven tam kol/rıht/sahanlık zinciri; ayrı alt merdiven; galeri duvar/açıklıkları; çatı panel ve taşıyıcıları. Her adımda ilgili plan, kesit/kot ve fotoğraf kimlikleri yeniden karşılaştırılır. Rutin üretim için kullanıcı onayı beklenmez.

Önceki P03/P04/P05/P06/P07 sahneleri `scenes` içinde sürümlü olarak korunur. `build_mudam.py` eski ve kullanılmaz. Yeni betikler mevcut sürümün üzerine yazmayı reddeder.
'''
(B/'URETIM_DURUMU.md').write_text(status,encoding='utf8')
def source(key):return '../'+next(p for p in (R/'05_Dis_Mekan').rglob(key+'_*') if p.is_file()).relative_to(R).as_posix()
def compare(key,caption):return f'''<section class="panel"><h2>{caption}</h2><div class="compare"><img src="{source(key)}" alt="Kaynak fotoğraf {key}"><img class="overlay" src="renders/qa/P07_{key}.png" alt="Aynı bakıştan model" style="opacity:.55"></div><div class="controls"><button data-opacity="0">Fotoğraf</button><label>Model görünürlüğü <input type="range" min="0" max="100" value="55" aria-label="Model görünürlüğü"></label><output>55%</output><button data-opacity="100">Model</button></div></section>'''
markup='''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mudam - üretim incelemesi</title>
<style>*{box-sizing:border-box}body{margin:0;background:#10191d;color:#e8eeee;font:16px/1.6 system-ui}main{max-width:1480px;margin:auto;padding:32px}h1{font-size:40px;margin:0}h2{font-size:23px;margin:0 0 14px}p{max-width:1050px;color:#bfd0d5}a{color:#8ddacb}nav{display:flex;gap:22px;flex-wrap:wrap;margin:22px 0 30px}.badge{color:#f9c46b;font-size:14px;letter-spacing:.06em}.panel,figure{margin:0 0 26px;padding:20px;background:#1a282e;border-radius:12px}img{display:block;width:100%;height:auto}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}figcaption{margin-top:12px;color:#bfd0d5}.note{padding:15px;border-left:3px solid #f9c46b;background:#1e2b30}.compare{position:relative;overflow:hidden}.compare .overlay{position:absolute;inset:0;pointer-events:none}.controls{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin-top:14px}.controls label{display:flex;align-items:center;gap:16px;flex:1}.controls input{flex:1;min-width:100px;accent-color:#8ddacb}button{border:1px solid #567179;background:#22373d;color:#e8eeee;padding:7px 16px;border-radius:6px;cursor:pointer}table{border-collapse:collapse;width:100%;font-size:15px}th,td{text-align:left;border-bottom:1px solid #3a5058;padding:10px}th{color:#8ddacb}summary{cursor:pointer;font-size:20px;margin-bottom:16px}.small{font-size:14px}@media(max-width:850px){main{padding:16px}.grid{grid-template-columns:1fr}h1{font-size:30px}.controls label{min-width:60%}}</style></head><body><main>
<span class="badge">P06 - P09 / BÖLGESEL ÜRETİM</span><h1>Mudam / model kontrolü</h1>
<p>Giriş saçağı ve cephe açıklıkları, alt cam örtü, küçük okuma feneri ve üst merdivenin üç başlangıç basamağı üretildi. Aşağıdaki kontroller aynı kamera bakışındaki model ile kaynak fotoğrafı karşılaştırır.</p>
'''+f'''<nav><a href="{latest}">Güncel Blender dosyası</a><a href="URETIM_DURUMU.md">İş durumu</a><a href="reports/P07_P09_URETIM_RAPORU.md">Üretim ve kontrol raporu</a><a href="../10_Olcekli_Plan_ve_Fotograf_Analizi/FOTOGRAF_ATLASI.html">Fotoğraf atlası</a></nav>
<p class="note">Bütün bina henüz doğrulanmış değil. Ölçüsü açık elemanlar çalışma parametresi olarak tutuluyor. Merdivenin tam kolu, birçok cephe açıklığı, arazi ve çatı taşıyıcıları henüz tamamlanmadı.</p>
'''+compare('116','Giriş tarafı / fotoğraf 116')+compare('087','Cam salonlar / fotoğraf 087')+'''
<div class="grid"><figure><img src="renders/qa/P07_entry_detail.png" alt="Girişte üç cephe yüzü ve açıklıklar"><figcaption>Giriş pilotu: 6 açıklık kimliği; ayrı taş gövdeler, camlar ve önizleme çerçeveleri. Döner kapı kanatları ve mekanizma henüz yok.</figcaption></figure><figure><img src="renders/qa/P09_podium.png" alt="Üst merdivenin üç başlangıç basamağı"><figcaption>Üst merdivenin üç başlangıç basamağı. Mavi çizgi düzeltilmiş yükselme kılavuzudur; basamak veya korkuluk değildir. Tam kol henüz üretilmedi.</figcaption></figure></div>
<section class="panel"><h2>Paket takibi</h2><table><thead><tr><th>Paket</th><th>Çıktı</th><th>Açık iş</th></tr></thead><tbody>
<tr><td>P06</td><td>3 koşullu dış kamera</td><td>İç kamera, lens/kırpma ve tam kabuk uyumu</td></tr><tr><td>P07</td><td>Girişte kapalı kabuk hacimleri</td><td>Bütün duvarlar, taşıyıcı/kaplama ayrımı</td></tr><tr><td>P08</td><td>6 giriş açıklığı</td><td>Diğer katlar ve döner kapı mekanizması</td></tr><tr><td>P09</td><td>3 basamak + yön düzeltmesi</td><td>Tam kol, rıht zinciri, sahanlık ve alt merdiven</td></tr></tbody></table></section>
<details class="panel"><summary>Kaynak ve ölçüm kontrolleri</summary><div class="grid"><figure><img src="renders/qa/P06_116_triangular_canopy.png" alt="116 nokta eşleştirmesi"><figcaption>116: 6 hesap noktası RMS 6,35 px; 4 hesap dışı nokta RMS 10,05 px.</figcaption></figure><figure><img src="renders/qa/P06_087_multiview.png" alt="087 nokta eşleştirmesi"><figcaption>087: çatı ve kanat uçları hesaba dahil. 4 hesap dışı omuz noktası RMS 6,65 px.</figcaption></figure><figure><img src="references/P09_podium_plan_check.png" alt="Plan üzerinde basamaklar ve yükselme yönü"><figcaption>PDF2016 konturları 102 üzerinde. Geniş kıvrımlı uç başlangıç; dar uç +1 bağlantısı. Şema çizgileri gerçek rıht sayısı değildir.</figcaption></figure><figure><img src="../04_Ic_Mekan/Merdivenler_ve_Dolasim/022_Merdiven_ve_katlar_arasi_dolasim_WikiArquitectura.jpg" alt="Üç geniş başlangıç basamağının kaynak fotoğrafı"><figcaption>022: üç basamak ve üst merdiven yönü için fotoğraf kontrolü.</figcaption></figure></div><p class="small"><a href="reports/P07_verification.json">Giriş mesh ve geçiş denetimi</a> · <a href="reports/P09_verification.json">Merdiven yeniden açma denetimi</a> · <a href="config/entry_openings.json">Açıklık listesi</a> · <a href="config/entry_package.json">Ölçü ve kaynak kayıtları</a></p></details>
<p class="small">8 Ekim 2026. Kamera izdüşümü ile yazılım aktarımı denetlenir; bu, ölçülmüş bina doğruluğu anlamına gelmez. Eski sürümler korunur.</p></main>
<script>document.querySelectorAll('.controls').forEach(c=>{const slider=c.querySelector('input'),overlay=c.parentElement.querySelector('.overlay'),out=c.querySelector('output');const update=v=>{slider.value=v;overlay.style.opacity=Number(v)/100;out.textContent=v+'%'};slider.addEventListener('input',()=>update(slider.value));c.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>update(b.dataset.opacity)));});</script></body></html>'''
(B/'URETIM.html').write_text(markup,encoding='utf8')
# No old builder gate is loosened; only current scoped work is recorded.
gate_path=B/'config/reference_gate.json';gate=json.loads(gate_path.read_text(encoding='utf8'));gate['current_regional_studies']=['P06','P07','P08','P09'];gate['global_shell_accepted']=False;gate['routine_user_approval_required']=False;gate_path.write_text(json.dumps(gate,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print('Published',latest)
