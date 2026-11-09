"""Replace only the sixteen locally cut tiles; preserve the rest of the hybrid."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
version='v006' if '--v006' in sys.argv else ('v005' if '--v005' in sys.argv else 'v003')
out=root/f'scenes/MUDAM_R151_ACT_CEVRE_ADAY_{version}.blend'
assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(root/('scenes/MUDAM_R151_ACT_CEVRE_ADAY_v005.blend' if version=='v006' else 'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v002.blend')))
cut=json.loads((root/'reports/ACT2020_museum_cut_candidate.json').read_text())
assert cut['clipped_directory']=='clipped_glb_'+version
col=bpy.data.collections['R151_ACT2020_PHOTOGRAMMETRY_CANDIDATE']
changes=[]
for row in cut['changes']:
    if version=='v006' and row['file']!='Tile-125-98-1-1_m-00107.glb':continue
    name='R151_ACT_'+Path(row['file']).stem
    old=bpy.data.objects.get(name)
    if row['empty']:
        assert old is None
        continue
    assert old
    bpy.data.objects.remove(old,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(root/'.local_source_cache/act_context'/cut['clipped_directory']/row['file']))
    for obj in list(bpy.context.selected_objects):
        if obj.type!='MESH':continue
        obj.name=name
        for parent in list(obj.users_collection):parent.objects.unlink(obj)
        col.objects.link(obj)
        obj['source_ids']='ACT_MESH3D_2020_CC0'
        obj['status']='candidate_ground_preservation'
        for mat in obj.data.materials:
            if hasattr(mat.cycles,'emission_sampling'):mat.cycles.emission_sampling='NONE'
    changes.append(name)
scene=bpy.context.scene;cam=scene.camera
cam.location=(92,-130,120);cam.rotation_euler=(Vector((0,5,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48
scene.render.filepath=str(root/f'renders/qa/R151_{version}_candidate_museum.png')
bpy.ops.render.render(write_still=True)
if version=='v006':
    cam.location=(45,-44,4);cam.rotation_euler=(Vector((29,-43,-7))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=28
    scene.render.filepath=str(root/'renders/qa/R151_v006_ground_seam.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(root/f'reports/R151_{version}_ground_restore_candidate.json').write_text(json.dumps(dict(file=str(out),changed_tiles=changes,accepted=False,method=('Preserve original source lower base below inherited R17 wall bottom' if version=='v006' else ('Actual concave bridge boundary and LiDAR-matched original source ground' if version=='v005' else 'Preserve original source triangles below road-relative -1m with ground-like slope; candidate classification requires visual review.'))),indent=2))
print('R151_'+version+'_SAVED',flush=True)
