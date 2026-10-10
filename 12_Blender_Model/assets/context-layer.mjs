// The detailed context is streamed on demand, independently of the building layer.
const host=document.querySelector('#viewport');
const section=document.createElement('section');
section.innerHTML='<h2>Dokulu çevre</h2><button id="contextView">Arazi ve çevreyi aç</button><p class="note">ACT 2020: gerçek cepheler, yollar ve ağaçlar. Bina ve çevre ayrı açılıp kapanır. Optimize GLB katmanları; uzak çevre isteğe bağlı yüklenir.</p>';
document.querySelector('main > aside').prepend(section);
const button=section.querySelector('button');let frame;
button.addEventListener('click',()=>{
 if(!frame){frame=document.createElement('iframe');frame.title='Mudam, arazi ve çevre katmanları';frame.src='WEB_HAFIF.html?v=clean2';frame.style.cssText='position:absolute;inset:0;width:100%;height:100%;border:0;z-index:4;background:#30383b';host.append(frame);}
 else frame.hidden=!frame.hidden;
 const active=!frame.hidden;button.textContent=active?'Bina incelemesine dön':'Arazi ve çevreyi aç';
 host.style.gridColumn=active?'2 / -1':'';document.querySelector('#inspector').hidden=active;
 for(const s of document.querySelectorAll('main > aside:first-child > section'))if(s!==section){s.inert=active;s.style.opacity=active?'.45':'';}
});
