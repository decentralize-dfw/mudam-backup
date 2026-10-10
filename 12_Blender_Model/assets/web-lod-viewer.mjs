import * as THREE from 'three';
import {OrbitControls} from './vendor/three/OrbitControls.js';
import {GLTFLoader} from './vendor/three/GLTFLoader.js';
import {sampleRendering} from './performance-review.mjs';
const $=id=>document.getElementById(id),scene=new THREE.Scene();scene.background=new THREE.Color('#cad2d1');
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.85;document.body.prepend(renderer.domElement);
const camera=new THREE.PerspectiveCamera(42,1,.1,2500),controls=new OrbitControls(camera,renderer.domElement);controls.maxDistance=1500;controls.minDistance=2;
scene.add(new THREE.HemisphereLight(0xffffff,0x787c68,1.4));const sun=new THREE.DirectionalLight(0xfff6e5,2);sun.position.set(-30,70,40);scene.add(sun);const fill=new THREE.DirectionalLight(0xe3edff,1);fill.position.set(50,20,-30);scene.add(fill);
const draw=()=>renderer.render(scene,camera);const resize=()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);draw();};addEventListener('resize',resize);controls.addEventListener('change',draw);
function home(far=false){controls.target.set(0,0,-5);camera.position.set(...(far?[260,360,480]:[100,130,160]));controls.update();draw();}
$('close').onclick=()=>home();$('all').onclick=()=>home(true);resize();home();
const models=new Map(),pending=new Map(),loaded=[];let manifest;
async function load(key){
 if(models.has(key)){models.get(key).visible=$(key).checked;draw();return;}
 if(pending.has(key))return pending.get(key);
 const work=(async()=>{const row=manifest.layers.find(r=>r.key===key);$('status').textContent=`${key==='building'?'Mudam':'Çevre'} yükleniyor · ${(row.gzip_bytes/1e6).toFixed(1)} MB`;
 const res=await fetch(new URL(row.url,new URL('config/r151_web_lod.json',location.href)));if(!res.ok)throw Error('Katman dosyası yüklenemedi.');let bytes=await res.arrayBuffer();if(new Uint8Array(bytes)[0]===31)bytes=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
 const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');if(hash!==row.sha256)throw Error('Katman dosyası doğrulanamadı.');
 const gltf=await new GLTFLoader().parseAsync(bytes,'');models.set(key,gltf.scene);gltf.scene.visible=$(key).checked;scene.add(gltf.scene);loaded.push(key);$('status').textContent=`${loaded.length} katman hazır`;draw();$('measure').disabled=false;$('report').textContent=JSON.stringify({layers:manifest.layers.map(({key,triangles,draw_primitives_after,gzip_bytes})=>({key,triangles,draw_primitives_after,gzip_bytes})),loaded},null,2);
 })();pending.set(key,work);try{await work;}catch(e){$('status').textContent=e.message;throw e;}finally{pending.delete(key);}
}
for(const key of ['building','near_context','far_context'])$(key).onchange=()=>{$('fps').textContent='';if($(key).checked)load(key).catch(console.error);else if(models.has(key)){models.get(key).visible=false;draw();}};
$('measure').onclick=async()=>{const pos=camera.position.clone(),target=controls.target.clone();$('measure').disabled=true;$('fps').textContent='12 saniyelik ölçüm…';try{const result=await sampleRendering({render:()=>{draw();return {...renderer.info.render};},frame:t=>{const v=pos.clone().sub(target).applyAxisAngle(new THREE.Vector3(0,1,0),t*.35);camera.position.copy(target).add(v);camera.lookAt(target);},signature:()=>[...models].map(([k,m])=>k+':'+m.visible).join(','),hidden:()=>document.hidden});$('fps').textContent=`${result.delivered_fps.toFixed(1)} FPS · bu cihaz ve görünüm`;$('report').textContent=JSON.stringify(result,null,2);}catch(e){$('fps').textContent=e.message;}finally{camera.position.copy(pos);controls.target.copy(target);controls.update();draw();$('measure').disabled=false;}};
try{const response=await fetch('config/r151_web_lod.json',{cache:'no-store'});if(!response.ok)throw Error('Web modeli hazırlanıyor; aktarım henüz bitmedi.');manifest=await response.json();await load('building');await load('near_context');}catch(e){$('status').textContent=e.message;console.error(e);}
