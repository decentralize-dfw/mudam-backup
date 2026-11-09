from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[];uvs=[];images=[];cache={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in me.vertices);uv=me.uv_layers.active
 for t in me.loop_triangles:
  fs.append([off+i for i in t.vertices]);uvs.append([tuple(uv.data[i].uv) for i in t.loops]);mat=me.materials[t.material_index];im=next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image);images.append(im.name)
  if im.name not in cache:
   arr=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(arr);cache[im.name]=(arr.reshape(im.size[1],im.size[0],4),list(im.size))
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);verts=np.array([tuple(v) for v in vs]);faces=np.array(fs);uvs=np.array(uvs)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v064.blend'));o=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];colors=[];distances=[]
for v in o.data.vertices:
 h,n,idx,dist=tree.find_nearest(o.matrix_world@v.co);a,b,c=verts[faces[idx]];ab=b-a;ac=c-a;ap=np.array(h)-a;aa=ab@ab;bb=ab@ac;cc=ac@ac;dd=ap@ab;ee=ap@ac;den=aa*cc-bb*bb
 if abs(den)<1e-15:weights=np.array([1.,0,0])
 else:
  u=(cc*dd-bb*ee)/den;w=(aa*ee-bb*dd)/den;weights=np.array([1-u-w,u,w])
 uv=weights@uvs[idx];arr,size=cache[images[idx]];x=float(uv[0]%1)*(size[0]-1);y=float(uv[1]%1)*(size[1]-1);ix=int(x);iy=int(y);fx=x-ix;fy=y-iy;col=(1-fy)*((1-fx)*arr[iy,ix]+fx*arr[iy,min(ix+1,size[0]-1)])+fy*((1-fx)*arr[min(iy+1,size[1]-1),ix]+fx*arr[min(iy+1,size[1]-1),min(ix+1,size[0]-1)]);colors.append(col);distances.append(dist)
attr=o.data.color_attributes.new(name='ACT_SURFACE_COLOR',type='FLOAT_COLOR',domain='CORNER')
for l in o.data.loops:attr.data[l.index].color=colors[l.vertex_index]
m=bpy.data.materials.new('ACT_nearest_surface_color');m.use_nodes=True;nt=m.node_tree;vc=nt.nodes.new('ShaderNodeVertexColor');vc.layer_name=attr.name;bs=nt.nodes.get('Principled BSDF');nt.links.new(vc.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.85;o.data.materials.append(m)
for p in o.data.polygons:
 if p.index>=35200:p.material_index=len(o.data.materials)-1
path=R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v066.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);(R/'reports/R169_COLOR_TRANSFER_v066.json').write_text(json.dumps(dict(scope='Nearest source surface vertex-color transfer on authored facades; roof baked image retained.',p90_source_distance=float(np.percentile(distances,90)),max_distance=max(distances),accepted=False),indent=2));print('COLOR_DONE',len(colors),np.percentile(distances,90),max(distances))
