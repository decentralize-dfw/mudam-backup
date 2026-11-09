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

bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v071.blend'));roof=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];target=roof.copy();target.data=roof.data.copy();bpy.context.collection.objects.link(target);target.name='R169_FACADES'
import bmesh
for obj,remove_roof in [(target,True),(roof,False)]:
 bm=bmesh.new();bm.from_mesh(obj.data);bm.faces.ensure_lookup_table();drop=[f for f in bm.faces if (f.index<35200)==remove_roof];bmesh.ops.delete(bm,geom=drop,context='FACES');loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(obj.data);bm.free()
o=target.copy();o.data=target.data.copy();bpy.context.collection.objects.link(o);o.name='TEMP_COLOR_SAMPLING';bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=4,use_grid_fill=True);bm.to_mesh(o.data);bm.free();colors=[];distances=[]

count=len(o.data.vertices);locations=np.empty((count,3));indices=np.empty(count,dtype=np.int32);distances=np.empty(count)
for i,vert in enumerate(o.data.vertices):
 h,n,idx,dist=tree.find_nearest(o.matrix_world@vert.co);locations[i]=h;indices[i]=idx;distances[i]=dist
tri=verts[faces[indices]];ab=tri[:,1]-tri[:,0];ac=tri[:,2]-tri[:,0];ap=locations-tri[:,0];dot=lambda a,b:np.einsum('ij,ij->i',a,b);aa=dot(ab,ab);bb=dot(ab,ac);cc=dot(ac,ac);dd=dot(ap,ab);ee=dot(ap,ac);den=aa*cc-bb*bb;safe=np.where(abs(den)<1e-15,1,den);uu=(cc*dd-bb*ee)/safe;ww=(aa*ee-bb*dd)/safe;weights=np.c_[1-uu-ww,uu,ww];uv=np.einsum('ij,ijk->ik',weights,uvs[indices]);colors=np.ones((count,4),np.float32);names=np.array(images)[indices]
for name,(arr,size) in cache.items():
 ids=np.where(names==name)[0]
 if not len(ids):continue
 x=(uv[ids,0]%1)*(size[0]-1);y=(uv[ids,1]%1)*(size[1]-1);ix=x.astype(int);iy=y.astype(int);fx=(x-ix)[:,None];fy=(y-iy)[:,None];jx=np.minimum(ix+1,size[0]-1);jy=np.minimum(iy+1,size[1]-1);colors[ids]=(1-fy)*((1-fx)*arr[iy,ix]+fx*arr[iy,jx])+fy*((1-fx)*arr[jy,ix]+fx*arr[jy,jx])
colors[:,:3]=np.where(colors[:,:3]<=.04045,colors[:,:3]/12.92,((colors[:,:3]+.055)/1.055)**2.4);colors[:,3]=1
attr=o.data.color_attributes.new(name='ACT_SURFACE_COLOR',type='FLOAT_COLOR',domain='CORNER');loopids=np.empty(len(o.data.loops),dtype=np.int32);o.data.loops.foreach_get('vertex_index',loopids);attr.data.foreach_set('color',colors[loopids].ravel());print('VECTOR_COLORS',count,flush=True)
m=bpy.data.materials.new('Measured_source_color_emission');m.use_nodes=True;nt=m.node_tree;vc=nt.nodes.new('ShaderNodeVertexColor');vc.layer_name=attr.name;em=nt.nodes.new('ShaderNodeEmission');nt.links.new(vc.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],nt.nodes.get('Material Output').inputs['Surface']);o.data.materials.clear();o.data.materials.append(m)
for f in o.data.polygons:f.material_index=0
img=bpy.data.images.new('R169_FACADE_SOURCE_v073',width=4096,height=4096,alpha=False);m=bpy.data.materials.new('R169_FACADE_SOURCE_BAKED_v073');m.use_nodes=True;nt=m.node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=img;nt.nodes.active=tex;target.data.materials.clear();target.data.materials.append(m)
for f in target.data.polygons:f.material_index=0
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.render.bake.use_selected_to_active=True;s.render.bake.cage_extrusion=.001;s.render.bake.max_ray_distance=.003;s.render.bake.margin=16
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);target.select_set(True);bpy.context.view_layer.objects.active=target;bpy.ops.object.bake(type='EMIT');img.filepath_raw=str(R/'textures/R169_facade_source_v073.png');img.file_format='PNG';img.save();nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color']);nt.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.85;bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT');target.select_set(True);roof.select_set(True);bpy.context.view_layer.objects.active=roof;bpy.ops.object.join();bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v073.blend'),compress=True)
(R/'reports/R169_COLOR_TRANSFER_v073.json').write_text(json.dumps(dict(helper_vertices=len(colors),source_distance_p90=float(np.percentile(distances,90)),max_source_distance=max(distances),accepted=False,scope='Dense nearest-source color sampled onto temporary subdivided authored facades, rebaked to original authored topology. No raw scan mesh retained.'),indent=2));print('DENSE_COLOR_COMPLETE',len(colors))

