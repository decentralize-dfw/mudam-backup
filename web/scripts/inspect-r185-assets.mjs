import fs from 'node:fs';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule()});
const manifest=JSON.parse(fs.readFileSync('demo/data/cevre3.json'));
for(const [key,row] of Object.entries(manifest.files)){
 const d=await io.read('demo/'+row.file);console.log(key,d.getRoot().listNodes().map(n=>n.getName()).filter(n=>/R161_ROAD|R168_SOURCE_JUNCTION|R177_ROAD/.test(n)));
}
const d=await io.read('12_Blender_Model/exports/r152_clean/r185_road9_REVIEW.glb');console.log('replacement',d.getRoot().listNodes().map(n=>n.getName()));
