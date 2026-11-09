from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R235_KALE_AVLU_KOT_ADAY_v001.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith('R193_SOUTHWEST_COURT'):continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);records=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith('R194_'):continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001);long=[e for e in bm.edges if e.calc_length()>1];bmesh.ops.subdivide_edges(bm,edges=long,cuts=3,use_grid_fill=True);bm.to_mesh(o.data);bm.free();changes=[]
 for v in o.data.vertices:
  p=o.matrix_world@v.co;hit=g.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),300)[0]
  if hit is None:continue
  old=p.z;p.z=hit.z+.025;v.co=o.matrix_world.inverted()@p;changes.append(abs(p.z-old))
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(o.data);bm.free()
 o.data.update()
 if changes:records.append(dict(name=o.name,changedVertices=len(changes),maxShift=max(changes)))
assert records
path=R/'scenes/MUDAM_R236_KALE_AVLU_YOL_OTURUM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for o in bpy.context.scene.objects:o.select_set(o.name.startswith(('R194_','R193_SOUTHWEST_COURT')))
glb=R/'exports/r152_clean/r236_court_paths_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 checks.append(dict(name=o.name,finite=all(math.isfinite(x)for v in o.data.vertices for x in v.co),zero=sum(p.area<1e-10 for p in o.data.polygons)))
assert all(c['finite']and not c['zero']for c in checks)
(R/'reports/R236_COURT_PATH_CONTACT.json').write_text(json.dumps(dict(accepted=False,published=False,changes=records,reopen=checks,method='Retained source-traced XY footprints; independent court-grade contact, subdivisions only on existing authored path mesh',limits=['Inherited R235 court fit not finally accepted','Path outside court unchanged; border crossings and stone boundary need visual review','No full fort or region11 acceptance']),indent=2));print('R236_READY',records)

