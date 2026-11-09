"""Separate web copy: distance-based context LOD, compact copied textures, layer GLBs."""
from pathlib import Path
import bpy,json,hashlib,subprocess,time
from mathutils import Vector
R=Path(__file__).resolve().parents[1];cache=R/'.local_source_cache/r151_web_lod';cache.mkdir(exist_ok=True)
source=R/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v011.blend';out=R/'scenes/MUDAM_R151_WEB_LOD_v001.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
for s in list(bpy.data.scenes):
 if s!=scene:bpy.data.scenes.remove(s)
for o in list(bpy.data.objects):
 if o.name not in scene.objects or (o.type=='MESH' and (o.hide_render or not o.visible_get())):bpy.data.objects.remove(o,do_unlink=True)
def triangles(o):o.data.calc_loop_triangles();return len(o.data.loop_triangles)
objects=[o for o in scene.objects if o.type=='MESH'];before={o.name:triangles(o) for o in objects}
context=[o for o in objects if o.name.startswith('R151_ACT_')];architecture=[o for o in objects if o not in context]
# Record image use before changing copied payloads. Highest demanded resolution wins.
uses={}
for o in objects:
 bounds=[o.matrix_world@Vector(c) for c in o.bound_box];distance=min((p.x*p.x+p.y*p.y)**.5 for p in bounds)
 cap=1024 if o not in context else (1024 if distance<90 else (512 if distance<220 else 256))
 for m in o.data.materials:
  if not m or not m.use_nodes:continue
  for node in m.node_tree.nodes:
   if node.type=='TEX_IMAGE' and node.image:uses[node.image]=max(cap,uses.get(node.image,0))
rows=[]
for i,(im,cap) in enumerate(uses.items()):
 if im.size[0]==0:continue
 original=bytes(im.packed_file.data) if im.packed_file else Path(bpy.path.abspath(im.filepath)).read_bytes()
 inp=cache/f'image_{i:04d}.source';inp.write_bytes(original)
 normal=im.colorspace_settings.name in ('Non-Color','Raw')
 # Non-colour and alpha payloads remain lossless PNG; colour photos use JPEG.
 jpeg=not normal and im.channels<4
 if im.name.startswith('Image_'):jpeg=True
 target=cache/f'image_{i:04d}{".jpg" if jpeg else ".png"}'
 rows.append(dict(name=im.name,input=str(inp),output=str(target),before_size=list(im.size),before_bytes=len(original),cap=min(cap,512) if normal else cap,jpeg=jpeg,colorspace=im.colorspace_settings.name))
manifest=cache/'textures.json';manifest.write_text(json.dumps(rows,indent=2))
subprocess.run(['C:/Users/yigit/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-X','utf8',str(R/'scripts/resize_web_textures.py'),str(manifest)],check=True)
rows=json.loads(manifest.read_text())
for r in rows:
 im=bpy.data.images[r['name']]
 if im.packed_file:im.unpack(method='REMOVE')
 im.filepath=r['output'];im.reload();im.colorspace_settings.name=r['colorspace'];im.pack()
changes=[]
for i,o in enumerate(objects):
 count=before[o.name];ratio=1
 if o in context:
  bounds=[o.matrix_world@Vector(c) for c in o.bound_box];distance=min((p.x*p.x+p.y*p.y)**.5 for p in bounds)
  ratio=.45 if distance<90 else (.2 if distance<220 else .1)
 elif count>1500 and any(x in o.name for x in ('RAIL','ROUND','BALUST')):ratio=.4
 if ratio==1:continue
 # Each tile owns its data; duplicate inherited rails before applying modifiers.
 if o.data.users>1:o.data=o.data.copy()
 bpy.context.view_layer.objects.active=o
 mod=o.modifiers.new('WEB_LOD','DECIMATE');mod.ratio=ratio;mod.use_collapse_triangulate=True
 bpy.ops.object.modifier_apply(modifier=mod.name)
 changes.append(dict(name=o.name,before=count,after=triangles(o),ratio=ratio))
 if i%50==0:print('LOD',i,len(objects),flush=True)
bpy.ops.outliner.orphans_purge(do_local_ids=True,do_linked_ids=False,do_recursive=True)
scene['web_lod_source']=source.name;scene['web_lod_scope']='Distance-based ACT context simplification. Architecture shell/openings preserved. Dense rails reduced separately. Original source untouched.'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(source=str(source),file=str(out),accepted=False,before_triangles=sum(before.values()),after_triangles=sum(triangles(o) for o in objects),context_before=sum(before[o.name] for o in context),context_after=sum(triangles(o) for o in context),architecture_before=sum(before[o.name] for o in architecture),architecture_after=sum(triangles(o) for o in architecture),changes=changes,textures=rows,texture_bytes_before=sum(r['before_bytes'] for r in rows),texture_bytes_after=sum(r['after_bytes'] for r in rows),blend_bytes=out.stat().st_size)
(R/'reports/R151_WEB_LOD_build.json').write_text(json.dumps(report,indent=2));print('WEB_LOD_SAVED',report['before_triangles'],report['after_triangles'],report['blend_bytes'],flush=True)
