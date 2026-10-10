/* Candidate review only. Direct CC0 ACT tiles; no Ion/Google service or token. */
const C=globalThis.Cesium,status=document.querySelector('#status'),toggle=document.querySelector('#building'),environment=document.querySelector('#environment');
try {
 if(!C)throw new Error('Görüntüleyici kitaplığı yüklenemedi.');
 C.Ion.defaultAccessToken='';
 const configResponse=await fetch('config/act_context_candidate.json');if(!configResponse.ok)throw new Error('Çevre ayarları okunamadı.');
 const config=await configResponse.json();
 const viewer=new C.Viewer('view',{baseLayer:false,globe:false,skyBox:false,skyAtmosphere:false,animation:false,timeline:false,baseLayerPicker:false,geocoder:false,homeButton:false,sceneModePicker:false,navigationHelpButton:false,fullscreenButton:false,requestRenderMode:true});
 viewer.scene.backgroundColor=C.Color.fromCssColorString('#30383b');
 const target=C.Cartesian3.fromDegrees(...config.anchor_degrees,config.datum_ellipsoid_candidate);
 const home=()=>{viewer.camera.lookAt(target,new C.HeadingPitchRange(C.Math.toRadians(-32),C.Math.toRadians(-44),650));viewer.camera.lookAtTransform(C.Matrix4.IDENTITY);viewer.scene.requestRender();};
 document.querySelector('#home').addEventListener('click',home);home();
 const resource=new C.Resource({url:config.tileset_url,retryAttempts:3,retryCallback:()=>Promise.resolve(true)});
 const tiles=await C.Cesium3DTileset.fromUrl(resource,{maximumScreenSpaceError:1,cacheBytes:768*1024*1024,maximumCacheOverflowBytes:256*1024*1024,credit:'ACT Luxembourg · mesh3D 2020 · CC0'});viewer.scene.primitives.add(tiles);
 tiles.tileFailed.addEventListener(e=>{status.textContent='Bazı çevre parçaları yüklenemedi; bağlantı kontrol edilmeli.';console.error(`ACT tile: ${e.url} — ${e.message}`);});
 status.textContent='Çevre açık; yerleştirilmiş bina yükleniyor…';
 const localCandidate=new URLSearchParams(location.search).get('candidate')==='1';
 const releaseURL=new URL(localCandidate?'config/act_candidate_release.json':'config/model_release.json',location.href);const rr=await fetch(releaseURL);if(!rr.ok)throw new Error('Model yayın kaydı okunamadı.');const release=await rr.json();
 const response=await fetch(new URL(release.url,releaseURL));if(!response.ok)throw new Error('Bina modeli indirilemedi.');
 const bytes=await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
 const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');if(hash!==release.sha256)throw new Error('Bina dosyası yayın kaydıyla eşleşmiyor.');
 const blobURL=URL.createObjectURL(new Blob([bytes],{type:'model/gltf-binary'}));
 const model=await C.Model.fromGltfAsync({url:blobURL,modelMatrix:C.Matrix4.fromArray(config.local_to_ecef_column_major),show:false});URL.revokeObjectURL(blobURL);viewer.scene.primitives.add(model);
 for(const name of config.hide_model_nodes){const node=model.getNode(name);if(node)node.show=false;}
 if(!C.ClippingPolygonCollection.isSupported(viewer.scene))throw new Error('Birleşik görünüm bu cihazda desteklenmiyor; kaynak çevre gösteriliyor.');
 const clipping=new C.ClippingPolygonCollection({enabled:false,polygons:config.clipping_polygons_degrees.map(points=>new C.ClippingPolygon({positions:C.Cartesian3.fromDegreesArray(points.flat())}))});tiles.clippingPolygons=clipping;
 const setBuilding=()=>{model.show=toggle.checked;clipping.enabled=toggle.checked;viewer.scene.requestRender();};toggle.disabled=false;toggle.checked=true;toggle.addEventListener('change',setBuilding);setBuilding();
 environment.disabled=false;environment.addEventListener('change',()=>{tiles.show=environment.checked;viewer.scene.requestRender();});
 status.textContent=`${release.revision} + ACT çevresi · birleştirme adayı`;
 globalThis.mudamContextCandidate={viewer,tiles,model,release,config};
} catch(error){status.textContent=error.message;console.error(error);}
