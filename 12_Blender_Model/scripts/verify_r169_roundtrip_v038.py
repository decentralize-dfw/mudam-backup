from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];source=R/'scenes/MUDAM_R169_YAN_BAGLANTI_ADAY_v038.blend';out=R/'exports/r152_clean/r169_geometry_review_v038.glb'
def stats():
 count=0;bounds=[];bad=0
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();count+=len(o.data.loop_triangles)
  for v in o.data.vertices:
   p=o.matrix_world@v.co;assert all(math.isfinite(x) for x in p);bounds.append(tuple(p))
  bad+=sum(t.area<1e-9 for t in o.data.loop_triangles)
 return dict(triangles=count,degenerate=bad,min=[min(p[i] for p in bounds) for i in range(3)],max=[max(p[i] for p in bounds) for i in range(3)])
bpy.ops.wm.open_mainfile(filepath=str(source));before=stats();assert before['degenerate']==0,before
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out));after=stats();assert before['triangles']==after['triangles'];drift=max(abs(before[k][i]-after[k][i]) for k in ['min','max'] for i in range(3));assert drift<.001;assert after['degenerate']==0
report=dict(source=source.name,export=out.name,bytes=out.stat().st_size,before=before,after=after,max_bounds_drift_m=drift,accepted=False,published=False,validation_scope='GLB technical round trip only; visual reconstruction incomplete')
(R/'reports/R169_GLB_ROUNDTRIP_v038.json').write_text(json.dumps(report,indent=2));print('ROUNDTRIP_PASSED',report)






