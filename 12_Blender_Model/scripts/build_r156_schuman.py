from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r156/schuman_clean.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R155_MELIA_CEVRE_v002.blend'))
s=bpy.context.scene;col=bpy.data.collections.new('R156_SCHUMAN_CLEAN');s.collection.children.link(col)
def signature(o):
 return hashlib.sha256(str((tuple(o.matrix_world),[(tuple(v.co)) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
inherited={o.name:signature(o) for o in s.objects if o.type=='MESH'}
def mat(name,c,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
panels=[mat('R156_PANEL_'+str(i),c) for i,c in enumerate([(.12,.18,.20),(.20,.27,.29),(.30,.37,.38),(.40,.45,.43),(.54,.55,.48),(.66,.64,.54)])]
glass=mat('R156_GLAZING',(.055,.11,.14),.19,.4);frame=mat('R156_FRAMES',(.20,.24,.25),.4,.5);roofmat=mat('R156_METAL_ROOF',(.18,.22,.24),.75,.15);stone=mat('R156_PLINTH',(.30,.33,.32),.85)
batches={};ground=bpy.data.objects['R154_FAR_GROUND'];bvh=BVHTree.FromObject(ground,bpy.context.evaluated_depsgraph_get());contacts=[]
def height(x,y):
 heights=[]
 for o in s.objects:
  if o.type!='MESH' or not (o.name.startswith(('R154_FAR_GROUND','R154_FAR_ROADS','R152_CLASS2_TERRAIN','R152_PATH_','R152_FORECOURT_'))):continue
  hit,p,n,i=o.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),distance=400)
  if hit:heights.append(p.z)
 if not heights:raise RuntimeError('No terrain at '+str((x,y)))
 return max(heights)
def add(name,vs,fs,m):
 target=batches.setdefault(name,[[],[],m]);off=len(target[0]);target[0].extend(vs);target[1].extend([[i+off for i in f] for f in fs])
def box(name,a,b,z0,z1,depth,m):
 a=Vector(a);b=Vector(b);u=(b-a).normalized();n=Vector((u.y,-u.x));p=[a,b,b-n*depth,a-n*depth];vs=[(q.x,q.y,z) for z in (z0,z1) for q in p];add(name,vs,[[0,3,2,1],[4,5,6,7]]+[[i,(i+1)%4,(i+1)%4+4,i+4] for i in range(4)],m)

roof=d['roof'];base=d['base'];levels=d['levels'];floorh=31/levels;stone=mat('R156_LIMESTONE',(.56,.54,.47),.8);windowcount=0
for ringnum,path in enumerate(d['rings']):
 for a,b in zip(path,path[1:]+path[:1]):
  a=Vector(a);b=Vector(b);u=(b-a).normalized();out=Vector((u.y,-u.x));length=(b-a).length;n=max(1,round(length/1.65));w=length/n
  for i in range(n):
   aa=a+u*i*w;bb=aa+u*w
   # Real recessed glazed openings separated by stone piers and spandrels.
   for j in range(levels):
    lo=base+j*floorh;hi=lo+floorh;win0=lo+.85;win1=hi-.40
    box('R156_STONE_PIERS',aa,aa+u*.24,lo,hi,.34,stone)
    box('R156_SPANDREL',aa+u*.24,bb,lo,win0,.34,stone)
    box('R156_LINTELS',aa+u*.24,bb,win1,hi,.34,stone)
    l=aa+u*.24-out*.16;r=bb-out*.16
    box('R156_WINDOWS',l+u*.06,r-u*.06,win0+.06,win1-.06,.07,glass)
    box('R156_WINDOW_SILLS',l,r,win0,win0+.06,.10,frame)
    box('R156_WINDOW_HEADS',l,r,win1-.06,win1,.10,frame)
    box('R156_WINDOW_JAMBS',l,l+u*.06,win0,win1,.10,frame)
    box('R156_WINDOW_JAMBS',r-u*.06,r,win0,win1,.10,frame);windowcount+=1
   ha=height(*aa);hb=height(*bb);contacts.extend([ha,hb]);box('R156_GROUND_PLINTH',aa,bb,min(ha,hb)-.25,max(base+.05,ha+.05,hb+.05),.40,stone)
  box('R156_PARAPETS',a,b,roof,roof+.45,.35,stone)
  box('R156_CORNICE',a+out*.12,b+out*.12,roof-.24,roof,.50,stone)
for tri in d['roof_triangles']:add('R156_ROOF',[(x,y,roof-.08) for x,y in tri],[[0,1,2]],roofmat)
for room in d['rooftop_rooms']:
 path=room['xy'];z=room['z']
 for a,b in zip(path,path[1:]+path[:1]):box('R156_ROOFTOP_ROOM_WALLS',a,b,roof-.08,z,.22,stone)
 for t in room['triangles']:add('R156_ROOFTOP_ROOM_CAPS',[(x,y,z) for x,y in t],[[0,1,2]],roofmat)
# Roof courtyards remain open; no cap spans either inner ring.
for name,(vs,fs,m) in batches.items():
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(m);o['source']=d['source'];o['level_id']='SITE_SCHUMAN';o['status']='source_based_context_candidate'
errors=[o.name for o in col.objects if any(p.area<1e-9 for p in o.data.polygons)]
assert not errors,errors
assert all(signature(bpy.data.objects[n])==h for n,h in inherited.items())
s.cycles.samples=16;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
for label,eye,target in [('schuman',(230,10,105),(90,142,22)),('site',(245,-205,165),(30,75,12))]:
 cam=s.camera;cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48;s.render.filepath=str(R/f'renders/qa/R156_{label}.png');bpy.ops.render.render(write_still=True)
out=R/'scenes/MUDAM_R156_SCHUMAN_CEVRE_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/schuman.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
report=dict(scene=out.name,objects=len(col.objects),triangles=sum(len(p.vertices)-2 for o in col.objects for p in o.data.polygons),window_bays=windowcount,courtyards=2,ground_boundary_samples=len(contacts),ground_range=[min(contacts),max(contacts)],museum_and_terrain_unchanged=True,zero_area_objects=errors,limits=['OSM 31m height and nine levels retained; roof altitude estimated from ACT.','Window bay width and reveal depths interpreted from ACT facade, not measured.','Entrance geometry unresolved; three rooftop volumes traced from ACT, heights sampled.'],inherited_signatures=inherited)
(R/'reports/R156_BUILD.json').write_text(json.dumps(report,indent=2));print('R156_SAVED',len(col.objects),flush=True)

