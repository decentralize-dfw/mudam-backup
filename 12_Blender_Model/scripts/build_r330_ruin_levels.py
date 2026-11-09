import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R328_KALINTI_LIDAR_TABAN_ADAY_v001.blend'))
data=json.loads((R/'reports/R330_RUIN_ELEMENT_PLANES.json').read_text());changes=[]
for name,row in data.items():
 if not row['accepted']:continue
 o=bpy.data.objects[name];a,b,c=row['plane'];old=[v.co.z for v in o.data.vertices];top=max(old);count=0
 for v in o.data.vertices:
  if 'COURT' in name and abs(v.co.z-top)<.001:v.co.z=a*v.co.x+b*v.co.y+c
  elif abs(v.co.z-top)<.001:v.co.z=a*v.co.x+b*v.co.y+c
  else:continue
  count+=1
 o.data.update();o['source']='Independent architectural plane fitted to stable classified ACT2024 cells; held-out residuals in R330_RUIN_ELEMENT_PLANES.json. No scan mesh transferred.'
 changes.append(dict(name=name,vertices=count,previousTop=top,newMin=min(v.co.z for v in o.data.vertices),newMax=max(v.co.z for v in o.data.vertices),heldOutRMS=row['rms']))
out=R/'scenes/MUDAM_R330_KALINTI_KOTLARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
checks=[]
for row in changes:
 o=bpy.data.objects[row['name']];bm=bmesh.new();bm.from_mesh(o.data);checks.append(dict(name=o.name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
bpy.ops.object.select_all(action='DESELECT')
for row in changes:bpy.data.objects[row['name']].select_set(True)
glb=R/'exports/r152_clean/r330_ruin_levels_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
for label,x,y,scale in [('north',-35,68,44),('east',60,-30,42)]:
 bpy.ops.object.camera_add(location=(x,y,70));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((x,y,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=scale;s.render.filepath=str(R/f'renders/qa/R330_{label}_ruin.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));roundtrip=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':roundtrip.append(dict(name=o.name,nonFinite=sum(not all(math.isfinite(x) for x in v.co) for v in o.data.vertices),zeroArea=sum(p.area<1e-10 for p in o.data.polygons)))
(R/'reports/R330_LEVEL_BUILD.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changes=changes,meshChecks=checks,glbChecks=roundtrip,limits=['Only two locally supported plane fits applied; remaining coping and moat domains unresolved.','Raised court boundary must be reconciled with surrounding coping before acceptance.']),indent=2));print('R330_READY',changes,checks)
