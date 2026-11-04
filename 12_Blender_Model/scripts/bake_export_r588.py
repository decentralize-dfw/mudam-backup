"""R588 local contact-AO/export. Run only after the selected geometry revision passes local geometry QA.

This script writes local review artifacts only; it never publishes or edits release config.
"""
import bpy
import hashlib
import json
import math
import re
import sys
from pathlib import Path
import numpy as np
from mathutils import Vector

R = Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SOURCE = R / 'scenes' / (args[0] if args else 'MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v020.blend')
OUTPUT = R / 'scenes' / (args[1] if len(args)>1 else 'R588_BATI_TERAS_TEMAS_AO_ADAY_v004.blend')
IMAGE = R / 'textures/R588_west_terrace_contact_ao.png'
GLB = R / 'exports/r152_clean/r588_near_REVIEW.glb'
UV_NAME = 'R588_WEST_CONTACT_AO_ATLAS'
TARGET_NAMES = [
    'R588_WEST_APRON_AND_RETAINING_BODY',
    'R588_WEST_CLASS2_GROUND_RESTORATION',
    'R322_WEST_MUSEUM_TERRACE', 'R321_MUSEUM_WEST_MOAT_RETAINING',
    'R490_NW_MINERAL_PASSAGE', 'R152_HISTORIC_WALL_759680904',
    'R523_WEST_MOAT_LOWER_GROUND_0',
    'R552_WEST_SLOPING_MASONRY_PLINTH',
    'R549_WEST_GLASS_EXTERNAL_GROUND_0', 'R549_WEST_GLASS_EXTERNAL_GROUND_1',
    'R588_WEST_GLASS_CORNER_GROUND',
    'R546_WEST_MOAT_EDGE_1',
]


def geom_sig(obj):
    mesh = obj.data
    points = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    loops = np.empty(len(mesh.loops), dtype=np.int32)
    starts = np.empty(len(mesh.polygons), dtype=np.int32)
    totals = np.empty(len(mesh.polygons), dtype=np.int32)
    mesh.vertices.foreach_get('co', points)
    mesh.loops.foreach_get('vertex_index', loops)
    mesh.polygons.foreach_get('loop_start', starts)
    mesh.polygons.foreach_get('loop_total', totals)
    world = np.asarray(obj.matrix_world, dtype=np.float64)
    return hashlib.sha256(points.tobytes() + loops.tobytes() + starts.tobytes()
                          + totals.tobytes() + world.tobytes()).hexdigest()


def uv_sig(layer):
    values = np.empty(len(layer.data) * 2, dtype=np.float32)
    layer.data.foreach_get('uv', values)
    return hashlib.sha256(values.tobytes()).hexdigest()


def write_report(name, value):
    (R / 'reports' / name).write_text(json.dumps(value, indent=2), encoding='utf-8')


def connected_uv_names(material, mesh):
    """UV dependencies reachable from rendered shader outputs, including groups.

    Old glTF-only occlusion groups have already been removed from copied
    materials. Orphan AO textures therefore do not falsely retain stale UVs.
    Group-input dependencies are followed back into their calling material.
    """
    if not material or not material.use_nodes or not material.node_tree:
        return set()
    used, seen = set(), set()
    render_uv = next((u.name for u in mesh.uv_layers if u.active_render),
                     mesh.uv_layers[0].name if len(mesh.uv_layers) else None)

    def remember(name):
        name = name or render_uv
        if name:
            used.add(name)

    def follow_input(socket, context):
        for link in socket.links:
            walk(link.from_node, link.from_socket.name, context)

    def walk(node, output_name, context):
        key = (node.as_pointer(), output_name, tuple(n.as_pointer() for n in context))
        if key in seen:
            return
        seen.add(key)
        if node.type == 'GROUP_INPUT':
            if context:
                parent = context[-1]
                socket = parent.inputs.get(output_name)
                if socket:
                    follow_input(socket, context[:-1])
            return
        if node.type == 'GROUP' and node.node_tree:
            outputs = [n for n in node.node_tree.nodes if n.type == 'GROUP_OUTPUT']
            active = [n for n in outputs if getattr(n, 'is_active_output', False)]
            for out in active or outputs:
                socket = out.inputs.get(output_name)
                if socket:
                    follow_input(socket, context + (node,))
            return
        if node.type == 'UVMAP':
            remember(node.uv_map)
        elif node.type == 'NORMAL_MAP' and node.space == 'TANGENT':
            remember(node.uv_map)
        elif node.type == 'TANGENT' and node.direction_type == 'UV_MAP':
            remember(node.uv_map)
        elif node.type == 'TEX_COORD' and output_name == 'UV':
            remember(None)
        elif node.type == 'TEX_IMAGE' and not node.inputs['Vector'].is_linked:
            remember(None)
        elif node.type == 'ATTRIBUTE' and node.attribute_name in mesh.uv_layers:
            remember(node.attribute_name)
        for socket in node.inputs:
            follow_input(socket, context)

    outputs = [n for n in material.node_tree.nodes if n.type == 'OUTPUT_MATERIAL']
    active = [n for n in outputs if getattr(n, 'is_active_output', False)]
    for out in active or outputs:
        for socket in out.inputs:
            follow_input(socket, ())
    return used


assert SOURCE.is_file(), SOURCE
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
original = bpy.context.scene
before = {o.name: geom_sig(o) for o in original.objects if o.type == 'MESH'}
targets, skipped = [], []
for name in TARGET_NAMES:
    obj = original.objects.get(name)
    if obj is None or obj.type != 'MESH' or obj.hide_render or not len(obj.data.polygons):
        skipped.append(name)
        continue
    if obj.data.users > 1:
        obj.data = obj.data.copy()
    assert UV_NAME not in obj.data.uv_layers, 'Refusing repeated AO on ' + name
    targets.append(obj)
assert {'R588_WEST_APRON_AND_RETAINING_BODY', 'R588_WEST_CLASS2_GROUND_RESTORATION'} <= {o.name for o in targets}
old_uvs = {o.name: {u.name: uv_sig(u) for u in o.data.uv_layers} for o in targets}

# Copy before removing export-only AO groups: target materials may be shared
# with the museum or other context objects that must remain unchanged.
copies, removed_groups = {}, []
for obj in targets:
    for index, old_material in enumerate(obj.data.materials):
        if old_material is None:
            continue
        if old_material.name not in copies:
            copied = old_material.copy()
            copied.name = old_material.name + '_R588_AO'
            copied.use_nodes = True
            for node in list(copied.node_tree.nodes):
                if node.type == 'GROUP' and node.node_tree and 'glTF Material Output' in node.node_tree.name:
                    removed_groups.append({'material': copied.name, 'group': node.node_tree.name})
                    copied.node_tree.nodes.remove(node)
            copies[old_material.name] = copied
        obj.data.materials[index] = copies[old_material.name]

removed_uvs, used_uvs, retained_uvs = [], {}, {}
for obj in targets:
    mesh = obj.data
    used = set().union(*(connected_uv_names(m, mesh) for m in mesh.materials if m))
    assert used <= set(mesh.uv_layers.keys()), (obj.name, 'Missing material UV dependency', sorted(used))
    used_uvs[obj.name] = {name: old_uvs[obj.name][name] for name in sorted(used)}
    # Blender permits at most eight UV layers. Remove the minimum number of
    # unused sets needed for the single new AO layer, preferring stale AO sets.
    candidates = [u.name for u in mesh.uv_layers if u.name not in used]
    candidates.sort(key=lambda name: (0 if re.search(r'AO|LIGHTMAP|ATLAS', name, re.I) else 1,
                                      1 if name in ('UVMap', 'MicroUV') else 0, name))
    while len(mesh.uv_layers) >= 8:
        assert candidates, (obj.name, 'Eight material-used UV layers; cannot safely add AO')
        name = candidates.pop(0)
        removed_uvs.append({'object': obj.name, 'name': name, 'sha256': old_uvs[obj.name][name],
                            'reason': 'Unused by connected rendered material after copied old glTF AO groups removed'})
        mesh.uv_layers.remove(mesh.uv_layers[name])
    retained_uvs[obj.name] = {u.name: uv_sig(u) for u in mesh.uv_layers}
    for name, digest in used_uvs[obj.name].items():
        assert uv_sig(mesh.uv_layers[name]) == digest, (obj.name, name)
    assert len(mesh.uv_layers) <= 7
target_names = {o.name for o in targets}
verts, faces, loop_map = [], [], []
for obj in targets:
    offset = len(verts)
    verts.extend(obj.matrix_world @ vertex.co for vertex in obj.data.vertices)
    faces.extend(tuple(offset + i for i in p.vertices) for p in obj.data.polygons)
    loop_map.extend((obj.name, loop.index) for loop in obj.data.loops)

bake_scene = bpy.data.scenes.new('R588_TEMP_CONTACT_AO_BAKE')
bpy.context.window.scene = bake_scene
atlas = bpy.data.meshes.new('R588_TEMP_CONTACT_AO_ATLAS')
atlas.from_pydata(verts, [], faces)
atlas.update()
assert len(atlas.loops) == len(loop_map)
bake_object = bpy.data.objects.new(atlas.name, atlas)
bake_scene.collection.objects.link(bake_object)
occluders = []
target_bounds = []
for target in targets:
    pts = [target.matrix_world @ Vector(v) for v in target.bound_box]
    target_bounds.append(([min(p[k] for p in pts)-3 for k in range(3)],
                          [max(p[k] for p in pts)+3 for k in range(3)]))
for obj in original.objects:
    if obj.type != 'MESH' or obj.hide_render or obj.name in target_names or not len(obj.data.polygons):
        continue
    if obj.name.startswith('R158_TREE_'):
        continue
    bb = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    if not any(all(max(v[k] for v in bb)>=lo[k] and min(v[k] for v in bb)<=hi[k]
                   for k in range(3)) for lo,hi in target_bounds):
        continue
    bake_scene.collection.objects.link(obj)
    occluders.append(obj.name)

for obj in bake_scene.objects:
    obj.select_set(False)
bpy.context.view_layer.objects.active = bake_object
bake_object.select_set(True)
atlas.uv_layers.new(name=UV_NAME)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=.004)
bpy.ops.object.mode_set(mode='OBJECT')
image = bpy.data.images.new('R588_WEST_TERRACE_CONTACT_AO', width=2048, height=2048, alpha=False)
image.colorspace_settings.name = 'Non-Color'
material = bpy.data.materials.new('R588_TEMP_AO_SHADER')
material.use_nodes = True
nodes, links = material.node_tree.nodes, material.node_tree.links
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
emission = nodes.new('ShaderNodeEmission')
ao = nodes.new('ShaderNodeAmbientOcclusion')
ao.samples = 16
ao.inputs['Distance'].default_value = 2
texture = nodes.new('ShaderNodeTexImage')
texture.image = image
nodes.active = texture
links.new(ao.outputs['Color'], emission.inputs['Color'])
links.new(emission.outputs[0], output.inputs['Surface'])
atlas.materials.append(material)
bake_scene.render.engine = 'CYCLES'
bake_scene.cycles.samples = 16
bake_scene.render.bake.margin = 8
bake_scene.render.bake.use_clear = True
print('R588_BAKING', len(targets), len(faces), len(occluders), flush=True)
bpy.ops.object.bake(type='EMIT')
image.filepath_raw = str(IMAGE)
image.file_format = 'PNG'
image.save()
image.pack()

for obj in targets:
    layer = obj.data.uv_layers.new(name=UV_NAME)
    assert layer and layer.name == UV_NAME and len(obj.data.uv_layers) <= 8, obj.name
for index, (name, loop_index) in enumerate(loop_map):
    bpy.data.objects[name].data.uv_layers[UV_NAME].data[loop_index].uv = atlas.uv_layers[UV_NAME].data[index].uv
group = bpy.data.node_groups.new('glTF Material Output R588', 'ShaderNodeTree')
group.interface.new_socket(name='Occlusion', in_out='INPUT', socket_type='NodeSocketFloat')
for copied in copies.values():
    nodes, links = copied.node_tree.nodes, copied.node_tree.links
    uv = nodes.new('ShaderNodeUVMap')
    uv.uv_map = UV_NAME
    texture = nodes.new('ShaderNodeTexImage')
    texture.image = image
    texture.interpolation = 'Linear'
    node = nodes.new('ShaderNodeGroup')
    node.node_tree = group
    links.new(uv.outputs[0], texture.inputs[0])
    links.new(texture.outputs['Color'], node.inputs['Occlusion'])

bpy.context.window.scene = original
bpy.data.scenes.remove(bake_scene)
bpy.data.objects.remove(bake_object, do_unlink=True)
bpy.data.meshes.remove(atlas)
bpy.data.materials.remove(material)
after = {o.name: geom_sig(o) for o in original.objects if o.type == 'MESH'}
assert before == after, 'AO process altered mesh geometry or transforms'
for name, layers in retained_uvs.items():
    for layer, digest in layers.items():
        assert uv_sig(bpy.data.objects[name].data.uv_layers[layer]) == digest, (name, layer)
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT), compress=True)
bpy.ops.wm.open_mainfile(filepath=str(OUTPUT))
reopened = {o.name: geom_sig(o) for o in bpy.context.scene.objects if o.type == 'MESH'}
assert before == reopened, 'Reopened geometry differs'
checks = []
for name in sorted(target_names):
    obj = bpy.data.objects[name]
    uv = obj.data.uv_layers[UV_NAME]
    assert all(math.isfinite(c) and -.00001 <= c <= 1.00001 for u in uv.data for c in u.uv), name
    for layer, digest in retained_uvs[name].items():
        assert uv_sig(obj.data.uv_layers[layer]) == digest, (name, layer)
    for material in obj.data.materials:
        if material is None:
            continue
        groups = [n for n in material.node_tree.nodes if n.type == 'GROUP' and n.node_tree and 'glTF Material Output' in n.node_tree.name]
        assert len(groups) == 1 and groups[0].node_tree.name.startswith('glTF Material Output R588'), material.name
        assert groups[0].inputs['Occlusion'].is_linked, material.name
    checks.append({'name': name, 'loops': len(uv.data), 'retainedUVsPreserved': True,
                   'connectedMaterialUsedUVsPreserved': True, 'retainedUVHashes': retained_uvs[name],
                   'connectedMaterialUsedUVHashes': used_uvs[name], 'uvCount': len(obj.data.uv_layers)})
write_report('R588_AO_BUILD.json', {
    'sourceScene': SOURCE.name, 'outputScene': OUTPUT.name, 'reopened': True,
    'targets': checks, 'skippedEmptyOrAbsent': skipped, 'occluders': occluders,
    'occluderSelection': 'Union of full target bounds expanded by 3 metres; vegetation excluded',
    'occluderTargetBoundsExpanded': [{'min': lo, 'max': hi} for lo, hi in target_bounds],
    'removedOldOcclusionGroups': removed_groups, 'image': str(IMAGE.relative_to(R)),
    'removedUnusedUVLayers': removed_uvs, 'uvLimit': 8,
    'imageSize': [2048, 2048], 'aoDistanceMetres': 2,
    'geometryChanged': False, 'geometryMeshCountChecked': len(before),
    'lighting': 'Local contact ambient occlusion only; dynamic sun lighting remains live.',
    'accepted': False, 'published': False,
})

selected = []
for obj in bpy.context.scene.objects:
    match = re.match(r'R(\d+)_', obj.name)
    revision = int(match[1]) if match else 0
    choose = obj.name.startswith(('R152_', 'R154_')) or obj.get('level_id') == 'L00_APPROACH' or 317 <= revision <= 588
    use = obj.type == 'MESH' and not obj.hide_render and bool(len(obj.data.polygons)) and choose
    obj.select_set(use)
    if use:
        assert all(math.isfinite(c) and abs(c) < 1500 for vertex in obj.data.vertices for c in (obj.matrix_world @ vertex.co)), obj.name
        selected.append(obj.name)
assert target_names <= set(selected)
bpy.ops.export_scene.gltf(filepath=str(GLB), export_format='GLB', use_selection=True,
                         export_apply=True, export_cameras=False, export_lights=False)
write_report('R588_EXPORT_SELECTION.json', {'near': selected})
print('R588_EXPORTED_NEAR', len(selected), GLB.stat().st_size, flush=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(GLB))
errors = []
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    invalid = sum(not all(math.isfinite(c) for c in vertex.co) for vertex in obj.data.vertices)
    zero = sum(face.area < 1e-10 for face in obj.data.polygons)
    if invalid or zero:
        errors.append({'name': obj.name, 'nonFinite': invalid, 'zeroArea': zero})
write_report('R588_GLB_ROUNDTRIP.json', {
    'file': str(GLB.relative_to(R)), 'bytes': GLB.stat().st_size,
    'errors': errors, 'accepted': False, 'published': False,
})
assert not any(e['nonFinite'] for e in errors), errors
if errors:
    print('R588_RAW_EXPORT_REQUIRES_RECORDED_WEB_SANITATION', errors, flush=True)
else:
    print('R588_RAW_AO_EXPORT_REOPEN_VERIFIED', flush=True)
# Final decoded Draco/WebP validation remains mandatory before publication.
