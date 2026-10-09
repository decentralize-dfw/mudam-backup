const $ = id => document.getElementById(id);
const escape = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let cached = '', loading = false, showAll = false, entries = [];
function drawUpdates() {
  const visible = showAll ? entries : entries.slice(0, 6);
  $('updates').innerHTML = visible.map(entry => {
    const [stamp, ...parts] = entry.split(' — ');
    let date = stamp.replace(/T/, ' ').replace(/\.\d+\+00:00/, ' UTC');
    const parsed = new Date(stamp.includes('T') ? stamp : stamp.replace(' UTC','Z').replace(' ','T'));
    if (!Number.isNaN(parsed.getTime())) date = parsed.toLocaleString('tr-TR', {day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'});
    const text = parts.join(' — ').replace(/`/g,'');
    const sentence = text.split(/\. (?=[A-ZÇĞİÖŞÜ])/)[0];
    const short = sentence.length > 210 ? sentence.slice(0,207).replace(/\s+\S*$/, '') + '…' : sentence;
    return `<article><time>${escape(date)}</time><p>${escape(short || text)}</p></article>`;
  }).join('');
  $('more').hidden = entries.length <= 6;
  $('more').textContent = showAll ? 'Daha az göster' : `Tüm güncellemeleri göster (${entries.length})`;
}
function render(md, board, progress) {
  const revision = board.latest_scene?.match(/_R(\d+)_/)?.[1];
  $('revision').textContent = `Son doğrulanmış sahne: R${revision || '?'}`;
  $('latest-change').textContent = progress.last_review_note || progress.review_note || '';
  $('priority').textContent = progress.current_priority ? `Sıradaki öncelik: ${progress.current_priority}` : '';
  const opened = new Set([...$('tasks').querySelectorAll('details[open]')].map(e => e.dataset.task));
  const tasks = board.tasks.map(task => {
    const steps = progress.tasks[task.id]?.steps;
    if (!steps?.length || steps.some(s => ![0,.5,1].includes(s.completion))) throw new Error(`${task.id} ilerleme kaydı eksik`);
    return {...task, steps, percent:Math.round(steps.reduce((n,s) => n+s.completion,0)/steps.length*100)};
  });
  const average = Math.round(tasks.reduce((n,t) => n+t.percent,0)/tasks.length);
  $('overall').textContent = `%${average}`;
  $('overall-bar').setAttribute('aria-valuenow',average);
  $('overall-bar').querySelector('span').style.width = `${average}%`;
  $('summary').textContent = `${tasks.filter(t => t.percent===100).length} tamamlandı · ${tasks.filter(t => t.percent<100).length} sürüyor`;
  $('task-count').textContent = `${tasks.length} iş paketi`;
  $('tasks').innerHTML = tasks.map(task => {
    const pending = task.steps.filter(s => s.completion < 1);
    return `<details data-task="${escape(task.id)}" ${opened.has(task.id)?'open':''}><summary><span class="chevron" aria-hidden="true">›</span><span class="task-id">${escape(task.id)}</span><span class="task-title">${escape(task.title)}</span><span class="bar task-bar" aria-hidden="true"><span style="width:${task.percent}%"></span></span><span class="task-percent">%${task.percent}</span></summary><div class="task-body">${pending.length ? '<ul>'+pending.map(s => `<li class="${s.completion ? 'doing' : ''}"><span class="dot" aria-hidden="true">${s.completion ? '◐' : '○'}</span><span>${escape(s.label)}${s.completion ? ' <small>· sürüyor</small>' : ''}</span></li>`).join('')+'</ul>' : '<p class="complete">Bu paketin iş adımları tamamlandı.</p>'}<p><a href="URETIM_DURUMU.md">Teknik ayrıntılar ve açık konular · MD ↗</a></p></div></details>`;
  }).join('');
  entries = md.replace(/\r\n?/g,'\n').split(/\n\s*\n/).map(p => p.trim()).filter(p => /^(?:20\d{2}-\d{2}-\d{2}(?:T|\s)|R\d+\s*:)/.test(p)).map(p => p.replace(/^(R\d+)\s*:\s*/, '$1 — ')).reverse();
  drawUpdates();
}
async function read(path, json=false) {
  const url = new URL(path, location.href);url.searchParams.set('_status',Date.now());
  const response = await fetch(url,{cache:'no-store'});
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return json ? response.json() : response.text();
}
async function refresh() {
  if (loading) return; loading=true; $('refresh').disabled=true;
  try {
    const [md,board,progress] = await Promise.all([read('URETIM_DURUMU.md'),read('../11_Blender_Modelleme_Plani/is_paketleri.json',true),read('config/production_progress.json',true)]);
    const signature=JSON.stringify([md,board,progress]);
    if (signature!==cached) {render(md,board,progress);cached=signature;}
    $('sync').textContent = `Son kontrol ${new Date().toLocaleTimeString('tr-TR',{hour:'2-digit',minute:'2-digit',second:'2-digit'})} · 15 sn`;
    $('error').hidden=true;
  } catch(error) {
    $('sync').textContent='Kayıt okunamadı';$('error').textContent=`${cached ? 'Son okunan kayıt gösteriliyor. ' : ''}Güncelleme alınamadı: ${error.message}`;$('error').hidden=false;
  } finally {loading=false;$('refresh').disabled=false;}
}
$('refresh').addEventListener('click',refresh);
$('more').addEventListener('click',()=>{showAll=!showAll;drawUpdates();});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});
setInterval(()=>{if(!document.hidden)refresh();},15000);
refresh();
