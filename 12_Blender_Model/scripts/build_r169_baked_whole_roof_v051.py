from pathlib import Path
import bpy,json,math,bmesh,numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169'
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 ob.data.calc_loop_triangles();off=len(vs);vs.extend(ob.matrix_world@v.co for v in ob.data.vertices);fs.extend([off+i for i in t.vertices] for t in ob.data.loop_triangles)
source_tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_KAYNAK_CATI_ADAY_v045.blend'))
roof=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];bpy.ops.object.select_all(action='DESELECT');roof.select_set(True);bpy.context.view_layer.objects.active=roof
# Replace inferred vertical skirt with source-measured facade/eave sections.
d=json.loads((D/'row_whole_roof_samples_v045.json').read_text());nx=d['nx'];ny=d['ny'];ring=[Vector((*p,0)) for p in d['ring']];cut=-65.65
me=roof.data;vs=[tuple(v.co) for v in me.vertices[:nx*ny]];fs=[tuple(p.vertices) for p in me.polygons if p.material_index==0];roof_faces=len(fs);measurements=[];fallbacks=0
edges=[list(range(nx)),[j*nx+nx-1 for j in range(ny)],list(range(ny*nx-1,(ny-1)*nx-1,-1)),[j*nx for j in range(ny-1,-1,-1)]]
# This ring is clockwise in XY; outward is its left normal.
for edge in edges:
 tangent=(Vector(vs[edge[-1]])-Vector(vs[edge[0]]));tangent.z=0;tangent.normalize();normal=Vector((-tangent.y,tangent.x,0));rows=[]
 for idx in edge:
  top=Vector(vs[idx]);row=[idx]
  for k in range(1,13):
   z=top.z+(cut-top.z)*k/12;p=Vector((top.x,top.y,z));h,*_=source_tree.ray_cast(p+normal*1.2,-normal,2.4)
   if h is not None and abs((h-p).dot(normal))<.8:
    point=h;measurements.append(float((h-p).dot(normal)))
   else:point=p;fallbacks+=1
   row.append(len(vs));vs.append(tuple(point))
  rows.append(row)
 for a,b in zip(rows,rows[1:]):
  for k in range(12):fs.append((a[k],a[k+1],b[k+1],b[k]))
new=bpy.data.meshes.new('R169_SOURCE_ROOF_AND_EAVE');new.from_pydata(vs,[],fs);new.materials.clear()
for m in me.materials:new.materials.append(m)
for p in new.polygons:p.material_index=int(p.index>=roof_faces)
roof.data=new
bm=bmesh.new();bm.from_mesh(new);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(new);bm.free()
(R/'reports/R169_EAVE_SECTIONS_v051.json').write_text(json.dumps(dict(measured=len(measurements),fallback=fallbacks,max_offset=max(abs(x) for x in measurements),accepted=False),indent=2))
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
for f in roof.data.polygons:f.use_smooth=f.material_index==0
# Angle split preserves sharp roof feature boundaries while smoothing sampling facets.
mod=roof.modifiers.new('Measured feature creases','EDGE_SPLIT');mod.split_angle=math.radians(35);mod.use_edge_angle=True;bpy.ops.object.modifier_apply(modifier=mod.name)
img=bpy.data.images.new('R169_WHOLE_ROOF_SOURCE_COLOR',width=2048,height=2048,alpha=False)
mat=bpy.data.materials.new('R169_WHOLE_ROOF_BAKED');mat.use_nodes=True;nodes=mat.node_tree.nodes;tex=nodes.new('ShaderNodeTexImage');tex.image=img;nodes.active=tex;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.82
roof.data.materials.clear();roof.data.materials.append(mat)
with bpy.data.libraries.load(str(D/'source.blend'),link=False) as (src,dst):dst.objects=src.objects
sources=[]
for ob in dst.objects:
 if ob is not None and ob.type=='MESH':bpy.context.collection.objects.link(ob);sources.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in sources:ob.select_set(True)
bpy.context.view_layer.objects.active=sources[0];bpy.ops.object.join();sources=[bpy.context.object]
for sm in sources[0].data.materials:
 if not sm or not sm.use_nodes:continue
 nt=sm.node_tree;st=next((n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image),None)
 if st:
  em=nt.nodes.new('ShaderNodeEmission');nt.links.new(st.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
s=bpy.context.scene;s.render.engine='CYCLES' ;s.cycles.samples=1;s.render.bake.use_selected_to_active=True;s.render.bake.cage_extrusion=.35;s.render.bake.max_ray_distance=.80;s.render.bake.use_pass_direct=False;s.render.bake.use_pass_indirect=False;s.render.bake.use_pass_color=True;s.render.bake.margin=16
bpy.ops.object.select_all(action='DESELECT')
for ob in sources:ob.select_set(True)
roof.select_set(True);bpy.context.view_layer.objects.active=roof;bpy.ops.object.bake(type='EMIT')
img.filepath_raw=str(R/'textures/R169_whole_roof_source_v051.png');img.file_format='PNG';img.save();mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
for ob in sources:bpy.data.objects.remove(ob,do_unlink=True)
path=R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v051.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
s=bpy.context.scene;s.render.bake.use_selected_to_active=False;s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20
for tag,pos in [('rear',(-80,-285,-48)),('front',(-50,-307,-43)),('top',(-67,-299,-30))]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/('renders/qa/R169_whole_v051_'+tag+'.png'));bpy.ops.render.render(write_still=True)
print('WHOLE_ROOF_BAKED',path)
