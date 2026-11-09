from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
root=Path(__file__).resolve().parents[1];data=json.loads((root/'.local_source_cache/act_context/pavilion_ground_join.json').read_text())
out=root/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v008.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(root/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v007.blend'))
me=bpy.data.meshes.new('R151_PAV_GROUND_JOIN');me.from_pydata(data['vertices'],[],data['triangles']);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for f in me.polygons:
 if f.normal.z<0:f.flip()
ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(bpy.data.objects['R68_MOAT_GROUND'].data.materials[0]);uv=me.uv_layers.new(name='R151_GROUND_METRIC_UV')
for f in me.polygons:
 for li in f.loop_indices:
  q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.x/4,q.y/3)
ob['status']='conditional_interpolated_ground_join';ob['source_ids']='ACT_LIDAR2024_CLASS2';changed=[]
from mathutils.kdtree import KDTree
points=data['source_ground_points'];tree=KDTree(len(points))
for i,p in enumerate(points):tree.insert((p[0],p[1],0),i)
tree.balance()
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith('R17_') or o.hide_render:continue
 coords=[o.matrix_world@v.co for v in o.data.vertices]
 if not coords or abs(min(q.z for q in coords)+3.831193685531616)>1e-4:continue
 o.data=o.data.copy();inv=o.matrix_world.inverted()
 for v,q in zip(o.data.vertices,coords):
  if abs(q.z+3.831193685531616)<1e-4:
   near=tree.find_n((q.x,q.y,0),8);weights=[1/max(d,.05)**2 for _,i,d in near];z=sum(points[i][2]*w for (_,i,d),w in zip(near,weights))/sum(weights);q.z=min(q.z,z-.15);v.co=inv@q
 o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(o.data);bm.free();changed.append(o.name)
scene=bpy.context.scene;cam=scene.camera
for label,eye,target,lens in [('museum',(92,-130,120),(0,5,0),48),('ground_seam',(45,-44,4),(30.58,-43.29,-7),28)]:
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;scene.render.filepath=str(root/f'renders/qa/R151_v008_{label}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(root/'reports/R151_v008_ground_join_build.json').write_text(json.dumps(dict(file=str(out),accepted=False,changed_walls=changed,new_mesh=ob.name,ground_area=data['domain_area'],source_distances=data['nearest_source_distance_quantiles'],limits=data['limits'],remaining=['Local visual seam acceptance','Duplicate source-surface exclusion','Independent reopen and inheritance check','Publish only after complete scene and viewer acceptance']),indent=2))
print('R151_v008_SAVED',flush=True)
