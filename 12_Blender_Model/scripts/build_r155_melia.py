from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r155/melia_facades.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R154_GENIS_ARAZI_KALE_v003.blend'))
s=bpy.context.scene;col=bpy.data.collections.new('R155_MELIA_CLEAN');s.collection.children.link(col)
def signature(o):
 return hashlib.sha256(str((tuple(o.matrix_world),[(tuple(v.co)) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
inherited={o.name:signature(o) for o in s.objects if o.type=='MESH'}
def mat(name,c,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
panels=[mat('R155_PANEL_'+str(i),c) for i,c in enumerate([(.12,.18,.20),(.20,.27,.29),(.30,.37,.38),(.40,.45,.43),(.54,.55,.48),(.66,.64,.54)])]
glass=mat('R155_GLAZING',(.055,.11,.14),.19,.4);frame=mat('R155_FRAMES',(.20,.24,.25),.4,.5);roofmat=mat('R155_METAL_ROOF',(.62,.66,.65),.4,.5);stone=mat('R155_PLINTH',(.30,.33,.32),.85)
batches={};ground=bpy.data.objects['R154_FAR_GROUND'];bvh=BVHTree.FromObject(ground,bpy.context.evaluated_depsgraph_get());contacts=[]
def height(x,y):
 p,n,i,dist=bvh.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),400)
 if p:return p.z
 # Road layer has holes in the grass mesh.
 ro=bpy.data.objects['R154_FAR_ROADS'];hit,p,n,i=ro.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),distance=400)
 if hit:return p.z
 raise RuntimeError('Missing ground below hotel '+str((x,y)))
def add(name,vs,fs,m):
 target=batches.setdefault(name,[[],[],m]);off=len(target[0]);target[0].extend(vs);target[1].extend([[i+off for i in f] for f in fs])
def box(name,a,b,z0,z1,depth,m):
 a=Vector(a);b=Vector(b);u=(b-a).normalized();n=Vector((u.y,-u.x));p=[a,b,b-n*depth,a-n*depth];vs=[(q.x,q.y,z) for z in (z0,z1) for q in p];add(name,vs,[[0,3,2,1],[4,5,6,7]]+[[i,(i+1)%4,(i+1)%4+4,i+4] for i in range(4)],m)
roof=d['roof'];base=d['base'];used=0
for side in d['sides']:
 a=Vector(side['a']);b=Vector(side['b']);delta=b-a;u=delta.normalized();out=Vector((u.y,-u.x));cols=side['columns'];w=delta.length/cols;h=(roof-base)/side['rows']
 # Per-side exposure normalization avoids treating the shaded facade as all glass.
 colors=sorted(sum(c['rgb'])/3 for c in side['cells'] if c['samples']);bright=colors[int(len(colors)*.85)]
 for cell in side['cells']:
  i,j=cell['i'],cell['j'];aa=a+u*(i*w);bb=aa+u*w;lo=base+j*h;hi=lo+h;c=cell['rgb'];lum=sum(c)/3/max(bright,.02)
  isglass=cell['samples']>0 and lum<.72 and c[2]>c[0]*.90
  mi=max(0,min(5,round(lum*5)))
  material=glass if isglass else panels[mi];name='R155_GLAZING' if isglass else 'R155_FACADE_PANELS_'+str(mi)
  box(name,aa+u*.025,bb-u*.025,lo+.025,hi-.025,.10,material)
  if isglass:used+=1
 # Dark recessed joints support all cells; segmented lower plinth follows the DTM.
 for i in range(cols+1):
  q=a+u*(i*w);box('R155_VERTICAL_JOINTS',q-u*.025-out*.03,q+u*.025-out*.03,base,roof,.06,frame)
 for j in range(side['rows']+1):box('R155_HORIZONTAL_JOINTS',a-out*.03,b-out*.03,base+j*h-.025,base+j*h+.025,.06,frame)
 for i in range(cols):
  aa=a+u*i*w;bb=aa+u*w;ha=height(*aa);hb=height(*bb);contacts.extend([ha,hb]);low=min(ha,hb)-.3
  box('R155_GROUND_PLINTH',aa,bb,low,max(base+.03,ha+.03,hb+.03),.28,stone)
 box('R155_ROOF_PARAPET',a,b,roof,roof+.30,.22,roofmat)
xy=d['footprint'];add('R155_ROOF',[(x,y,roof-.04) for x,y in xy],[list(range(len(xy)))],roofmat)
# Roof circular equipment locations traced from the downloaded overhead reference.
for px,py in [(943,360),(948,405),(958,455),(1056,946),(1018,998),(1074,1038),(1083,1080),(780,1078),(733,1075)]:
 x=127+(px-700)*75/1400;y=49-(py-700)*75/1400;n=16;r=.45;vs=[(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),z) for z in (roof,roof+.28) for i in range(n)];add('R155_ROOF_CIRCULAR_EQUIPMENT',vs,[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]+[list(range(n,2*n))],frame)
for name,(vs,fs,m) in batches.items():
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(m);o['source']=d['source'];o['level_id']='SITE_MELIA';o['status']='source_based_context_candidate'
errors=[o.name for o in col.objects if any(p.area<1e-9 for p in o.data.polygons)]
assert not errors,errors
assert all(signature(bpy.data.objects[n])==h for n,h in inherited.items())
s.cycles.samples=16;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
for label,eye,target in [('melia',(205,-60,62),(127,49,19)),('site',(210,-200,145),(20,40,10))]:
 cam=s.camera;cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48;s.render.filepath=str(R/f'renders/qa/R155_{label}.png');bpy.ops.render.render(write_still=True)
out=R/'scenes/MUDAM_R155_MELIA_CEVRE_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/melia.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
report=dict(scene=out.name,objects=len(col.objects),triangles=sum(len(p.vertices)-2 for o in col.objects for p in o.data.polygons),sampled_cells=d['sampled_cells'],glass_cells=used,ground_boundary_samples=len(contacts),ground_range=[min(contacts),max(contacts)],museum_and_terrain_unchanged=True,zero_area_objects=errors,limits=['Facade grid approximate; colors sampled from ACT and exposure-normalized per side.','Glazing classification is a context interpretation, not a measured window schedule.','Roof altitude inferred from ACT; 32m height from OSM.','Entrances hidden by vegetation remain unresolved.'],inherited_signatures=inherited)
(R/'reports/R155_BUILD.json').write_text(json.dumps(report,indent=2));print('R155_SAVED',len(col.objects),flush=True)
