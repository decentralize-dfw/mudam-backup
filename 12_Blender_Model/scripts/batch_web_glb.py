"""Bake static node transforms and batch identical material/attribute primitives.
Images/materials stay byte-identical. This is a separate visual web LOD, not the
element-selectable authoring model. No animation, skins or morphs are supported.
"""
from pathlib import Path
import json,struct,sys,gzip,hashlib,copy
import numpy as np
DT={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}
W={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def batch(src,dst):
 raw=Path(src).read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);binary=raw[28+n:]
 assert not d.get('animations') and not d.get('skins')
 context='context' in Path(src).stem
 if context:
  for mat in d.get('materials',[]):
   if 'KHR_materials_unlit' in mat.get('extensions',{}):continue
   assert mat.get('emissiveFactor')==[1,1,1] and mat.get('pbrMetallicRoughness',{}).get('baseColorFactor')==[0,0,0,1]
   mat['pbrMetallicRoughness']={'baseColorTexture':mat.pop('emissiveTexture'),'metallicFactor':0,'roughnessFactor':1}
   mat.pop('emissiveFactor');mat.setdefault('extensions',{})['KHR_materials_unlit']={}
  d.setdefault('extensionsUsed',[]).append('KHR_materials_unlit')
 def arr(i):
  a=d['accessors'][i];assert 'sparse' not in a;v=d['bufferViews'][a['bufferView']];w=W[a['type']];dt=np.dtype(DT[a['componentType']]);return np.ndarray((a['count'],w),dt,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',w*dt.itemsize),dt.itemsize)).copy()
 def matrix(n):
  if 'matrix' in n:return np.array(n['matrix']).reshape(4,4).T
  x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
 groups={};before_tri=0;before_calls=0;bounds=[]
 def walk(i,parent):
  nonlocal before_tri,before_calls
  node=d['nodes'][i];m=parent@matrix(node)
  if 'mesh' in node:
   for p in d['meshes'][node['mesh']]['primitives']:
    assert p.get('mode',4)==4 and not p.get('targets')
    attrs={k:arr(a) for k,a in p['attributes'].items()};pos=attrs['POSITION'];attrs['POSITION']=(pos@m[:3,:3].T+m[:3,3]).astype('<f4');bounds.extend([attrs['POSITION'].min(0),attrs['POSITION'].max(0)])
    if 'NORMAL' in attrs:
     norm=attrs['NORMAL']@np.linalg.inv(m[:3,:3]);norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-20);attrs['NORMAL']=norm.astype('<f4')
    if 'TANGENT' in attrs:
     t=attrs['TANGENT'].copy();t[:,:3]=t[:,:3]@m[:3,:3].T;t[:,:3]/=np.maximum(np.linalg.norm(t[:,:3],axis=1)[:,None],1e-20);t[:,3]*=np.sign(np.linalg.det(m[:3,:3]));attrs['TANGENT']=t
    ids=arr(p['indices']).reshape(-1).astype('<u4') if 'indices' in p else np.arange(len(pos),dtype='<u4')
    if np.linalg.det(m[:3,:3])<0:ids=ids.reshape(-1,3)[:,[0,2,1]].reshape(-1)
    if 'KHR_materials_unlit' in d.get('materials',[])[p.get('material',0)].get('extensions',{}):
     attrs.pop('NORMAL',None);attrs.pop('TANGENT',None)
    if context:
     attrs['POSITION']=np.round(attrs['POSITION'],3)
    sig=tuple((k,d['accessors'][a]['componentType'],d['accessors'][a]['type'],d['accessors'][a].get('normalized',False)) for k,a in sorted(p['attributes'].items()) if k in attrs)
    key=(p.get('material',-1),sig);g=groups.setdefault(key,dict(attrs={k:[] for k in attrs},indices=[],count=0))
    for k,a in attrs.items():g['attrs'][k].append(a)
    g['indices'].append(ids+g['count']);g['count']+=len(pos);before_tri+=len(ids)//3;before_calls+=1
  for child in node.get('children',[]):walk(child,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,np.eye(4))
 output=bytearray();views=[];accessors=[];primitives=[]
 def view(data):
  output.extend(b'\0'*((-len(output))%4));i=len(views);views.append(dict(buffer=0,byteOffset=len(output),byteLength=len(data)));output.extend(data);return i
 for (material,sig),g in groups.items():
  at={}
  arrays={k:np.concatenate(g['attrs'][k]) for k in g['attrs']}
  records=np.concatenate([a.view('u1').reshape(len(a),-1) for a in arrays.values()],axis=1)
  _,unique,inverse=np.unique(np.ascontiguousarray(records).view(np.dtype((np.void,records.shape[1]))).reshape(-1),return_index=True,return_inverse=True)
  order=np.argsort(unique);unique=unique[order];remap=np.empty(len(order),dtype='<u4');remap[order]=np.arange(len(order));inverse=remap[inverse]
  for k,ctype,typ,normalized in sig:
   a=arrays[k][unique];idx=len(accessors);q=dict(bufferView=view(a.tobytes()),componentType=ctype,type=typ,count=len(a))
   if normalized:q['normalized']=True
   if k=='POSITION':q.update(min=a.min(0).tolist(),max=a.max(0).tolist())
   accessors.append(q);at[k]=idx
  ids=inverse[np.concatenate(g['indices'])].astype('<u4');idx=len(accessors);accessors.append(dict(bufferView=view(ids.tobytes()),componentType=5125,type='SCALAR',count=len(ids)));p=dict(attributes=at,indices=idx,mode=4)
  if material>=0:p['material']=material
  primitives.append(p)
 images=copy.deepcopy(d.get('images',[]))
 for im in images:
  assert 'bufferView' in im and 'uri' not in im
  v=d['bufferViews'][im['bufferView']];payload=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];im['bufferView']=view(payload)
 doc={k:copy.deepcopy(d[k]) for k in ['asset','materials','textures','samplers','extensionsUsed','extensionsRequired'] if k in d};doc.update(scene=0,scenes=[dict(nodes=[0])],nodes=[dict(name=Path(dst).stem,mesh=0)],meshes=[dict(primitives=primitives)],images=images,bufferViews=views,accessors=accessors,buffers=[dict(byteLength=len(output))]);output.extend(b'\0'*((-len(output))%4));doc['buffers'][0]['byteLength']=len(output)
 jb=json.dumps(doc,separators=(',',':')).encode();jb+=b' '*((-len(jb))%4);packed=struct.pack('<4sII',b'glTF',2,28+len(jb)+len(output))+struct.pack('<I4s',len(jb),b'JSON')+jb+struct.pack('<I4s',len(output),b'BIN\0')+output
 Path(dst).write_bytes(packed);gz=Path(str(dst)+'.gz');gz.write_bytes(gzip.compress(packed,compresslevel=9,mtime=0));assert gzip.decompress(gz.read_bytes())==packed
 report=dict(file=str(dst),source=str(src),triangles=before_tri,draw_primitives_before=before_calls,draw_primitives_after=len(primitives),bytes=len(packed),gzip_bytes=gz.stat().st_size,sha256=hashlib.sha256(packed).hexdigest(),bounds=[np.min(bounds,axis=0).tolist(),np.max(bounds,axis=0).tolist()],images=len(images),image_payloads_preserved=True,context_emission_converted_to_unlit=context,position_rounding_m=.001 if context else 0)
 Path(str(dst)+'.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True);return report
if __name__=='__main__':batch(sys.argv[1],sys.argv[2])

