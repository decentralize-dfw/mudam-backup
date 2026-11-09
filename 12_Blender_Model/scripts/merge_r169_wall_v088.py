from pathlib import Path
import bpy
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_v087.blend'));name='ARCH_REAR_PROJECTION_WALL_0';bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
with bpy.data.libraries.load(str(R/'scenes/MUDAM_R169_MIMARI_DUVAR_UST_KESIM_v088.blend')) as (src,dst):dst.objects=[name]
bpy.context.collection.objects.link(dst.objects[0]);bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_v088.blend'))
