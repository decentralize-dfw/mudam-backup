import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R433_ON_YOL_CAKISMA_TEMIZLIGI_ADAY_v001.blend'));fort=json.loads((R/'.local_source_cache/r154/fort.json').read_text());col=bpy.context.scene.collection;entry=Vector((*fort['entry'],0));direction=Vector((*fort['direction'],0));tangent=Vector((*fort['tangent'],0));deck=fort['deck_z'];stone=bpy.data.materials['R154_FORT_STONE_PBR'];frame=bpy.data.materials['R154_CUT_STONE_DRESSINGS'];dark=bpy.data.materials['R154_RECESSED_OPENINGS'];body=bpy.data.objects['R154_FORT_MASONRY_BODY']
def uv(o, scale=4, horizontal=False):
    me = o.data
    for l in list(me.uv_layers):
        me.uv_layers.remove(l)
    layer = me.uv_layers.new(name='UVMap')
    for f in me.polygons:
        normal = f.normal
        u = Vector((0, 0, 1)).cross(normal).normalized() if abs(normal.z) < 0.7 else Vector((1, 0, 0))
        v = normal.cross(u).normalized()
        for li in f.loop_indices:
            q = me.vertices[me.loops[li].vertex_index].co
            layer.data[li].uv = (q.x / scale, q.y / scale) if horizontal else (q.dot(u) / scale, q.dot(v) / scale)
def mesh(name, vs, fs, material, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(vs, [], fs)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-06)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    me.materials.append(material)
    o['level_id'] = 'SITE'
    o['source'] = 'ACT LiDAR2024 / ACT2020 / OSM'
    uv(o)
    if smooth:
        for f in me.polygons:
            f.use_smooth = True
    return o
def arch(name, center, bottom, width, straight, depth, material):
    r = width / 2
    shape = [(-r, 0), (r, 0)] + [(r * math.cos(a), straight + r * math.sin(a)) for a in [math.pi * i / 20 for i in range(21)]]
    vs = []
    for d in depth:
        for x, z in shape:
            vs.append(tuple(center + tangent * x + direction * d + Vector((0, 0, bottom + z))))
    n = len(shape)
    fs = [list(range(n - 1, -1, -1)), list(range(n, 2 * n))] + [[i, (i + 1) % n, (i + 1) % n + n, i + n] for i in range(n)]
    return mesh(name, vs, fs, material)
def subtract(target, cutter):
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new('Source opening', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
# Restore only the volume of the superseded small window; the new opening is cut in both pieces.
fill=arch('R434_SUPERSEDED_WINDOW_MASONRY',entry+tangent*5,deck+.8,1.55,1.55,[0,2.1],stone)
for o in list(bpy.context.scene.objects):
 if o.name.startswith(('R154_ENTRANCE_ARCH_','R154_ENTRANCE_JAMB_','R154_ENTRANCE_RECESSED','R154_FRONT_WINDOW_')):o.hide_render=True;o.hide_viewport=True;o.hide_set(True)
rows=[('ENTRANCE',entry,deck-.04,2.65,-1.65-(deck-.04)-1.325),('WINDOW',entry+tangent*6.30,-5.04,2.65,-1.60+5.04-1.325)]
for label,c,bottom,width,straight in rows:
 for target in [body,fill]:subtract(target,arch('R434_TEMP_CUT',c,bottom,width,straight,[-1.4,2.1],dark))
 arch('R434_'+label+'_RECESSED',c,bottom,width*.98,straight,[.30,.34] if label=='WINDOW' else [1.8,1.84],dark)
 radius=width/2
 for j in range(20):
  a=math.pi*j/20+.002;b=math.pi*(j+1)/20-.002;points=[(radius*math.cos(a),straight+radius*math.sin(a)),(radius*math.cos(b),straight+radius*math.sin(b)),((radius+.24)*math.cos(b),straight+(radius+.24)*math.sin(b)),((radius+.24)*math.cos(a),straight+(radius+.24)*math.sin(a))];vs=[tuple(c+tangent*x+direction*d+Vector((0,0,bottom+z))) for d in [-.18,.15] for x,z in points];mesh('R434_'+label+'_ARCH_%02d'%j,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],frame)
 for side in [-1,1]:
  xs=[side*radius,side*(radius+.24)];vs=[tuple(c+tangent*x+direction*d+Vector((0,0,z))) for d in [-.18,.15] for x,z in [(xs[0],bottom),(xs[1],bottom),(xs[1],bottom+straight),(xs[0],bottom+straight)]];mesh('R434_'+label+'_JAMB_'+str(side),vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],frame)
 # Photo-visible rectangular window frame and sill, below semicircular fanlight.
 if label=='WINDOW':
  def bar(name,x0,x1,z0,z1,d0=.10,d1=.22):
   vs=[tuple(c+tangent*x+direction*d+Vector((0,0,z))) for d in [d0,d1] for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]];return mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],frame)
  bar('R434_WINDOW_MULLION',-.045,.045,bottom,bottom+straight);bar('R434_WINDOW_TRANSOM',-radius,radius,bottom+straight-.045,bottom+straight+.045);bar('R434_WINDOW_LOWER_FRAME',-radius,radius,bottom,bottom+.08);bar('R434_WINDOW_STONE_SILL',-radius-.28,radius+.28,bottom-.18,bottom-.02,-.35,.1)
uv(body);uv(fill)
out=R/'scenes/MUDAM_R434_KALE_ON_CEPHE_ACIKLIKLARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('R434_'):
  bm=bmesh.new();bm.from_mesh(o.data);checks.append(dict(name=o.name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R434_FRONT_OPENING_BUILD.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,checks=checks,source='R432 projection and R423_68151060 independent photo',limits=['Source ACT arch pixels blurred: 2.65m width is model candidate, not surveyed.','Entrance lateral displacement not applied; bridge alignment preserved pending registration.','Historic body has inherited intentional open eaves; local operations require ray verification.']),indent=2));print('R434_SAVED',flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-107,-92,6));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-63,-54,1.7))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=50;s.render.filepath=str(R/'renders/qa/R434_front_candidate.png');bpy.ops.render.render(write_still=True)
