"""Match the small interpolated seam to adjacent ACT geometry and photo colours."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];out=root/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v009.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(root/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v008.blend'))
patch=bpy.data.objects['R151_PAV_GROUND_JOIN'];positions=[];faces=[];lookup=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith('R151_ACT_'):continue
 bounds=[o.matrix_world@Vector(c) for c in o.bound_box]
 if max(q.x for q in bounds)<18 or min(q.x for q in bounds)>43 or max(q.y for q in bounds)<-55 or min(q.y for q in bounds)>-30:continue
 for f in o.data.polygons:
  if len(f.vertices)!=3:continue
  ps=[o.matrix_world@o.data.vertices[i].co for i in f.vertices];center=sum(ps,Vector())/3
  if not (18<center.x<43 and -55<center.y<-30 and center.z<-2.5):continue
  n=(ps[1]-ps[0]).cross(ps[2]-ps[0]).normalized()
  if abs(n.z)<.4:continue
  i=len(positions);positions.extend(ps);faces.append((i,i+1,i+2));lookup.append((o,f.index))
assert faces
tree=BVHTree.FromPolygons(positions,faces,all_triangles=True)
edge_counts={}
for f in patch.data.polygons:
 for a,b in f.edge_keys:edge_counts[(a,b)]=edge_counts.get((a,b),0)+1
boundary={i for edge,count in edge_counts.items() if count==1 for i in edge}
cache={};colours=[];distances=[];snapped=[]
for v in patch.data.vertices:
 q=patch.matrix_world@v.co;near,normal,idx,distance=tree.find_nearest(q);distances.append(distance)
 o,face_index=lookup[idx];f=o.data.polygons[face_index];tri=[positions[i] for i in faces[idx]]
 if v.index in boundary and (Vector((q.x,q.y))-Vector((near.x,near.y))).length<.4:
  z=tri[0].z-(normal.x*(q.x-tri[0].x)+normal.y*(q.y-tri[0].y))/normal.z
  if abs(z-q.z)<1.5:snapped.append(dict(vertex=v.index,old_z=q.z,new_z=z));q.z=z;v.co=patch.matrix_world.inverted()@q
 mat=o.data.materials[f.material_index];im=next((n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image),None);assert im
 if im.name not in cache:cache[im.name]=(list(im.pixels[:]),*im.size)
 pixels,w,h=cache[im.name];uvs=[o.data.uv_layers.active.data[i].uv for i in f.loop_indices]
 uv=geometry.barycentric_transform(near,*tri,*[Vector((u.x,u.y,0)) for u in uvs]);x=min(w-1,max(0,round((uv.x%1)*(w-1))));y=min(h-1,max(0,round((uv.y%1)*(h-1))));offset=4*(y*w+x);colours.append((*pixels[offset:offset+3],1))
patch.data.update();attr=patch.data.color_attributes.new(name='ACT_GROUND_PHOTO_BLEND',type='FLOAT_COLOR',domain='CORNER')
for loop in patch.data.loops:attr.data[loop.index].color_srgb=colours[loop.vertex_index]
mat=bpy.data.materials.new('R151_ACT_GROUND_PHOTO_BLEND');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();attrnode=nodes.new('ShaderNodeVertexColor');attrnode.layer_name=attr.name;emit=nodes.new('ShaderNodeEmission');output=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(attrnode.outputs['Color'],emit.inputs['Color']);mat.node_tree.links.new(emit.outputs[0],output.inputs['Surface']);patch.data.materials.clear();patch.data.materials.append(mat)
patch['assumption_note']='Small interpolated terrain seam. Boundary heights and nearest photo-ground colours sampled from ACT 2020; interior heights from ACT 2024 LiDAR. This is blending geometry, not a surveyed hidden surface.'
s=bpy.context.scene;c=s.camera;c.location=(45,-44,4);c.rotation_euler=(Vector((30.58,-43.29,-7))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=28;s.render.filepath=str(root/'renders/qa/R151_v009_ground_seam.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(root/'reports/R151_v009_ground_blend.json').write_text(json.dumps(dict(file=str(out),accepted=False,source_ground_faces=len(faces),boundary_vertices_snapped=snapped,colour_sample_max_distance=max(distances),image_count=len(cache),limits=['Nearest-ground photo colour interpolation; not original photographic coverage inside removed building footprint.','Local seam and duplicate-surface inspection required before production acceptance.']),indent=2))
print('R151_v009_SAVED',flush=True)
