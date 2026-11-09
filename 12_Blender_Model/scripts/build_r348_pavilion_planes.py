import bpy,bmesh,json,math,ast
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R334_HENDEK_CAKISMA_TEMIZLIK_ADAY_v001.blend'))
data={k:v for k,v in json.loads((R/'reports/R347_PAVILION_PLANES.json').read_text()).items() if v.get('valid')};regions=[];records=[]
for row in data.values():
 poly=row['outline']
 for face in tessellate_polygon([[Vector((x,y,0)) for x,y in poly]]):regions.append([poly[i] if isinstance(i,int) else (i.x,i.y) for i in face])
# Reuse the already verified attribute-preserving polygon clipper, executing
# only its function and terrain loop, never the other candidate's workflow.
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text())
clip=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='clip')
loop=next(n for n in source.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='ob')
code=ast.unparse(loop).replace("ob.name not in ['R152_CLASS2_TERRAIN']","not (ob.name == 'R152_CLASS2_TERRAIN' or ob.name.startswith('R152_PATH_'))")
exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));exec(compile(code,'<terrain and path cut>','exec'))
m=bpy.data.materials.new('R348_RUIN_MINERAL_FLOOR');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.23,.215,.18,1);p.inputs['Roughness'].default_value=.94
normal=R/'textures/R157_ground_micro_normal.png'
if normal.exists():
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(normal),check_existing=True);t.image.colorspace_settings.name='Non-Color';n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.2;m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
new=[]
for label,row in data.items():
 xy=row['outline'];a,b,c=row['plane'];n=len(xy);vs=[(x,y,a*x+b*y+c+dz) for dz in [-.15,0] for x,y in xy];faces=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 name='R348_'+label.upper()+'_RUIN_FLOOR';me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(m)
 if label=='pavilion_west':
  grass=bpy.data.objects['R152_CLASS2_TERRAIN'].data.materials[0];me.materials[0]=grass
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
 for l in me.loops:
  v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x/2,v.y/2)
 o['level_id']='SITE';o['source']='Independent planar chamber floor fitted to ACT2024 classified laser returns; source plan independently reconstructed; no scanned mesh faces.';new.append(name)
out=R/'scenes/MUDAM_R348_PAVYON_KADEMELERI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
checks=[]
for name in new:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
bpy.ops.object.select_all(action='DESELECT')
for name in new+[r['name'] for r in records]:bpy.data.objects[name].select_set(True)
glb=R/'exports/r152_clean/r348_outer_moats_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('R348_Check');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
for label,x,y,scale in [('pavilion',32,-50,75)]:
 bpy.ops.object.camera_add(location=(x,y,70));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((x,y,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=scale;s.render.filepath=str(R/f'renders/qa/R348_{label}_ruin.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));roundtrip=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':roundtrip.append(dict(name=o.name,nonFinite=sum(not all(math.isfinite(x) for x in v.co) for v in o.data.vertices),zeroArea=sum(p.area<1e-10 for p in o.data.polygons)))
(R/'reports/R348_RUIN_FLOORS.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,planes=data,clipped=records,meshChecks=checks,glbChecks=roundtrip,limits=['Two separately measured pavilion ground/terrace planes applied; east lawn failed held-out maximum residual and is unchanged.','Coping, court boundary and pavilion remain unresolved; not whole-ring acceptance.']),indent=2));print('R348_READY',checks,roundtrip)
