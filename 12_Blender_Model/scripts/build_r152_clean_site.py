from pathlib import Path
import bpy,bmesh,json,math,random,numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r152';data=json.loads((D/'clean_site.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R151_WEB_CLEAN_v002.blend'))
s=bpy.context.scene
for o in list(s.objects):
 if o.name.startswith('R151_ACT_') or o.name=='R151_PAV_GROUND_JOIN':bpy.data.objects.remove(o,do_unlink=True)
col=bpy.data.collections.new('R152_CLEAN_NEAR_SITE');s.collection.children.link(col)
def material(name,color,rough=1,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
mats={'grass':material('R152_TURF',(.19,.27,.085)),'paving':material('R152_LIMESTONE_PAVING',(.48,.46,.39),.86),'gravel':material('R152_FINE_GRAVEL',(.42,.36,.25)), 'stone':bpy.data.materials.get('R55_HISTORIC_MASONRY_APPEARANCE_CANDIDATE') or material('R152_HISTORIC_STONE',(.43,.39,.30)), 'zinc':material('R152_FORT_ZINC',(.32,.38,.40),.48,.6),'bark':material('R152_BARK',(.17,.105,.055))}
leafmats=[material('R152_FOLIAGE_'+str(i),c) for i,c in enumerate([(.13,.25,.075),(.19,.30,.10),(.24,.32,.12),(.11,.22,.06)])]
historic_wall=next((o for o in s.objects if o.type=='MESH' and o.name.startswith('R35_WALL_51946353_') and len(o.data.materials)),None)
historic=historic_wall.data.materials[max(range(len(historic_wall.data.materials)),key=lambda i:sum(p.area for p in historic_wall.data.polygons if p.material_index==i))] if historic_wall else None
if historic:mats['stone']=historic
for kind,image_prefix in [('stone','R129_historic_masonry_basecolor'),('grass','R129_moat_turf_basecolor')]:
 textured=next((m for m in bpy.data.materials if m.use_nodes and any(n.type=='TEX_IMAGE' and n.image and n.image.name.startswith(image_prefix) for n in m.node_tree.nodes)),None)
 if textured:mats[kind]=textured
made=[]
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(mat);o['source_ids']='ACT2024_CLASS2,ACT2020_REFERENCE,OSM';o['status']='clean_site_reconstruction_candidate';o['level_id']='SITE';uv=me.uv_layers.new(name='METRIC_UV_4x3m')
 for f in me.polygons:
  n=f.normal;u=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.8 else Vector((1,0,0));v=n.cross(u).normalized()
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/4,q.dot(v)/3)
 required={getattr(n,'uv_map','') for n in mat.node_tree.nodes} if mat.use_nodes else set()
 for uvname in required-{'','METRIC_UV_4x3m'}:
  alias=me.uv_layers.new(name=uvname)
  for a,b in zip(alias.data,uv.data):a.uv=b.uv
 made.append(name);return o
for row in data['meshes']:mesh(row['name'],row['vertices'],row['faces'],mats[row['material']])
def ringmesh(name,center,rings,mat,segments=64):
 vs=[(center[0]+r*math.cos(2*math.pi*i/segments),center[1]+r*math.sin(2*math.pi*i/segments),z) for r,z in rings for i in range(segments)];fs=[]
 for k in range(len(rings)-1):
  for i in range(segments):fs.append([k*segments+i,k*segments+(i+1)%segments,(k+1)*segments+(i+1)%segments,(k+1)*segments+i])
 fs.extend([list(range(segments-1,-1,-1)),list(range((len(rings)-1)*segments,len(rings)*segments))]);return mesh(name,vs,fs,mat)
for row in data['towers']:
 r=row['radius'];z=row['roof'];c=row['center'];ringmesh('R152_FORT_TOWER_'+row['name'],c,[(r,row['base']),(r,z-.55),(r+.12,z-.55),(r+.12,z-.3),(r,z-.3),(r,z)],mats['stone']);ringmesh('R152_FORT_CAP_'+row['name'],c,[(r,z),(r*.85,z+.10),(.28,z+.27)],mats['zinc']);ringmesh('R152_FORT_FINIAL_'+row['name'],c,[(.28,z+.27),(.32,z+.65),(.18,z+.95),(.03,z+1.08)],mats['zinc'],16)
# Extend only the bottoms of inherited historic inner walls; openings and tops
# remain unchanged. Source museum geometry is retained.
p=np.load(D/'ground_samples.npz')['xyz'];tree=KDTree(len(p))
for i,q in enumerate(p):tree.insert((q[0],q[1],0),i)
tree.balance();extended=[];gv=[];gf=[]
for row in data['meshes']:
 if row['name']=='R152_CLASS2_TERRAIN' or row['name'].startswith(('R152_PATH_','R152_FORECOURT_')):
  offset=len(gv);gv.extend(row['vertices']);gf.extend([offset+i for i in f] for f in row['faces'])
ground_bvh=BVHTree.FromPolygons(gv,gf)
def modeled_ground(q):
 hit=ground_bvh.ray_cast(Vector((q.x,q.y,100)),Vector((0,0,-1)),200)[0]
 return hit.z if hit is not None else float('inf')
for o in s.objects:
 if o.type!='MESH' or not o.name.startswith('R35_WALL_51946353_'):continue
 co=[o.matrix_world@v.co for v in o.data.vertices];old=min(q.z for q in co);changed=0
 for v,q in zip(o.data.vertices,co):
  if abs(q.z-old)>.001:continue
  near=tree.find_n((q.x,q.y,0),8);z=min(min(p[i,2] for _,i,d in near),modeled_ground(q))-.2
  if z<q.z:q.z=z;v.co=o.matrix_world.inverted()@q;changed+=1
 if changed:extended.append(dict(name=o.name,vertices=changed));o.data.update()
# The previously registered pavilion bases followed the old photographic
# ground. Extend only their buried lower vertices to the new classified
# ground; retain the window, portal, upper wall and roof coordinates.
for o in s.objects:
 if o.type!='MESH' or not (o.name.startswith('R17_WALL_') or o.name in ('R17_WINDOW_LEFT','R17_WINDOW_RIGHT','R17_WINDOW_SILL','P05_FRONT_0','P05_FRONT_9','P05_FRONT_10')):continue
 if o.name.startswith('P05_FRONT_'):
  zmin=min((o.matrix_world@v.co).z for v in o.data.vertices);low=[v for v in o.data.vertices if abs((o.matrix_world@v.co).z-zmin)<.001]
 else:low=[v for v in o.data.vertices if (o.matrix_world@v.co).z < -4]
 if not low:continue
 samples=[]
 for v in low:
  q=o.matrix_world@v.co;samples.extend(p[i,2] for _,i,d in tree.find_n((q.x,q.y,0),12));samples.append(modeled_ground(q))
 low_ids={v.index for v in low}
 for e in o.data.edges:
  a,b=e.vertices
  if a not in low_ids or b not in low_ids:continue
  va=o.matrix_world@o.data.vertices[a].co;vb=o.matrix_world@o.data.vertices[b].co;count=max(2,int((vb-va).length/.5))
  samples.extend(modeled_ground(va.lerp(vb,i/count)) for i in range(1,count))
 base=min(samples)-.3;changed=0
 for v in low:
  q=o.matrix_world@v.co
  if q.z>base:q.z=base;v.co=o.matrix_world.inverted()@q;changed+=1
 if changed:extended.append(dict(name=o.name,vertices=changed,base=float(base)));o.data.update()
# Canopy positions remain reference data. Rejected placeholder trees are not built.
s['stage']='R152 clean near-site reconstruction candidate';s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
cam=s.camera
for label,eye,target in [('pavilion',(60,-85,20),(25,-37,-5))]:
 for o in col.objects:
  if o.name.startswith('R152_TREE_'):o.hide_render=(label=='pavilion')
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45;s.render.filepath=str(R/f'renders/qa/R152_clean_{label}.png');bpy.ops.render.render(write_still=True)
for o in col.objects:
 if o.name.startswith('R152_TREE_'):o.hide_render=False
out=R/'scenes/MUDAM_R152_TEMIZ_YAKIN_CEVRE_v009.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
exp=R/'exports/r152_clean';exp.mkdir(exist_ok=True);bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:
 if o.type=='MESH':o.select_set(True)
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and o.get('level_id')=='L00_APPROACH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(exp/'near_site.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
bpy.ops.object.select_all(action='DESELECT')
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and o.visible_get() and o.name not in col.objects and o.get('level_id')!='L00_APPROACH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(exp/'building.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
report=dict(scene=str(out),new_objects=len(col.objects),meshes=made,extended_inner_walls=extended,trees=0,limits=data['limits'],accepted=False)
(R/'reports/R152_CLEAN_SITE_BUILD.json').write_text(json.dumps(report,indent=2));print('R152_CLEAN_SITE_SAVED',len(col.objects),flush=True)
