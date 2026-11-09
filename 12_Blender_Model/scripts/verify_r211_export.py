from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R211_BUTUN_BINA_KABUKLARI_v002.blend'));s=bpy.context.scene;names=[];before=[]
for o in s.objects:
 selected=o.type=='MESH' and o.name.startswith(('R176_','R190_','R201_','R206_','R209_'));o.select_set(selected)
 if selected:
  names.append(o.name);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.001);before.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
path=R/'exports/r152_clean/r211_north_architecture_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
# The saved blend has been reopened, and the exported payload is independently decoded.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path));triangles=0;zero=0;finite=True;after=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 for t in o.data.loop_triangles:
  a,b,c=[o.data.vertices[i].co for i in t.vertices];zero+=((b-a).cross(c-a).length<1e-10)
 finite=finite and all(math.isfinite(c) for v in o.data.vertices for c in v.co)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.001);after.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges)));bm.free()
(R/'reports/R211_EXPORT_REOPEN.json').write_text(json.dumps(dict(technicalOnly=True,sourceFidelityAccepted=False,file=str(path),bytes=path.stat().st_size,triangles=triangles,zeroTriangles=zero,finite=finite,blendReopen=before,glbReopen=after),indent=2));print('R211_EXPORT',triangles,zero,finite,flush=True)
