from pathlib import Path
import bpy,bmesh,json,math,random,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r157/landscape.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R156_SCHUMAN_CEVRE_v002.blend'));s=bpy.context.scene
col=bpy.data.collections.new('R157_BRANCHING_WOODLAND');s.collection.children.link(col)
def plain(name,c,rough=.85):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;return m
soil=plain('R157_CONTINUOUS_LANDCOVER',(.2,.25,.12));nt=soil.node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures/R157_landcover_atlas.jpg'));tex.extension='EXTEND';nt.links.new(tex.outputs['Color'],p.inputs['Base Color'])
# Fine grain only. The old large-scale bump pattern is deliberately absent.
normal=nt.nodes.new('ShaderNodeTexImage');normal.image=bpy.data.images.load(str(R/'textures/R157_ground_micro_normal.png'));normal.image.colorspace_settings.name='Non-Color';normal.extension='REPEAT';uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='MicroUV';nt.links.new(uv.outputs['UV'],normal.inputs['Vector']);nm=nt.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.16;nt.links.new(normal.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],p.inputs['Normal'])
path=plain('R157_COMPACTED_MINERAL_PATH',(.34,.32,.26));road=plain('R157_MATTE_ASPHALT',(.105,.115,.12));paving=plain('R157_PALE_PAVING',(.36,.36,.33))
changed=[]
for row in d['updates']:
 o=bpy.data.objects[row['name']];assert len(o.data.vertices)==len(row['vertices'])
 for v,q in zip(o.data.vertices,row['vertices']):v.co=q
 o.data.update();o.data.materials.clear();isground=o.name in ('R152_CLASS2_TERRAIN','R154_FAR_GROUND')
 if isground:o.data.materials.append(soil)
 else:
  o.data.materials.append(paving if 'FORECOURT' in o.name else path);o.data.materials.append(road)
 for poly in o.data.polygons:
  poly.use_smooth=True
  if row['material_indices']:poly.material_index=row['material_indices'][poly.index]
 if isground:
  for l in list(o.data.uv_layers):o.data.uv_layers.remove(l)
  atlas=o.data.uv_layers.new(name='UVMap');micro=o.data.uv_layers.new(name='MicroUV');o.data.uv_layers.active=atlas
  for li,loop in enumerate(o.data.loops):
   q=o.data.vertices[loop.vertex_index].co;atlas.data[li].uv=((q.x+500)/1150,(q.y+450)/1100);micro.data[li].uv=(q.x/2,q.y/2)
 changed.append(o.name)
bark=plain('R157_BARK',(.105,.082,.055));leaves=[plain('R157_LEAF_'+str(i),c) for i,c in enumerate([(.065,.12,.028),(.11,.18,.040),(.16,.23,.067),(.085,.145,.043)])]
for m in leaves:
 m.use_backface_culling=False;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Subsurface Weight'].default_value=.025
prototypes=[]
for near in (False,True):
 for seed in range(4):
  rng=random.Random(157+seed+100*near);vs=[];fs=[];slots=[]
  def branch(a,b,r0,r1):
   delta=(b-a).normalized();u=delta.cross(Vector((0,0,1)))
   if u.length<.01:u=Vector((1,0,0))
   u.normalize();v=delta.cross(u);off=len(vs);n=6
   vs.extend([tuple(q+rr*(math.cos(i*math.tau/n)*u+math.sin(i*math.tau/n)*v)) for q,rr in [(a,r0),(b,r1)] for i in range(n)]);ff=[[off+i,off+(i+1)%n,off+(i+1)%n+n,off+i+n] for i in range(n)]+[list(range(off+n-1,off-1,-1)),list(range(off+n,off+2*n))];fs.extend(ff);slots.extend([0]*len(ff))
  trunk=Vector((rng.uniform(-.015,.015),rng.uniform(-.015,.015),.45));branch(Vector((0,0,0)),trunk,.013,.009);tips=[]
  for k in range(9):
   angle=k*math.tau/9+rng.uniform(-.3,.3);rad=rng.uniform(.13,.26);a=trunk* rng.uniform(.55,1);b=Vector((rad*.55*math.cos(angle),rad*.55*math.sin(angle),rng.uniform(.56,.74)));branch(a,b,.007,.004)
   for j in range(3):
    ang=angle+(j-1)*.55;tip=Vector((rad*math.cos(ang),rad*math.sin(ang),rng.uniform(.66,.98)));branch(b,tip,.0035,.0008);tips.append(tip)
  leafcount=2200 if near else 420
  for k in range(leafcount):
   c=tips[k%len(tips)]+Vector((rng.gauss(0,.058),rng.gauss(0,.058),rng.gauss(0,.052)));angle=rng.random()*math.tau;u=Vector((math.cos(angle),math.sin(angle),rng.uniform(-.35,.35))).normalized();v=u.cross(Vector((rng.uniform(-.5,.5),rng.uniform(-.5,.5),1))).normalized();length=rng.uniform(.010,.019) if near else rng.uniform(.027,.041);width=length*.5;off=len(vs)
   vs.extend([tuple(c-u*length),tuple(c-u*length*.25+v*width),tuple(c+u*length*.55+v*width*.6),tuple(c+u*length),tuple(c+u*length*.55-v*width*.6),tuple(c-u*length*.25-v*width)]);fs.extend([[off,off+1,off+2,off+3],[off,off+3,off+4,off+5]]);slots.extend([1+rng.randrange(4)]*2)
  me=bpy.data.meshes.new('R157_TREE_PROTOTYPE_'+str(near)+'_'+str(seed));me.from_pydata(vs,[],fs);me.update()
  for m in [bark]+leaves:me.materials.append(m)
  for f,slot in zip(me.polygons,slots):f.material_index=slot;f.use_smooth=slot==0
  prototypes.append(me)
for i,t in enumerate(d['trees']):
 o=bpy.data.objects.new('R157_TREE_'+str(i),prototypes[(4 if t['near'] else 0)+i%4]);col.objects.link(o);o.location=(*t['xy'],t['z']-.12);o.scale=(t['radius']/.30,t['radius']/.30,t['height']);o.rotation_euler.z=(i*2.39996)%math.tau;o['source']=t['source'];o['level_id']='SITE_VEGETATION';o['species']='representative broadleaf branching, not surveyed species'
# Preserve every building and fort mesh; only listed terrain meshes have changed.
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
for label,eye,target in [('near',(150,-210,110),(0,-10,0)),('park',(-145,-210,65),(-45,-45,-5)),('far',(650,-710,610),(55,75,-8))]:
 cam=s.camera;cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48;s.render.filepath=str(R/f'renders/qa/R157_{label}.png');bpy.ops.render.render(write_still=True)
out=R/'scenes/MUDAM_R157_ARAZI_YOLLAR_AGACLAR_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
for file,select in [('near_site',lambda o:o.name.startswith(('R152_','R154_')) or o.get('level_id')=='L00_APPROACH'),('vegetation',lambda o:o.name.startswith('R157_TREE_'))]:
 bpy.ops.object.select_all(action='DESELECT')
 for o in s.objects:
  if o.type=='MESH' and not o.hide_render and select(o):o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean'/f'{file}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
report=dict(scene=out.name,terrain_changes=[{k:v for k,v in x.items() if k not in ('vertices','material_indices')} for x in d['updates']],tree_instances=len(d['trees']),lidar_trees=sum(t['near'] for t in d['trees']),prototypes=len(prototypes),atlas_repeat=False,limits=d['limits'],accepted=False)
(R/'reports/R157_BUILD.json').write_text(json.dumps(report,indent=2));print('R157_SAVED',flush=True)
