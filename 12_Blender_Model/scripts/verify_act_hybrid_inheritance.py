"""Check the local tile replacement did not modify the inherited architecture."""
from pathlib import Path
import bpy,json,hashlib,array,sys
root=Path(__file__).resolve().parents[1]
def snapshot(file):
    bpy.ops.wm.open_mainfile(filepath=str(root/'scenes'/file))
    rows={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        h=hashlib.sha256()
        for collection,attribute,size,code in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_total',1,'i')]:
            values=array.array(code,[0])*(len(collection)*size);collection.foreach_get(attribute,values);h.update(values.tobytes())
        h.update(repr([[*v] for v in o.matrix_world]).encode())
        h.update(repr((o.hide_render,[m.name if m else None for m in o.data.materials])).encode())
        rows[o.name]=h.hexdigest()
    return rows
version='v011' if '--v011' in sys.argv else ('v010' if '--v010' in sys.argv else ('v009' if '--v009' in sys.argv else ('v008' if '--v008' in sys.argv else 'v005')))
old=snapshot('MUDAM_R151_ACT_CEVRE_ADAY_v005.blend' if version!='v005' else 'MUDAM_R151_ACT_CEVRE_ADAY_v002.blend')
new=snapshot(f'MUDAM_R151_ACT_CEVRE_ADAY_{version}.blend')
if version!='v005':assert set(new)-set(old)=={'R151_PAV_GROUND_JOIN'} and not set(old)-set(new)
else:assert old.keys()==new.keys()
changed=[n for n in old if old[n]!=new[n]]
assert changed
if version!='v005':
    registration=json.loads((root/'reports/R151_v007_registration_build.json').read_text());ground=json.loads((root/'reports/R151_v008_ground_join_build.json').read_text())
    allowed=set(registration['rigid_pavilion_objects']+registration['link_transition_objects']+ground['changed_walls'])
    if version in ('v010','v011'):allowed.add('P05_LINK_FLOOR')
else:
    assert all(n.startswith('R151_ACT_') for n in changed),changed
    allowed={'R151_ACT_'+Path(x['file']).stem for x in json.loads((root/'reports/ACT2020_museum_cut_candidate.json').read_text())['changes']}
assert set(changed)<=allowed
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()]
assert not missing,missing
result=dict(reopened=True,geometry_and_transform_scope=True,changed=changed,unchanged_meshes=len(old)-len(changed),inherited_architecture_unchanged=version=='v005',outside_declared_scope_unchanged=True,missing_images=missing,accepted=False,scope='Geometry, transform, material slot identities and render visibility preserved outside declared change scope; visual seam acceptance remains separate.')
(root/f'reports/R151_{version}_inherited_verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
