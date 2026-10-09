import * as THREE from 'three';
import {OrbitControls} from './vendor/three/OrbitControls.js';
import {GLTFLoader} from './vendor/three/GLTFLoader.js';
import {latestModelRelease,modelBytes} from './model-release.mjs';
import {LEVELS,clipEquations,retained,sourceIds} from './viewer-core.mjs';
const $=id=>document.getElementById(id), view=$('viewport'), status=$('status');
const scene=new THREE.Scene();scene.background=new THREE.Color('#e7e9e3');
const camera=new THREE.PerspectiveCamera(42,1,.05,3000);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.85;view.prepend(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=false;controls.minDistance=.15;controls.maxDistance=500;
scene.add(new THREE.HemisphereLight(0xffffff,0x787c68,1.4));const sun=new THREE.DirectionalLight(0xfff6e5,2);sun.position.set(-30,70,40);scene.add(sun);const fill=new THREE.DirectionalLight(0xe3edff,1);fill.position.set(50,20,-30);scene.add(fill);
let edgeLines=[];let model,meshes=[],selected,box,manifest=[],extensions=[],planes=[],mainBounds,report;
const metadataNode=o=>{let n=o;while(n&&!n.userData.element_id&&!n.userData.source_ids&&n.parent&&n.parent!==model)n=n.parent;return n;};
const isSite=o=>/^(R34_|R35_|R38_|P18_)/.test(metadataNode(o).name);
function draw(){renderer.render(scene,camera)}
new ResizeObserver(()=>{const w=view.clientWidth,h=view.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();draw()}).observe(view);controls.addEventListener('change',draw);
function fit(bounds,mode='iso'){const c=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3());const radius=Math.max(size.x,size.y,size.z,2)*.75/Math.tan(THREE.MathUtils.degToRad(camera.fov/2))/Math.min(camera.aspect,1);camera.up.set(0,1,0);const dir=mode==='top'?new THREE.Vector3(0,1,.00001):mode==='front'?new THREE.Vector3(0,.08,1):new THREE.Vector3(1,.8,1).normalize();camera.position.copy(c).addScaledVector(dir,radius);controls.target.copy(c);controls.update();document.body.dataset.camera=JSON.stringify({bounds:[bounds.min.toArray(),bounds.max.toArray()],target:controls.target.toArray(),camera:camera.position.toArray()});draw()}
function apply(){planes=clipEquations($('level').value,$('axis').value,+$('offset').value,$('reverse').checked);renderer.clippingPlanes=planes.map(p=>new THREE.Plane(new THREE.Vector3(...p.slice(0,3)),p[3]));for(const l of edgeLines)l.visible=$('edges').checked;for(const m of meshes)m.visible=($('site').checked||!isSite(m))&&(!$('isolate').checked||metadataNode(m)===selected);const band=LEVELS[$('level').value];$('band').textContent=band?`${band[0].toFixed(2)} ile ${band[1].toFixed(2)} m · koşullu model kotları`:'Kot aralığı uygulanmıyor.';if(box)box.visible=!!selected&&selected.visible;draw()}
function setAxis(){const axis=$('axis').value, b=mainBounds;const limits=axis==='H'?[-6,32]:axis==='E'?[b.min.x,b.max.x]:[-b.max.z,-b.min.z];$('offset').min=Math.floor(limits[0]);$('offset').max=Math.ceil(limits[1]);$('offset').value=axis==='H'?5:(limits[0]+limits[1])/2;$('cutValue').value=(+$('offset').value).toFixed(2);$('offset').disabled=$('cutValue').disabled=axis==='none';apply()}
function field(label,value){if(value===undefined)return;const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=String(value);$('metadata').append(dt,dd)}
function sourceLink(source,id){const a=document.createElement('a');a.className='source';a.target='_blank';a.rel='noopener';a.textContent=`${id} · ${source.credit||'Kaynak görsel'}`;a.href='../'+source.path.split('/').map(encodeURIComponent).join('/');return a}
function select(mesh){selected=mesh?metadataNode(mesh):null;if(box){scene.remove(box);box.geometry.dispose();box.material.dispose();box=null}$('metadata').replaceChildren();$('sources').replaceChildren();$('revisions').replaceChildren();$('focus').disabled=$('clear').disabled=$('isolate').disabled=!mesh;if(!mesh)$('isolate').checked=false;document.body.classList.toggle('has-selection',!!mesh);if(!mesh){$('selectedName').textContent='Henüz seçim yok';$('raw').textContent='';apply();return}const node=metadataNode(mesh),d=node.userData;$('selectedName').textContent=node.name;box=new THREE.BoxHelper(selected,0xd78d17);box.material.depthTest=false;box.renderOrder=100;scene.add(box);field('Tür',d.element_type);field('Bölge / kat etiketi',[d.zone_id,d.level_id].filter(Boolean).join(' / '));field('Durum',d.status);field('Yatay konum',d.confidence_xy);field('Düşey konum',d.confidence_z);field('Detay güveni',d.confidence_detail);field('Varsayım',d.assumption_note);field('Görünüm',d.surface_appearance_status);const bb=new THREE.Box3().setFromObject(selected);field('Model kot aralığı',`${bb.min.y.toFixed(3)} … ${bb.max.y.toFixed(3)} m (rölöve ölçüsü değil)`);const ids=sourceIds(d);if(!ids.length)field('Kaynak kaydı','Bu parçanın kaynak kimliği boş; paket raporunu inceleyin.');for(const id of ids){const s=manifest.find(s=>s.id===id);if(s)$('sources').append(sourceLink(s,id));else {const p=document.createElement('p');p.className='note';p.textContent=`${id} · doğrudan kaynak bağlantısı kayıtlı değil`;$('sources').append(p)}}const text=node.name+' '+JSON.stringify(d);for(const e of extensions.filter(e=>new RegExp('\\b'+e.id+'(?:_|\\b)').test(text))){const p=document.createElement('p'),a=document.createElement('a');a.href='reports/'+e.report;a.target='_blank';a.textContent=e.title;p.append(a,document.createElement('br'),document.createTextNode(e.limits));$('revisions').append(p)}$('raw').textContent=JSON.stringify(d,null,2);apply()}
function search(){const q=$('search').value.trim().toUpperCase();$('results').replaceChildren();if(q.length<2)return;const unique=new Map();for(const m of meshes){const n=metadataNode(m);if(n.name.toUpperCase().includes(q)&&!unique.has(n.name))unique.set(n.name,m)}for(const [name,m]of [...unique].slice(0,30)){const b=document.createElement('button');b.textContent=name;b.onclick=()=>select(m);$('results').append(b)}if(unique.size>30){const p=document.createElement('p');p.textContent=`${unique.size} sonuç; ilk 30 gösteriliyor.`;$('results').append(p)}}
const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();let down;
renderer.domElement.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY]});renderer.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5||e.button!==0)return;const r=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-r.left)/r.width*2-1,1-(e.clientY-r.top)/r.height*2);ray.setFromCamera(pointer,camera);const hits=ray.intersectObjects(meshes,false);const hit=hits.find(h=>{if(!h.object.visible||!retained(h.point,planes))return false;const mat=Array.isArray(h.object.material)?h.object.material[h.face.materialIndex]:h.object.material;return !($('skipGlass').checked&&(mat.transmission>.1||(mat.transparent&&mat.opacity<.6)||/GLASS|GLAZ/i.test(mat.name)))});select(hit?.object)});
$('edges').onchange=$('level').onchange=$('site').onchange=$('reverse').onchange=$('isolate').onchange=apply;$('axis').onchange=setAxis;$('offset').oninput=()=>{$('cutValue').value=(+$('offset').value).toFixed(2);apply()};$('cutValue').oninput=$('cutValue').onchange=()=>{if($('cutValue').value!==''&&Number.isFinite(+$('cutValue').value)){$('offset').value=$('cutValue').value;apply()}};$('search').oninput=search;$('iso').onclick=()=>fit(mainBounds);$('top').onclick=()=>fit(mainBounds,'top');$('front').onclick=()=>fit(mainBounds,'front');$('focus').onclick=()=>selected&&fit(new THREE.Box3().setFromObject(selected));$('clear').onclick=()=>select(null);
async function json(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error(`${url}: ${r.status}`);return r.json()}
let loading=false, releaseHash, downloadURL;
function disposeModel(root){
  const geometries=new Set(),materials=new Set(),textures=new Set();
  root.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of [o.material].flat().filter(Boolean)){materials.add(m);for(const value of Object.values(m))if(value?.isTexture)textures.add(value)}});
  for(const item of [...geometries,...materials,...textures])item.dispose();
}
async function refreshModel(){
  if(loading)return;loading=true;
  try{
    const release=await latestModelRelease();
    if(release.sha256===releaseHash)return;
    status.style.color='';status.textContent=`${release.revision} yükleniyor…`;
    const [bytes,sources,revisions]=await Promise.all([
      modelBytes(release,n=>{status.textContent=`${release.revision} yükleniyor · ${(n/1e6).toFixed(1)} / ${(release.download_bytes/1e6).toFixed(1)} MB`}),
      json('references/source_manifest.json'),json('config/checkpoint_extensions.json')]);
    const gltf=await new GLTFLoader().parseAsync(bytes,'');
    const previous=model,wasLoaded=!!model;
    if(previous){select(null);scene.remove(previous)}
    model=gltf.scene;meshes=[];edgeLines=[];manifest=sources;extensions=revisions;report=release;
    scene.add(model);model.updateMatrixWorld(true);mainBounds=new THREE.Box3();
    model.traverse(o=>{if(o.isMesh){meshes.push(o);if(!isSite(o))mainBounds.expandByObject(o)}});
    const edgeCache=new Map(),lineMaterial=new THREE.LineBasicMaterial({color:0x57665d,transparent:true,opacity:.3,depthWrite:false});
    for(const m of meshes){
      if(isSite(m)||/GLASS|GLAZ|PROFILE|FRAME|ROD|BAR|LAME|SEAT/i.test(m.name))continue;
      let geometry=edgeCache.get(m.geometry.uuid);
      if(!geometry){geometry=new THREE.EdgesGeometry(m.geometry,30);edgeCache.set(m.geometry.uuid,geometry)}
      const line=new THREE.LineSegments(geometry,lineMaterial);m.add(line);edgeLines.push(line);
    }
    if(previous)disposeModel(previous);
    if(downloadURL)URL.revokeObjectURL(downloadURL);
    downloadURL=URL.createObjectURL(new Blob([bytes],{type:'model/gltf-binary'}));
    $('blend').href=downloadURL;$('blend').textContent='GLB indir';$('blend').download=release.source_glb.split('/').pop();
    $('ready').textContent=release.source_scene.split('/').pop();
    status.textContent=`${release.revision} · ${release.selected_mesh_count.toLocaleString('tr')} model parçası · otomatik güncel`;
    apply();if(!wasLoaded)fit(mainBounds);
    document.body.dataset.loaded='true';document.body.dataset.meshes=meshes.length;document.body.dataset.sourceScene=release.source_scene;
    releaseHash=release.sha256;
  }catch(e){
    status.textContent=(model?'Mevcut model açık; güncelleme yeniden denenecek: ':'Model açılamadı: ')+e.message;
    status.style.color='#9a311b';console.error(e);
  }finally{loading=false}
}
await refreshModel();
setInterval(()=>{if(!document.hidden)refreshModel()},60000);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refreshModel()});
