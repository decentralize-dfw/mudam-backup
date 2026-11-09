import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R488_AVLU_SUR_MALZEME_BAGLANTI_ADAY_v001.blend'));D=json.loads((R/'reports/R489_DARK_INSET_PLANE.json').read_text());poly=D['outline'];tris=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]]);regions=[[poly[i] if isinstance(i,int) else (i.x,i.y) for i in f] for f in tris];records=[]
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
    if ob.type != 'MESH' or ob.hide_render or not (ob.name in ['R152_CLASS2_TERRAIN','R152_FORECOURT_0'] or ob.name.startswith('R152_PATH_')):
        continue
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
        for region in regions:
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



def solid(name,xy,zfn,depth,mat):
 n=len(xy);vs=[(x,y,zfn(x,y)+dz) for dz in [0,-depth] for x,y in xy];fs=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);ob['level_id']='SITE';me.materials.append(mat);return ob
c=D['coefficients'];height=lambda x,y:c[0]*x+c[1]*y+c[2];mat=bpy.data.materials.new('R489_SOURCE_DARK_INSET');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.035,.065,.075,1);bs.inputs['Roughness'].default_value=.36
# Independent flat inset; unknown function is explicitly retained in metadata.
ob=solid('R489_NW_DARK_HORIZONTAL_INSET',poly,height,.2,mat);ob['source']=D['interpretation'];ob['heightFitHeldoutMaxM']=D['max'];ob['heightFitHeldoutRmsM']=D['rms']
# Cut inherited court only where the visible inset occupies its footprint.
cutter=solid('TEMP_INSET_CUT',poly,lambda x,y:10,22,mat);body=bpy.data.objects['R457_NORTH_LOADING_COURT'];bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('DarkInsetOpening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
stone=bpy.data.objects['R457_NORTH_LOADING_COURT'].data.materials[0];names=[ob.name]
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
 a=Vector(a);b=Vector(b);direction=(b-a).normalized();normal=Vector((-direction.y,direction.x))*.07;xy=[a-normal,b-normal,b+normal,a+normal];o=solid('R489_INSET_STONE_BORDER_%d'%i,xy,lambda x,y:height(x,y)+.035,.4,stone);o['source']='Visible inset stone perimeter; 0.14m width visual estimate, not surveyed.';names.append(o.name)
checks={}
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks[name]={'nonManifold':sum(not e.is_manifold for e in bm.edges),'zeroArea':sum(f.calc_area()<1e-10 for f in bm.faces)};bm.free();assert not any(checks[name].values())
out=R/'scenes/MUDAM_R489_AVLU_KOYU_YATAY_BANT_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R489_BUILD.json').write_text(json.dumps(dict(checks=checks,cuts=records,reopened=True,accepted=False,published=False,uncertainty=D['interpretation']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-80,0,35));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-48,37,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=43;s.render.filepath=str(R/'renders/qa/R489_northwest_oblique.png');bpy.ops.render.render(write_still=True)
