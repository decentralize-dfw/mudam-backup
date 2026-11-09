import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R314_ECCL_GUNEY_KOSE_OTURUM_ADAY_v001.blend'))
a=Vector((178.3125,26.625));b=Vector((332.4375,282.375));u=(b-a).normalized();n=Vector((-u.y,u.x))
# Manual boundary measurements on orthographic ACT reference; no scan mesh transfer.
# Pixel/world mapping: x=167.5+.045px, y=52.5-.045py.
trace=[(244,548),(235,567),(230,585),(230,605),(234,625),(243,646),(256,666),(278,692),(475,828)]
outer=[Vector((167.5+x*.045,52.5-y*.045)) for x,y in trace]
poly=[b,b-n*12,Vector((185.275,24.735)),Vector((191.305,20.55)),Vector((302.25,95.25)),Vector((302.25,86.445))]+list(reversed(outer))
# Independent planar canopy solid with source-traced southern end.
if sum(p.x*q.y-q.x*p.y for p,q in zip(poly,poly[1:]+poly[:1]))<0:poly.reverse()
for o in list(bpy.context.scene.objects):
 if o.name=='R308_WING_CANOPY':bpy.data.objects.remove(o,do_unlink=True)
N=len(poly);verts=[(p.x,p.y,z) for z in [21.90,22.45] for p in poly];tris=tessellate_polygon([[Vector((p.x,p.y,0)) for p in poly]]);index={(round(p.x,6),round(p.y,6)):i for i,p in enumerate(poly)};faces=[]
for tri in tris:
 ids=[p if isinstance(p,int) else index[(round(p.x,6),round(p.y,6))] for p in tri];faces.extend([tuple(reversed(ids)),tuple(i+N for i in ids)])
faces.extend((i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N));me=bpy.data.meshes.new('R315_SOURCE_TRACED_WING');me.from_pydata(verts,[],faces);me.materials.append(bpy.data.materials['R308_ECCL_WING']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
scene=R/'scenes/MUDAM_R315_ECCL_KAYNAK_SACAK_UCU_ADAY_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;s.camera.location=(190,30,150);s.camera.rotation_euler=(Vector((190,30,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=45;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=4;s.render.filepath=str(R/'renders/qa/R315_tip_top_rebuilt_v002.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name=='R315_SOURCE_TRACED_WING')
glb=R/'exports/r152_clean/r315_canopy_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R315_CANOPY_TRACE.json').write_text(json.dumps(dict(accepted=False,published=False,scene=str(scene),source='renders/qa/R315_tip_top_source.png',sourcePixels=trace,polygon=[list(p) for p in poly],checks=checks,limits=['Manual45mm-per-pixel outer boundary trace, not surveyed','Inner edge and22.45/21.9 roof levels retained from prior candidate','End facade and soffit must be reconciled to revised outline before acceptance']),indent=2));print('R315_READY')


