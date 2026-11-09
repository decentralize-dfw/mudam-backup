from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R241_KALE_AVLU_SINIR_BAGLANTI_ADAY_v001.blend'))
terrain=bpy.data.objects['R154_FAR_GROUND'];terrain.data.calc_loop_triangles();g=BVHTree.FromPolygons([terrain.matrix_world@v.co for v in terrain.data.vertices],[list(t.vertices) for t in terrain.data.loop_triangles],all_triangles=True)
o=bpy.data.objects['R195_BOUNDARY_SOUTHWEST_COURT'];assert len(o.data.vertices)%4==0
changes=[];missing=[];top=[tuple(o.data.vertices[i].co) for i in range(len(o.data.vertices)) if i%4<2]
for i,v in enumerate(o.data.vertices):
 if i%4<2:continue
 p=o.matrix_world@v.co;h=g.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),300)[0]
 nearby=[]
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]:
  q=g.ray_cast(Vector((p.x+dx*.15,p.y+dy*.15,100)),Vector((0,0,-1)),300)[0]
  if q is not None:nearby.append(q)
 if nearby:h=min(nearby+([h] if h is not None else []),key=lambda q:q.z)
 if h is None:
  missing.append(i);continue
 if p.z>h.z-.10:
  delta=p.z-(h.z-.10);p.z=h.z-.10;v.co=o.matrix_world.inverted()@p;changes.append(delta)
assert top==[tuple(o.data.vertices[i].co) for i in range(len(o.data.vertices)) if i%4<2]
print('CONTACT',len(changes),max(changes,default=0),'MISSING',len(missing))
if not changes:raise RuntimeError('No contact correction warranted')
o.data.update();path=R/'scenes/MUDAM_R242_KALE_ISTINAT_ZEMIN_BAGLANTI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;t=Vector((-229.6,-192.1,-18));s.camera.location=t+Vector((35,-45,45));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=48;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R242_ruin_candidate.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name=='R195_BOUNDARY_SOUTHWEST_COURT')
glb=R/'exports/r152_clean/r242_retaining_contact_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[dict(name=o.name,finite=all(math.isfinite(c) for v in o.data.vertices for c in v.co),zero=sum(p.area<1e-10 for p in o.data.polygons)) for o in bpy.context.scene.objects if o.type=='MESH'];assert all(c['finite'] and not c['zero'] for c in checks)
(R/'reports/R242_RETAINING_CONTACT.json').write_text(json.dumps(dict(accepted=False,published=False,changedBottomVertices=len(changes),maximumExtension=max(changes),missingTerrainVertices=missing,topPreserved=True,reopen=checks,limits=['Contact to authored terrain only; not measured foundation depth','Missing terrain samples intentionally unchanged','Uphill apron and source fidelity remain incomplete']),indent=2));print('R242_READY')
