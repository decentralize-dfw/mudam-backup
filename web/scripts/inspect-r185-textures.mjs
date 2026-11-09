import fs from 'node:fs';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule()});
for(const path of ['demo/model/cevre3/authored-district.glb','12_Blender_Model/exports/r152_clean/r185_r188_district_draco_webp_REVIEW.glb']){const d=await io.read(path);console.log(path,d.getRoot().listTextures().map(t=>({name:t.getName(),bytes:t.getImage().length,mime:t.getMimeType()})));}
