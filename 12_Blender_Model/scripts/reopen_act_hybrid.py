"""Read-only independent reopening of the combined scene."""
from pathlib import Path
import bpy, json, sys
root = Path(__file__).resolve().parents[1]
version = 'v003' if '--v003' in sys.argv else 'v002'
path = root / f'scenes/MUDAM_R151_ACT_CEVRE_ADAY_{version}.blend'
bpy.ops.wm.open_mainfile(filepath=str(path))
scene = bpy.context.scene
context = [o for o in scene.objects if o.type == 'MESH' and o.name.startswith('R151_ACT_')]
architecture = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render and not o.name.startswith('R151_ACT_')]
missing = [im.name for im in bpy.data.images if im.source == 'FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
assert len(context) == 851 and architecture and not missing, (len(context), len(architecture), missing)
receipt = dict(file=str(path), reopened=True, context_meshes=len(context), visible_architecture_meshes=len(architecture), missing_images=missing, accepted=False, remaining=['Ground gaps beneath bridge and along museum cut must be resolved before production acceptance.'])
(root / f'reports/R151_{version}_reopen_verification.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps(receipt))
