import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R448_KALE_FOTOGRAF_MAZGAL_ACIKLIKLARI_ADAY_v001.blend'));bpy.ops.object.select_all(action='DESELECT');names=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and not o.hide_render and o.name.startswith(('R154_FORT_','R154_TOWER_','R154_ACORN_','R389_','R392_','R397_','R400_','R401_','R402_','R403_','R406_','R407_','R408_','R414_','R415_','R416_','R417_','R418_','R419_','R420_','R424_','R425_','R430_','R431_','R434_','R439_','R446_','R448_','R152_HISTORIC_WALL_51768377','R152_HISTORIC_WALL_92711484','R154_ENTRANCE_','R154_FRONT_WINDOW_')):o.select_set(True);names.append(o.name)
p=R/'exports/r152_clean/r448_fort_pavilion_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p));errors=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  bad=sum(not all(math.isfinite(x) for x in v.co) for v in o.data.vertices);zero=sum(f.area<1e-10 for f in o.data.polygons)
  if bad or zero:errors.append(dict(name=o.name,nonFinite=bad,zeroArea=zero))
(R/'reports/R448_GLB_ROUNDTRIP.json').write_text(json.dumps(dict(file=str(p),bytes=p.stat().st_size,objects=names,errors=errors,accepted=False,published=False),indent=2));assert not errors,errors
