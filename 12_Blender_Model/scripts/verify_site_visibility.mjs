import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {isSiteElement} from '../assets/viewer-core.mjs';
const root=new URL('../../',import.meta.url),base=new URL('../',import.meta.url);
const release=JSON.parse(await readFile(new URL('config/model_release.json',base)));
const bytes=await readFile(new URL(release.source_glb,root));
const gltf=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
const nodes=gltf.nodes.filter(n=>n.extras?.element_id||n.extras?.zone_id);
const groups={};
for(const prefix of ['R130_','R132_','R56_','R68_']) {
 const found=nodes.filter(n=>n.name.startsWith(prefix));assert(found.length,`${prefix} must exist in the actual release`);
 assert(found.every(n=>isSiteElement(n.name,n.extras)),`${prefix} must hide with its site`);groups[prefix]=found.length;
}
const building=nodes.filter(n=>n.name.startsWith('R10_')||n.name.startsWith('R19_'));
assert(building.length>50);assert(building.every(n=>!isSiteElement(n.name,n.extras)),'Building must stay visible');
const result={revision:release.revision,glb_sha256:release.sha256,site_groups:groups,building_nodes_checked:building.length,failures:[],scope:'Actual GLB semantic nodes tested; browser GPU rendering not measured.'};
await writeFile(new URL('reports/P20_site_visibility_verification.json',base),JSON.stringify(result,null,2)+'\n');
console.log(result);
