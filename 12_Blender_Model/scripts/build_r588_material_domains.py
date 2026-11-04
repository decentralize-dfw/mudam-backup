"""Prepared only. Run after the v010 integration scene exists; does not alter geometry elevations."""
import argparse,sys,json,hashlib
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
DRAFT=ROOT/'reports/R588_R552_MATERIAL_DOMAIN_DRAFT.json'
p=argparse.ArgumentParser();p.add_argument('--source',default=str(ROOT/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v010.blend'));p.add_argument('--output',default=str(ROOT/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v011.blend'));p.add_argument('--earth-material',default='R588_WEST_EARTH_NO_STALE_AO');p.add_argument('--report',default=str(ROOT/'reports/R588_R552_MATERIAL_DOMAIN_BUILD.json'));a=p.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else[])
assert Path(a.source).is_file(),a.source
assert Path(a.source).resolve()!=Path(a.output).resolve(),'Never overwrite source'
assert not Path(a.output).exists(),'Output already exists; choose another path'
bpy.ops.wm.open_mainfile(filepath=a.source);d=json.loads(DRAFT.read_text());boundary=d['north_masonry_boundary_xy'];target='R552_WEST_SLOPING_MASONRY_PLINTH';o=bpy.data.objects[target]
assert all(abs(v)<1e-8 for v in o.location) and all(abs(v-1)<1e-8 for v in o.scale) and all(abs(v)<1e-8 for v in o.rotation_euler),'Expected identity local coordinates'
mat=bpy.data.materials.get(a.earth_material);assert mat is not None,a.earth_material

def sig(ob):
 if ob.type!='MESH':return None
 h=hashlib.sha256();h.update(repr(tuple(tuple(v.co)for v in ob.data.vertices)).encode());h.update(repr(tuple(tuple(f.vertices)for f in ob.data.polygons)).encode());h.update(repr(tuple(m.name for m in ob.data.materials)).encode())
 for uv in ob.data.uv_layers:h.update(uv.name.encode());h.update(repr(tuple(tuple(t.uv)for t in uv.data)).encode())
 return h.hexdigest()
before={x.name:sig(x)for x in bpy.context.scene.objects if x.type=='MESH'};count=len(bpy.context.scene.objects);o.data.calc_loop_triangles();oldverts=[v.co.copy()for v in o.data.vertices];oldtris=[tuple(t.vertices)for t in o.data.loop_triangles];tree=BVHTree.FromPolygons(oldverts,oldtris,all_triangles=True)
# Copy only R552 materials before dropping obsolete glTF AO nodes; shared originals remain untouched.
original_uv_names_before_compaction=[u.name for u in o.data.uv_layers]
copied_materials=[]
for i,original in enumerate(list(o.data.materials)):
 local=original.copy();local.name=original.name+'_R588_LOCAL_NO_STALE_AO'
 removed_groups=[]
 for nd in list(local.node_tree.nodes):
  if nd.type=='GROUP' and nd.node_tree and 'glTF Material Output' in nd.node_tree.name:
   removed_groups.append(nd.node_tree.name);local.node_tree.nodes.remove(nd)
 o.data.materials[i]=local;copied_materials.append(dict(original=original.name,copy=local.name,removed_ao_groups=removed_groups))
def connected_uvs(material):
 found=set();seen=set();implicit=False
 def walk(n):
  nonlocal implicit
  if n in seen:return
  seen.add(n)
  if n.type in ('UVMAP','NORMAL_MAP') and n.uv_map:found.add(n.uv_map)
  if n.type=='TEX_IMAGE'and not n.inputs['Vector'].is_linked:implicit=True
  if n.type=='TEX_COORD'and n.outputs['UV'].is_linked:implicit=True
  for socket in n.inputs:
   for lk in socket.links:walk(lk.from_node)
 for output in material.node_tree.nodes:
  if output.type=='OUTPUT_MATERIAL':walk(output)
 if implicit:
  active=next((u.name for u in o.data.uv_layers if u.active_render),None)
  if active:found.add(active)
 return found
used_uv=set().union(*(connected_uvs(m)for m in o.data.materials))
future_uv=connected_uvs(mat)|{'R588_CAP_SANDSTONE_3M'}
used_uv_hash_before={name:hashlib.sha256(repr(tuple(tuple(t.uv)for t in o.data.uv_layers[name].data)).encode()).hexdigest()for name in used_uv}
removed_unused_uv_layers=[]
for uv_name in [u.name for u in o.data.uv_layers]:
 if uv_name not in used_uv|future_uv:
  removed_unused_uv_layers.append(uv_name);o.data.uv_layers.remove(o.data.uv_layers[uv_name])
for name,digest in used_uv_hash_before.items():assert hashlib.sha256(repr(tuple(tuple(t.uv)for t in o.data.uv_layers[name].data)).encode()).hexdigest()==digest
assert len(set(u.name for u in o.data.uv_layers)|future_uv)<=7,'Reserve one of eight UV slots for new AO'
bm=bmesh.new();bm.from_mesh(o.data);vol0=bm.calc_volume(signed=False);old_uv_names=[x.name for x in o.data.uv_layers]
# Geometric subdivisions only: vertical planes leave every existing surface in place.
for left,right in zip(boundary,boundary[1:]):
 dx,dy=right[0]-left[0],right[1]-left[1]
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-8,plane_co=(left[0],left[1],0),plane_no=(-dy,dx,0),clear_inner=False,clear_outer=False)
for x in [boundary[0][0],boundary[-1][0]]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-8,plane_co=(x,0,0),plane_no=(1,0,0),clear_inner=False,clear_outer=False)
slot=next((i for i,m in enumerate(o.data.materials)if m==mat),None)
if slot is None:slot=len(o.data.materials);o.data.materials.append(mat)
def edge_y(x):
 for q,r in zip(boundary,boundary[1:]):
  if q[0]-1e-8<=x<=r[0]+1e-8:return q[1]+(r[1]-q[1])*(x-q[0])/(r[0]-q[0])
 return None
changed_faces=0;changed_area=0.
for f in bm.faces:
 c=f.calc_center_median();yb=edge_y(c.x)
 if f.normal.z>.5 and yb is not None and c.y>yb+1e-7:
  f.material_index=slot;changed_faces+=1;changed_area+=f.calc_area()
assert changed_faces>0
bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));vol1=bm.calc_volume(signed=False);assert abs(vol1-vol0)<max(1e-6,vol0*1e-7),(vol0,vol1)
checks=dict(nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_area=sum(f.calc_area()<1e-12 for f in bm.faces));assert not any(checks.values()),checks
max_distance=max(tree.find_nearest(v.co)[3]for v in bm.verts);assert max_distance<1e-5,max_distance
bm.to_mesh(o.data);bm.free();o.data.update();assert all(x in o.data.uv_layers for x in old_uv_names)
# The ground material uses world-metric UVs. Existing stone UV layers are preserved.
known={'R545_GROUND_ATLAS':lambda v:((v.x+80)/160,(v.y+85)/180),'R545_MICRO_2M':lambda v:(v.x/2,v.y/2),'R554_STONE_METRIC_2_5M':lambda v:(v.x/2.5,v.y/2.5),'R556_STONE_ATLAS_20x10':lambda v:(v.x/20,v.y/10)}
required=set()
def visit_node(n,seen):
 if n in seen:return
 seen.add(n)
 if n.type=='UVMAP'and n.uv_map:required.add(n.uv_map)
 for socket in n.inputs:
  for link in socket.links:visit_node(link.from_node,seen)
for output in mat.node_tree.nodes:
 if output.type=='OUTPUT_MATERIAL':visit_node(output,set())
added=[]
for name in required:
 if name in o.data.uv_layers:continue
 assert name in known,('Missing unknown material UV',name)
 uv=o.data.uv_layers.new(name=name);assert uv is not None,('UV allocation failed',name);added.append(name)
 for li,loop in enumerate(o.data.loops):uv.data[li].uv=known[name](o.data.vertices[loop.vertex_index].co)
# Separate horizontal worn mineral stone from the vertical wall's coursed masonry.
# Reuse the already local CC0 sandstone maps and documented 3m physical repeat.
base=bpy.data.materials.get('R506_TOWER_SANDSTONE_CC0');assert base is not None
cap=base.copy();cap.name='R588_WEST_HORIZONTAL_SANDSTONE_CC0';cap['source']='Poly Haven sandstone_blocks_04, Rob Tuytel, CC0; existing R506 source record;3m repeat. Compatible worn mineral cap, not surveyed joint-layout reproduction.'
for node in cap.node_tree.nodes:
 if node.type=='UVMAP':node.uv_map='R588_CAP_SANDSTONE_3M'
 if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.25
bs=next(n for n in cap.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
# Persistent CC0-only color derivative prepared explicitly; no runtime color nodes.
# AO baking does not bake base color. Keep a direct glTF-compatible image connection.
from shutil import copyfile
prepared=ROOT/'textures/R588_cap_sandstone_pale_basecolor.png';assert prepared.is_file(),prepared
persistent=ROOT/'textures/R588_cap_sandstone_pale_basecolor.png'
if not persistent.exists()or hashlib.sha256(persistent.read_bytes()).digest()!=hashlib.sha256(prepared.read_bytes()).digest():copyfile(prepared,persistent)
pale=bpy.data.images.load(str(persistent),check_existing=True);pale.colorspace_settings.name='sRGB';pale.pack();pale['source']='CC0 Poly Haven sandstone_blocks_04; pale linearRGB color derivative. No ACT image content.'
link=next(iter(bs.inputs['Base Color'].links),None);assert link and link.from_node.type=='TEX_IMAGE','Expected direct PBR base-color image'
link.from_node.image=pale
cap_objects=[]
for ob in [o,bpy.data.objects['R588_WEST_APRON_AND_RETAINING_BODY']]:
 selected=[f for f in ob.data.polygons if f.normal.z>.7 and ((ob==o and f.material_index!=slot)or(ob!=o and 'STONE' in ob.data.materials[f.material_index].name and 'EARTH' not in ob.data.materials[f.material_index].name))]
 assert selected,ob.name
 capslot=len(ob.data.materials);ob.data.materials.append(cap)
 for f in selected:f.material_index=capslot
 uv=ob.data.uv_layers.get('R588_CAP_SANDSTONE_3M')or ob.data.uv_layers.new(name='R588_CAP_SANDSTONE_3M');assert uv is not None,('Cap UV allocation failed',ob.name);assert len(ob.data.uv_layers)<=7,('No final AO slot',ob.name)
 for li,loop in enumerate(ob.data.loops):
  v=ob.matrix_world@ob.data.vertices[loop.vertex_index].co;uv.data[li].uv=(v.x/3,v.y/3)
 cap_objects.append(dict(object=ob.name,top_faces=len(selected)))
after={x.name:sig(x)for x in bpy.context.scene.objects if x.type=='MESH'};changed=[k for k in before if before[k]!=after.get(k)];assert set(changed)=={target,'R588_WEST_APRON_AND_RETAINING_BODY'},changed;assert len(bpy.context.scene.objects)==count
bpy.ops.wm.save_as_mainfile(filepath=a.output,compress=True);bpy.ops.wm.open_mainfile(filepath=a.output)
report=dict(source=a.source,output=a.output,source_domain=str(DRAFT),reopened=True,changed_objects=changed,earth_faces_before_triangulation=changed_faces,earth_surface_area_m2=changed_area,volume_before=vol0,volume_after=vol1,max_vertex_to_original_surface_distance_m=max_distance,checks=checks,original_uv_layers_preserved=old_uv_names,original_uv_names_before_compaction=original_uv_names_before_compaction,removed_unused_uv_layers=removed_unused_uv_layers,copied_r552_materials=copied_materials,used_uv_coordinates_identical_after_compaction=True,final_ao_slot_reserved=True,added_required_uv_layers=added,horizontal_cap_material="R588_WEST_HORIZONTAL_SANDSTONE_CC0",cap_material_assignments=cap_objects,cap_texture_repeat_m=3,cap_normal_strength=.25,cap_requires_texture_bake=False,cap_color_derivative=str(persistent),cap_basecolor_connection="direct TEX_IMAGE to Principled Base Color",occlusion_bake_scope="AO only; no base-color conversion assumed",accepted=False,published=False)
Path(a.report).write_text(json.dumps(report,indent=2),encoding='utf-8');print('R588_R552_MATERIAL_DOMAIN',json.dumps(report))
