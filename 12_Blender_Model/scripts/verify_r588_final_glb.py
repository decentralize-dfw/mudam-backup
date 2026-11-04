"""Read-only compressed GLB validation; writes report only, never a scene."""
import bpy,json,struct,hashlib,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
FILE=R/'exports/r152_clean/r588_near_draco_webp_REVIEW.glb'
REPORT=R/'reports/R588_FINAL_GLB_ROUNDTRIP.json'
release=json.loads((R/'reports/R588_RELEASE_VALIDATION.json').read_text())
data=FILE.read_bytes();digest=hashlib.sha256(data).hexdigest()
assert digest==release['files']['near']['sha256'],'Final GLB does not match release validation'
assert struct.unpack_from('<I',data,0)[0]==0x46546c67
assert struct.unpack_from('<I',data,8)[0]==len(data)
offset=12;doc=None;binary=None
while offset<len(data):
 length,kind=struct.unpack_from('<II',data,offset);offset+=8;chunk=data[offset:offset+length];offset+=length
 if kind==0x4e4f534a:doc=json.loads(chunk)
 elif kind==0x004e4942:binary=chunk
assert doc is not None and binary is not None
required=doc.get('extensionsRequired',[])
assert {'KHR_draco_mesh_compression','EXT_texture_webp'}<=set(required),required
image_checks=[]
for index,image in enumerate(doc.get('images',[])):
 assert 'bufferView'in image,('Unexpected external image',index)
 view=doc['bufferViews'][image['bufferView']];start=view.get('byteOffset',0);encoded=binary[start:start+view['byteLength']]
 assert len(encoded)==view['byteLength'] and len(encoded)>16,(index,'Truncated image')
 assert image.get('mimeType')=='image/webp' and encoded[:4]==b'RIFF' and encoded[8:12]==b'WEBP',(index,'Invalid WebP image')
 image_checks.append(dict(index=index,name=image.get('name'),bytes=len(encoded),sha256=hashlib.sha256(encoded).hexdigest(),embeddedWebP=True))
def texture_infos(value,key=''):
 if isinstance(value,dict):
  if key.lower().endswith('texture') and isinstance(value.get('index'),int):yield value
  for k,v in value.items():yield from texture_infos(v,k)
 elif isinstance(value,list):
  for v in value:yield from texture_infos(v,key)
texture_bindings=0;occlusion_primitives=0
for mesh in doc.get('meshes',[]):
 for primitive in mesh['primitives']:
  if 'material'not in primitive:continue
  material=doc['materials'][primitive['material']]
  for info in texture_infos(material):
   channel=info.get('extensions',{}).get('KHR_texture_transform',{}).get('texCoord',info.get('texCoord',0))
   assert 'TEXCOORD_'+str(channel)in primitive['attributes'],(mesh.get('name'),'Missing referenced UV',channel)
   assert 0<=info['index']<len(doc['textures'])
   texture=doc['textures'][info['index']];image_index=texture.get('extensions',{}).get('EXT_texture_webp',{}).get('source',texture.get('source'))
   assert isinstance(image_index,int) and 0<=image_index<len(image_checks)
   texture_bindings+=1
  if 'occlusionTexture'in material:occlusion_primitives+=1
assert occlusion_primitives>0,'Contact AO texture bindings missing'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(FILE))
errors=[];objects=[];triangle_count=0
for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 mesh=obj.data;mesh.calc_loop_triangles();vertices=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',vertices);vertices=vertices.reshape(-1,3).astype(np.float64)
 if not np.isfinite(vertices).all() or not np.isfinite(np.asarray(obj.matrix_world)).all():errors.append(dict(object=obj.name,error='Nonfinite geometry'))
 idx=np.array([tuple(t.vertices)for t in mesh.loop_triangles],dtype=np.int64)
 if not len(idx):continue
 triangles=vertices[idx];a=triangles[:,1]-triangles[:,0];b=triangles[:,2]-triangles[:,0];cross=np.cross(a,b);areas=np.linalg.norm(cross,axis=1)*.5
 edge=np.maximum.reduce([np.linalg.norm(a,axis=1),np.linalg.norm(b,axis=1),np.linalg.norm(triangles[:,2]-triangles[:,1],axis=1)])
 altitude=2*areas/np.maximum(edge,1e-30);exact=np.all(cross==0,axis=1);bad=exact|((areas<1e-10)&(altitude<1e-5));triangle_count+=len(idx)
 if np.any(bad):errors.append(dict(object=obj.name,error='Decoded collapsed/numerical sliver triangles',count=int(sum(bad)),triangleIndices=np.where(bad)[0].tolist()))
 for layer in mesh.uv_layers:
  values=np.empty(len(layer.data)*2,dtype=np.float32);layer.data.foreach_get('uv',values)
  if len(layer.data)!=len(mesh.loops) or not np.isfinite(values).all():errors.append(dict(object=obj.name,error='Invalid UV array',layer=layer.name))
 for material in mesh.materials:
  if not material or not material.use_nodes:continue
  for node in material.node_tree.nodes:
   if node.type=='UVMAP' and node.uv_map and any(socket.is_linked for socket in node.outputs) and node.uv_map not in mesh.uv_layers:
    errors.append(dict(object=obj.name,error='Material references missing UV',material=material.name,uv=node.uv_map))
 objects.append(dict(name=obj.name,triangles=len(idx),uvLayers=list(mesh.uv_layers.keys()),badTriangles=int(sum(bad)),blenderPolygonAreaBelow1e10=sum(p.area<1e-10 for p in mesh.polygons)))
images=[]
for image in bpy.data.images:
 if image.type=='RENDER_RESULT' or image.users==0:continue
 width,height=image.size
 if width<=0 or height<=0:errors.append(dict(image=image.name,error='Image decoder returned invalid dimensions'));continue
 count=len(image.pixels);sample_indices=sorted(set([0,1,2,3,max(0,count//2),max(0,count-4),max(0,count-1)]));samples=[float(image.pixels[i])for i in sample_indices if i<count]
 valid=count>=width*height and all(math.isfinite(x)for x in samples)
 if not valid:errors.append(dict(image=image.name,error='Invalid decoded image pixels'))
 packed=image.packed_file
 images.append(dict(name=image.name,size=[width,height],channels=image.channels,finitePixelSamples=valid,packedBytes=len(packed.data)if packed else None,packedSHA256=hashlib.sha256(packed.data).hexdigest()if packed else None))
assert images,'No imported textures'
report=dict(file=str(FILE.relative_to(R)),sha256=digest,bytes=len(data),compressedGLBReimported=True,sceneSaved=False,criteria=dict(areaBelow=1e-10,altitudeBelow=1e-5,exactCollapseRejected=True),triangleCount=triangle_count,objects=objects,images=images,embeddedImages=image_checks,textureBindingsChecked=texture_bindings,occlusionPrimitives=occlusion_primitives,requiredExtensions=required,errors=errors,passed=not errors,accepted=False,published=False)
REPORT.write_text(json.dumps(report,indent=2));print('R588_FINAL_GLB_ROUNDTRIP',dict(triangles=triangle_count,objects=len(objects),images=len(images),textureBindings=texture_bindings,errors=errors),flush=True)
assert not errors,errors
