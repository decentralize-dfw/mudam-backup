import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R451_KALE_BURC_YUZEY_NORMALLERI_ADAY_v001.blend'))
d=json.loads((R/'reports/R453_NORTH_LOWER_FLOOR_PLANE.json').read_text());assert d['valid'];poly=[(-120+x*220/1400,95-y*220/1400) for x,y in [(700,263),(865,267),(870,232),(884,232),(881,328),(699,321)]];plane=d['plane']
tri=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]])
captris=list(tri);regions=[[poly[i] if isinstance(i,int) else (i.x,i.y) for i in f] for f in tri];records=[]
def clip(points, a, b, sign, inside):
    out = []
    for j, P in enumerate(points):
        Q = points[(j + 1) % len(points)]
        f = lambda X: sign * ((b[0] - a[0]) * (X[1] - a[1]) - (b[1] - a[1]) * (X[0] - a[0]))
        dp = f(P)
        dq = f(Q)
        ip = dp >= -1e-08 if inside else dp <= 1e-08
        iq = dq >= -1e-08 if inside else dq <= 1e-08
        if ip:
            out.append(P)
        if ip != iq:
            t = dp / (dp - dq)
            out.append(tuple((p + (q - p) * t for p, q in zip(P, Q))))
    return out
for ob in list(bpy.context.scene.objects):
    if ob.type != 'MESH' or ob.hide_render or ob.name not in ['R152_CLASS2_TERRAIN','R152_PATH_759551377','R152_PATH_51768376','R152_FORECOURT_0']:
        continue
    active_regions=regions
    if ob.name.startswith('R152_PATH_'):
        active_regions=[[(-120+x*220/1400,95-y*220/1400) for x,y in [(690,222),(888,222),(888,332),(690,332)]]]
    me = ob.data
    me.calc_loop_triangles()
    uvs = list(me.uv_layers)
    verts = []
    faces = []
    mis = []
    attrs = []
    changed = 0
    for tr in me.loop_triangles:
        points = []
        for li in tr.loops:
            q = ob.matrix_world @ me.vertices[me.loops[li].vertex_index].co
            points.append(tuple(q) + tuple((v for layer in uvs for v in layer.data[li].uv)))
        chunks = [points]
        for region in active_regions:
            sign = 1 if sum((region[i][0] * region[(i + 1) % len(region)][1] - region[(i + 1) % len(region)][0] * region[i][1] for i in range(len(region)))) > 0 else -1
            result = []
            for chunk in chunks:
                if max((p[0] for p in chunk)) < min((p[0] for p in region)) or min((p[0] for p in chunk)) > max((p[0] for p in region)) or max((p[1] for p in chunk)) < min((p[1] for p in region)) or (min((p[1] for p in chunk)) > max((p[1] for p in region))):
                    result.append(chunk)
                    continue
                remaining = chunk
                for i, a in enumerate(region):
                    if len(remaining) < 3:
                        break
                    b = region[(i + 1) % len(region)]
                    outside = clip(remaining, a, b, sign, False)
                    if len(outside) > 2:
                        result.append(outside)
                    remaining = clip(remaining, a, b, sign, True)
                if len(remaining) > 2:
                    changed += 1
            chunks = result
        for chunk in chunks:
            for i in range(1, len(chunk) - 1):
                tri = [chunk[0], chunk[i], chunk[i + 1]]
                if (Vector(tri[1][:3]) - Vector(tri[0][:3])).cross(Vector(tri[2][:3]) - Vector(tri[0][:3])).length < 1e-08:
                    continue
                k = len(verts)
                verts.extend((tuple(ob.matrix_world.inverted() @ Vector(p[:3])) for p in tri))
                attrs.extend((p[3:] for p in tri))
                faces.append((k, k + 1, k + 2))
                mis.append(tr.material_index)
    if changed:
        new = bpy.data.meshes.new(ob.name + '_COURT_CUT')
        new.from_pydata(verts, [], faces)
        new.update()
        for ma in me.materials:
            new.materials.append(ma)
        for i, ma in enumerate(mis):
            new.polygons[i].material_index = ma
        for j, layer in enumerate(uvs):
            dst = new.uv_layers.new(name=layer.name)
            for l in new.loops:
                dst.data[l.index].uv = attrs[l.vertex_index][j * 2:j * 2 + 2]
        ob.data = new
        records.append(dict(name=ob.name, cutTriangles=changed))
n=len(poly);vs=[(x,y,plane[0]*x+plane[1]*y+plane[2]+dz) for dz in [0,-.16] for x,y in poly];faces=[]
for f in captris:
 ids=[i if isinstance(i,int) else min(range(n),key=lambda j:(Vector((*poly[j],0))-i).length) for i in f];faces.append(tuple(ids));faces.append(tuple(i+n for i in reversed(ids)))
for i in range(n):j=(i+1)%n;faces.append((i,j,j+n,i+n))
me=bpy.data.meshes.new('R453_NORTH_MOAT_MINERAL_FLOOR');me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o)
m=bpy.data.materials.new('R453_NORTH_MOAT_MINERAL');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.19,.18,.15,1);bs.inputs['Roughness'].default_value=.89
tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=36;tex.inputs['Detail'].default_value=2
coord=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coord.outputs['Object'],tex.inputs['Vector']);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.008;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']);me.materials.append(m)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o['source']='R430 photo-traced boundary; analytic class2 plane; 35 held-out cells RMS0.03017m max0.05225m. No scan faces copied.';o['level_id']='SITE'
out=R/'scenes/MUDAM_R456_KUZEY_HENDEK_SINIR_BAGLANTISI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));o=bpy.data.objects['R453_NORTH_MOAT_MINERAL_FLOOR'];bm=bmesh.new();bm.from_mesh(o.data);check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();assert not any(check.values())
(R/'reports/R456_NORTH_FLOOR_BUILD.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,check=check,terrainCuts=records,source=d['check'],limits=['Boundary traced from ACT top view, not cadastral survey.','Mineral finish photo-estimated; procedural bump requires texture bake for GLB.','Only lower north moat floor; loading court and perimeter transitions remain unaccepted.']),indent=2));print('R430_SAVED',records,flush=True)

s=bpy.context.scene;s.render.engine="CYCLES";s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=750;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(0,44,75));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((0,44,-5))-s.camera.location).to_track_quat("-Z","Y").to_euler();s.camera.data.type="ORTHO";s.camera.data.ortho_scale=75;s.render.filepath=str(R/"renders/qa/R456_north_floor.png");bpy.ops.render.render(write_still=True)
