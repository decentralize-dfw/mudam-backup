from pathlib import Path
import bpy
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_SIZINTI_KONTROL_v086.blend'));names=['ARCH_WALL_MASS_0']
for o in bpy.context.scene.objects:
 if any(o.name.startswith(p) for p in ['ARCH_REAR_GLAZING_','ARCH_REAR_FRAME_','ARCH_REAR_FRAME_H_']) and 'REVEAL' not in o.name:
  s=o.name.replace('ARCH_REAR_GLAZING_','').replace('ARCH_REAR_FRAME_H_','').replace('ARCH_REAR_FRAME_','')
  if int(s.split('_')[0])<4:names.append(o.name)
for name in names:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
for o in list(bpy.context.scene.objects):
 if o.name.startswith('ARCH_EAVE_STEP_END_'):bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str(R/'scenes/MUDAM_R169_MIMARI_CEPHE_SINIRI_v087.blend')) as (src,dst):dst.objects=names
for o in dst.objects:bpy.context.collection.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_BIRLESIK_v087.blend'))
