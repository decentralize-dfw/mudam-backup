import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R430_ON_HENDEK_YAKLASIM_ZEMINI_ADAY_v001.blend'))
f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());z=f['deck_z'];a=Vector((*f['deck_start'],z));b=Vector((*f['deck_end'],z));axis=(b-a).normalized();side=Vector((-axis.y,axis.x,0));length=(b-a).length
names=[]
def mat(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
metal=mat('R431_BRIDGE_DARK_STEEL',(.105,.115,.105),.7,.46);wood=mat('R431_BRIDGE_WEATHERED_TIMBER',(.27,.235,.17),0,.86)
def box(name,x0,x1,y0,y1,z0,z1,ma):
 vs=[tuple(a+axis*x+side*y+Vector((0,0,zz))) for zz in [z0,z1] for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(ma);o['level_id']='SITE';names.append(name);return o
old=bpy.data.objects['R154_FORT_ENTRANCE_BRIDGE'];old.hide_render=True;old.hide_viewport=True;old.hide_set(True)
# Preserve measured existing bridge footprint and deck level. Separate beams and independent transverse boards.
box('R431_BRIDGE_STRUCTURAL_DECK',0,length,-1.2,1.2,-.30,-.075,metal)
count=math.ceil(length/.20)
for i in range(count):box('R431_BRIDGE_BOARD_%03d'%i,i*length/count+.003,(i+1)*length/count-.003,-1.2,1.2,-.075,0,wood)
# Photographed flat steel parapets with framed translucent-looking fine mesh infill.
# Use sparse explicit fine bars (no source photo texture), instead of opaque panels.
start=.12;end=length-.65;panels=math.ceil((end-start)/1.65)
for sign in [-1,1]:
 y=sign*1.14
 for k in range(panels+1):
  x=start+(end-start)*k/panels;box('R431_BRIDGE_POST_%d_%02d'%(sign,k),x-.025,x+.025,y-.025,y+.025,-.08,1.04,metal)
 box('R431_BRIDGE_HANDRAIL_%d'%sign,start-.04,end+.04,y-.04,y+.04,.995,1.045,metal)
 box('R431_BRIDGE_BOTTOMRAIL_%d'%sign,start,end,y-.018,y+.018,.10,.135,metal)
 for k in range(1,panels*18):
  x=start+(end-start)*k/(panels*18);box('R431_BRIDGE_INFILL_%d_%03d'%(sign,k),x-.004,x+.004,y-.006,y+.006,.135,.995,metal)
# Join components by material to avoid hundreds of runtime draw calls.
for label,ma in [('STEEL',metal),('TIMBER',wood)]:
 bpy.ops.object.select_all(action='DESELECT');obs=[bpy.data.objects[n] for n in names if bpy.data.objects.get(n) and bpy.data.objects[n].data.materials[0]==ma]
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name='R431_FORT_BRIDGE_'+label;obs[0]['source']='R423_68151060 photograph confirms timber deck and metal guards; inherited bridge footprint and elevation preserved. Guard1.04m and member sizes photo estimates, not surveyed.'
out=R/'scenes/MUDAM_R431_KALE_KOPRUSU_AHSAP_KORKULUK_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in ['R431_FORT_BRIDGE_STEEL','R431_FORT_BRIDGE_TIMBER']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(not x['nonManifold'] and not x['zeroArea'] for x in checks)
(R/'reports/R431_BRIDGE_BUILD.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,checks=checks,deckElevation=z,length=length,width=2.4,source='references/fort_inpa/R423_68151060.jpg',limitations=['Photograph supports timber/metal system; exact rail height, spacing, infill construction not surveyed.','Geometry remains candidate until same-camera visual comparison.']),indent=2));print('R431_SAVED',flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(-107,-92,6));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-63,-54,1.7))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=50;s.render.filepath=str(R/'renders/qa/R431_front_candidate.png');bpy.ops.render.render(write_still=True)
