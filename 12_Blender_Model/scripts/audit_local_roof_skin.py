"""Local normal rays across reference roof faces; distant walls cannot hide holes.

Read-only diagnostic. Hidden P06 faces are reference domains, never occluders.
"""
from pathlib import Path
import bpy, json, sys, math, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(B/'scripts'))
from release_utils import verified_current_scene
r = verified_current_scene()
bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
revision = re.search(r'_R(\d+)_', r['file']).group(1)
deps = bpy.context.evaluated_depsgraph_get()
verts, faces, owners = [], [], []
for ob in bpy.context.scene.objects:
    if ob.type != 'MESH' or ob.hide_render or not ob.visible_get():
        continue
    if not ob.name.startswith(('P10_', 'R83_')):
        continue
    eo = ob.evaluated_get(deps)
    mesh = eo.to_mesh()
    start = len(verts)
    verts.extend(eo.matrix_world @ v.co for v in mesh.vertices)
    faces.extend(tuple(start+i for i in p.vertices) for p in mesh.polygons)
    owners.extend([ob.name]*len(mesh.polygons))
    eo.to_mesh_clear()
tree = BVHTree.FromPolygons(verts, faces)
control_ob = bpy.data.objects['P10_MAIN_ROOF_FACE_1_GLASS_02_05']
control_points = [control_ob.matrix_world @ v.co for v in control_ob.data.vertices]
control_center = sum(control_points[:len(control_points)//2], Vector())/(len(control_points)//2)
control_normal = (control_points[1]-control_points[0]).cross(control_points[2]-control_points[0]).normalized()
control_tree = BVHTree.FromPolygons(verts, [face for face, owner in zip(faces, owners) if owner != control_ob.name])
control = dict(omitted_from_diagnostic_only=control_ob.name,
               baseline_hit=tree.ray_cast(control_center+control_normal*.3, -control_normal, .6)[0] is not None,
               missing_detected=control_tree.ray_cast(control_center+control_normal*.3, -control_normal, .6)[0] is None,
               scene_changed=False)
assert control['baseline_hit'] and control['missing_detected'], control

def inside(x, y, poly):
    result = False
    for a, b in zip(poly, poly[1:]+poly[:1]):
        if (a[1]>y) != (b[1]>y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            result = not result
    return result

rows = []
for ob in bpy.context.scene.objects:
    if not ob.name.startswith(('P06_MAIN_ROOF_FACE_', 'P06_MAIN_LANTERN_', 'P06_MAIN_CAP_')):
        continue
    ps = [ob.matrix_world @ v.co for v in ob.data.vertices]
    origin = ps[0]
    u = (ps[1]-origin).normalized()
    normal = (ps[1]-origin).cross(ps[2]-origin).normalized()
    v = normal.cross(u).normalized()
    poly = [[(p-origin).dot(u), (p-origin).dot(v)] for p in ps]
    samples, missing = 0, []
    def check(p, kind):
        hit = tree.ray_cast(p+normal*.3, -normal, .6)
        if hit[0] is None:
            missing.append(dict(position=list(p), kind=kind))
    # 5cm interior grid plus explicitly sampled perimeter bands at 0/1/3/6cm.
    for ix in range(math.floor(min(p[0] for p in poly)/.05), math.ceil(max(p[0] for p in poly)/.05)):
        for iy in range(math.floor(min(p[1] for p in poly)/.05), math.ceil(max(p[1] for p in poly)/.05)):
            x, y = (ix+.5)*.05, (iy+.5)*.05
            if inside(x, y, poly):
                samples += 1
                check(origin+u*x+v*y, 'interior')
    center = sum(ps, Vector())/len(ps)
    for a, b in zip(ps, ps[1:]+ps[:1]):
        edge = b-a
        inward = normal.cross(edge).normalized()
        if inward.dot(center-(a+b)/2)<0:
            inward = -inward
        count = max(1, math.ceil(edge.length/.05))
        for i in range(count):
            for offset in [0, .01, .03, .06]:
                p = a+edge*((i+.5)/count)+inward*offset
                if inside((p-origin).dot(u), (p-origin).dot(v), poly) or offset == 0:
                    samples += 1
                    check(p, 'edge_band')
    rows.append(dict(face=ob.name, samples=samples, missing_count=len(missing), missing=missing))
out = dict(file=r['file'], step_m=.05, ray_length_m=.6, faces=rows,
           negative_control=control,
           total_samples=sum(x['samples'] for x in rows), missing_count=sum(x['missing_count'] for x in rows),
           limits=['Only the main roof, lantern and cap reference domains are tested.',
                   'Local closure is not source silhouette acceptance or measurement certification.',
                   'No distant wall, shading layer or hidden reference sheet may mask a missing roof skin.'])
(B/'reports'/f'R{revision}_local_roof_skin.json').write_text(json.dumps(out, indent=2), encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='faces'}))
print([(x['face'],x['missing_count']) for x in rows])

# Test the narrow vertical strip directly below each main eave against visible
# architecture. This does not require distant room walls to be hit.
verts, faces = [], []
for ob in bpy.context.scene.objects:
    if ob.type != 'MESH' or ob.hide_render or not ob.visible_get() or ob.get('level_id') == 'SITE':
        continue
    if re.search('TREE|MOAT|HISTORIC|LAMP|LENS|SPOT|UPLIGHT|FIXTURE|RAIL|HANDRAIL|SEAT|CHAIR|SIGN|CONTROL|BUTTON|SHADING|SLAT', ob.name, re.I):
        continue
    eo = ob.evaluated_get(deps)
    mesh = eo.to_mesh()
    start = len(verts)
    verts.extend(eo.matrix_world @ v.co for v in mesh.vertices)
    faces.extend(tuple(start+i for i in p.vertices) for p in mesh.polygons)
    eo.to_mesh_clear()
tree = BVHTree.FromPolygons(verts, faces)
bands = []
for index in range(8):
    ob = bpy.data.objects[f'P06_MAIN_ROOF_FACE_{index}']
    a, b = [ob.matrix_world @ v.co for v in ob.data.vertices[:2]]
    edge = b-a
    normal = Vector((-edge.y, edge.x, 0)).normalized()
    count = math.ceil(edge.length/.05)
    missing = []
    for i in range(count):
        for drop in [.05, .15, .3, .6]:
            p = a+edge*((i+.5)/count)-Vector((0,0,drop))
            if tree.ray_cast(p+normal*.6, -normal, 1.2)[0] is None:
                missing.append(dict(position=list(p), drop_m=drop, fraction=(i+.5)/count,
                                    below_low_eave=p.z < min(a.z,b.z)-.001,
                                    classification='below_transition_domain' if p.z < min(a.z,b.z)-.001 else 'unresolved_local_gap'))
    bands.append(dict(edge=index, samples=count*4, missing_count=len(missing), missing=missing))
out = dict(file=r['file'], edges=bands, total_samples=sum(x['samples'] for x in bands),
           missing_count=sum(x['missing_count'] for x in bands), construction_acceptance=False,
           transition_domain_missing=sum(not m['below_low_eave'] for x in bands for m in x['missing']),
           limits=['Local eave diagnostic only; a displaced wall can be outside the 1.2m search band.',
                   'Sloping transition glazing ends at the low eave. Lower samples can lie in adjoining interior volume; no wall is required on this diagnostic plane.',
                   'Findings require source classification before any geometry repair.'])
(B/'reports'/f'R{revision}_local_eave_band.json').write_text(json.dumps(out, indent=2), encoding='utf8')
print('EAVE BANDS', [(x['edge'],x['missing_count']) for x in bands])
