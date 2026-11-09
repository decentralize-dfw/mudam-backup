from pathlib import Path
import bpy,json,math,random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r158/trees.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R157_ARAZI_YOLLAR_AGACLAR_v004.blend'));s=bpy.context.scene
for o in list(s.objects):
 if o.name.startswith('R157_TREE_'):bpy.data.objects.remove(o,do_unlink=True)
col=bpy.data.collections.new('R158_ACT_CANOPY_RECONSTRUCTION');s.collection.children.link(col)
vs=[];fs=[]
for o in s.objects:
 if o.type=='MESH' and (o.name in ('R152_CLASS2_TERRAIN','R154_FAR_GROUND','R154_FAR_ROADS') or o.name.startswith(('R152_PATH_','R152_FORECOURT_'))):
  o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in t.vertices) for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
bark=bpy.data.materials['R157_BARK'];leaf=bpy.data.materials.new('R158_LEAFY_BRANCH_CUTOUT');leaf.use_nodes=True;leaf.diffuse_color=(.2,.32,.1,1);leaf.use_backface_culling=False
nt=leaf.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.85;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures/R158_leafy_twig.png'));nt.links.new(tex.outputs['Color'],p.inputs['Base Color']);nt.links.new(tex.outputs['Alpha'],p.inputs['Alpha']);leaf.surface_render_method='DITHERED'
prototypes=[]
for seed in range(12):
 rng=random.Random(158+seed);vs=[];fs=[];slots=[];uvs=[]
 def branch(a,b,r0,r1):
  direction=(b-a).normalized();u=direction.cross(Vector((0,0,1)))
  if u.length<.01:u=Vector((1,0,0))
  u.normalize();v=direction.cross(u);off=len(vs);n=5
  vs.extend(tuple(q+rr*(math.cos(i*math.tau/n)*u+math.sin(i*math.tau/n)*v)) for q,rr in [(a,r0),(b,r1)] for i in range(n))
  for i in range(n):fs.append((off+i,off+(i+1)%n,off+(i+1)%n+n,off+i+n));slots.append(0);uvs.append([(0,0)]*4)
 trunk=Vector((rng.uniform(-.025,.025),rng.uniform(-.025,.025),.65));branch(Vector((0,0,0)),trunk,.014,.004);tips=[]
 for k in range(12):
  a=Vector((trunk.x*.5,trunk.y*.5,rng.uniform(.28,.58)));angle=k*2.39996+rng.uniform(-.4,.4);rad=rng.uniform(.18,.34);b=Vector((rad*.6*math.cos(angle),rad*.6*math.sin(angle),rng.uniform(.48,.75)));branch(a,b,.006,.0025)
  for j in (-1,1):
   ang=angle+j*.4;tip=Vector((rad*math.cos(ang),rad*math.sin(ang),rng.uniform(.58,.94)));branch(b,tip,.0025,.0006);tips.append(tip)
 for k in range(180 if seed<6 else 64):
  c=tips[k%len(tips)]+Vector((rng.gauss(0,.047),rng.gauss(0,.047),rng.gauss(0,.047)));ang=rng.random()*math.tau;u=Vector((math.cos(ang),math.sin(ang),rng.uniform(-.5,.5))).normalized();v=u.cross(Vector((rng.uniform(-.8,.8),rng.uniform(-.8,.8),1))).normalized();half=rng.uniform(.10,.145) if seed<6 else rng.uniform(.14,.20);off=len(vs);vs.extend(tuple(c+half*(u*x+v*y)) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]);fs.append((off,off+1,off+2,off+3));slots.append(1);uvs.append([(0,0),(1,0),(1,1),(0,1)])
 me=bpy.data.meshes.new(f'R158_CROWN_{seed}');me.from_pydata(vs,[],fs);me.materials.append(bark);me.materials.append(leaf);uv=me.uv_layers.new(name='UVMap')
 for poly,slot,coords in zip(me.polygons,slots,uvs):
  poly.material_index=slot;poly.use_smooth=slot==0
  for li,co in zip(poly.loop_indices,coords):uv.data[li].uv=co
 prototypes.append(me)
missing=[];made=[]
for i,t in enumerate(d['trees']):
 x,y=t['xy'];hit,normal,idx,dist=bvh.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),450)
 if hit is None:missing.append(t);continue
 o=bpy.data.objects.new(f'R158_TREE_{i:05d}',prototypes[i%6+(0 if t['near'] else 6)]);col.objects.link(o);o.location=(x,y,hit.z-.12);o.scale=(t['radius']/.40,t['radius']/.40,t['height']);o.rotation_euler.z=i*2.39996;o['source']=t['source'];o['level_id']='SITE_VEGETATION';made.append(o.name)
out=R/'scenes/MUDAM_R158_ACT_ORMAN_ORTUSU_v003.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for n in made:bpy.data.objects[n].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/vegetation.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
report={'scene':out.name,'trees':len(made),'source_tiles':d['source_tiles'],'source_canopy_area_m2':d['canopy_area_m2'],'missing_ground_count':len(missing),'prototype_count':12,'source_method':d['method'],'exact_individual_trees':False,'whole_context_complete':False,'terrain_buildings_roads_changed':False}
(R/'reports/R158_BUILD.json').write_text(json.dumps(report,indent=2));print('R158_SAVED',len(made),'MISSING',len(missing),flush=True)
