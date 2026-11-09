"""Reopen the dated pre-bake source with its external image paths relative to the checkout.

blender -b --factory-startup --disable-autoexec --python restore_prebake_sources.py -- --project-root <repo>
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
import bpy

parser = argparse.ArgumentParser()
parser.add_argument('--project-root', type=Path, default=Path(__file__).resolve().parents[2])
parser.add_argument('--manifest', type=Path)
parser.add_argument('--output', type=Path)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
root = args.project_root.resolve()
manifest_path = args.manifest or root / '12_Blender_Model/config/prebake_20261109_files.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
source = root / manifest['sourceScene']['path']
output = (args.output or source.with_name(source.stem + '_portable.blend')).resolve()
if output.exists() or output == source.resolve():
    raise FileExistsError(f'Choose a new output path for the portable copy: {output}')
def verify_file(record):
    path = (root / record['path']).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'Expected repository-relative input: {path}')
    if path.stat().st_size != record['bytes']:
        raise ValueError(f'Size mismatch: {path}')
    with path.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    if digest != record['sha256']:
        raise ValueError(f'SHA-256 mismatch: {path}')
    return path

verify_file(manifest['sourceScene'])
files = {name: verify_file(record) for record in manifest['externalFiles'] for name in record['imageDatablocks']}
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
output.parent.mkdir(parents=True, exist_ok=True)
for name, path in files.items():
    image = bpy.data.images[name]
    if image.packed_file or image.packed_files:
        raise ValueError(f'Expected external texture: {name}')
    image.filepath = '//' + os.path.relpath(path, output.parent).replace(os.sep, '/')
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True, relative_remap=False)
bpy.ops.wm.open_mainfile(filepath=str(output), load_ui=False, use_scripts=False)
for name, path in files.items():
    image = bpy.data.images[name]
    if not image.filepath.startswith('//') or Path(bpy.path.abspath(image.filepath)).resolve() != path:
        raise ValueError(f'Texture resolved outside its portable path: {name}')
    image.reload()
    if min(image.size) < 1:
        raise ValueError(f'Unable to decode the relocated texture: {name}')
print(f'PORTABLE_COPY_REOPENED {output}. Rebased and loaded {len(files)} image references across {len(set(files.values()))} distinct files.')

