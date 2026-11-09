import bpy,bmesh,json,hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R585_DOGU_HENDEK_CIFT_ZEMIN_TEMIZ_ADAY_v001.blend'))
def signature(o):return hashlib.sha256(str(([tuple(v.co)for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons],o.hide_render)).encode()).hexdigest()
before={o.name:signature(o)for o in bpy.context.scene.objects if o.type=='MESH'}
d=json.loads((R/'reports/R586_APRON_DESIGN.json').read_text());xy=[];idx={}
def ix(p):
 p=tuple(round(v,6)for v in p)
 if p not in idx:idx[p]=len(xy);xy.append(p)
 return idx[p]
fs=[tuple(ix(p)for p in t)for t in d['triangles']];n=len(xy);a,b,c=d['plane'];vs=[(x,y,a*x+b*y+c)for x,y in xy]+[(x,y,-7.6)for x,y in xy];edges=Counter(tuple(sorted((f[i],f[(i+1)%3])))for f in fs for i in range(3));faces=fs+[tuple(v+n for v in reversed(f))for f in fs]+[(a,b,b+n,a+n)for(a,b),count in edges.items()if count==1]
me=bpy.data.meshes.new('R586_WEST_STONE_APRON_RETURN');me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not any(check.values()),check;bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o)
source=bpy.data.objects['R321_MUSEUM_WEST_MOAT_RETAINING'];ma=source.data.materials[0].copy();ma.name='R586_STONE_APRON_UNBAKED'
# An old AO atlas cannot be reused on new geometry.
for node in list(ma.node_tree.nodes):
 if node.type=='GROUP' and 'glTF Material Output' in (node.node_tree.name if node.node_tree else ''):ma.node_tree.nodes.remove(node)
me.materials.append(ma)
for uvname in {u.name for u in source.data.uv_layers}|{'UVMap'}:
 uv=me.uv_layers.new(name=uvname)
 for f in me.polygons:
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.y/3)if abs(f.normal.z)>.5 else(v.x/4,v.z/3)
o['level_id']='SITE';o['source']=d['source'];o['acceptance']='Local candidate; northern termination and exact source correspondence not yet accepted.'
out=R/'scenes/MUDAM_R586_BATI_TAS_TERAS_DONUS_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));after={o.name:signature(o)for o in bpy.context.scene.objects if o.type=='MESH'};changed=[k for k in before if before[k]!=after.get(k)];assert not changed,changed
q=bpy.data.objects['R586_WEST_STONE_APRON_RETURN'];bpy.ops.object.select_all(action='DESELECT');q.select_set(True);bpy.context.view_layer.objects.active=q;bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r586_west_apron_REVIEW.glb'),export_format='GLB',use_selection=True,export_extras=True)
(R/'reports/R586_BUILD.json').write_text(json.dumps(dict(reopened=True,geometry=check,area=d['area'],unchanged=len(before),changed=changed,added=[k for k in after if k not in before],sourceHeldoutRMS=d['heldoutRMS'],sourceHeldoutMax=d['heldoutMax'],accepted=False,published=False),indent=2))
s=bpy.context.scene
for o in s.objects:
 if o.name.startswith('R158_TREE_'):o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-62,-19,39));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-35,5,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=56;s.render.filepath=str(R/'renders/qa/R586_west_apron_candidate.png');bpy.ops.render.render(write_still=True)
