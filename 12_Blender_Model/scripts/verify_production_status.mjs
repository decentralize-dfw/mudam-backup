import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
const root=new URL('../',import.meta.url), nodes=new Map();
function node(id){if(!nodes.has(id))nodes.set(id,{textContent:'',innerHTML:'',style:{},hidden:false,setAttribute(){},querySelector(){return node(id+'-span');},querySelectorAll(){return [];},addEventListener(){}});return nodes.get(id);}
let interval, fetchCount=0, extra='';
const context={URL,Date,console,location:{href:'http://localhost/12_Blender_Model/URETIM_DURUMU.html'},document:{hidden:false,getElementById:node,addEventListener(){}},setInterval(fn,ms){assert.equal(ms,15000);interval=fn;},fetch:async url=>{fetchCount++;assert.ok(url.searchParams.has('_status'));const path=url.pathname.replace('/12_Blender_Model/','');const text=await readFile(new URL(url.pathname.includes('/11_Blender_Modelleme_Plani/')?'../11_Blender_Modelleme_Plani/is_paketleri.json':path,root),'utf8');return {ok:true,text:async()=>text+extra,json:async()=>JSON.parse(text)};}};
vm.runInNewContext(await readFile(new URL('assets/production-status.mjs',root),'utf8'),context);
async function settled(){for(let i=0;i<100&&(!node('sync').textContent.startsWith('Son kontrol')||node('refresh').disabled);i++)await new Promise(r=>setTimeout(r,10));assert.equal(node('error').hidden,true);}
await settled();assert.match(node('revision').textContent,/R98/);assert.match(node('updates').innerHTML,/R98/);assert.match(node('updates').innerHTML,/R97/);assert.match(node('overall').textContent,/^%\d+/);const before=fetchCount;
extra='\n\nR999: AUTO_REFRESH_REGRESSION_PROBE\n';interval();await settled();assert.ok(fetchCount>before);assert.match(node('updates').innerHTML,/AUTO_REFRESH_REGRESSION_PROBE/);
console.log('Status: revision, undated checkpoint entries and 15-second automatic refresh passed; percentage '+node('overall').textContent);
