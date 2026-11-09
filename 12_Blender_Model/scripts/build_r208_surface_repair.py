from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R207_GERCEK_BITKI_CAKISMA_TEMIZLIGI_v001.blend'));records=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 mats=list(o.data.materials);land=any(m and m.name.startswith('R157_CONTINUOUS_LANDCOVER') for m in mats)
 surface=o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS'] or o.name.startswith(('R182_EXTENSION_','R192_GRADE_','R193_SOUTHWEST_COURT','R187_OUTER_BASTIONS','R187_CONNECTED_MOAT','R191_','R189_','R177_ROAD_','R178_APRON_'))
 if not(surface or land):continue
 me=o.data;before=sum(p.normal.z<-.001 for p in me.polygons);bm=bmesh.new();bm.from_mesh(me)
 for f in bm.faces:
  if f.normal.z<-.001:f.normal_flip()
 bm.to_mesh(me);bm.free();me.update();uv=me.uv_layers.active or me.uv_layers.new(name='UVMap');micro=me.uv_layers.get('MicroUV') or me.uv_layers.new(name='MicroUV')
 for p in me.polygons:
  m=mats[p.material_index] if p.material_index<len(mats) else None
  for li in p.loop_indices:
   v=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;micro.data[li].uv=(v.x/6,v.y/6)
   if m and m.name.startswith('R157_CONTINUOUS_LANDCOVER'):uv.data[li].uv=((v.x+500)/1150,(v.y+450)/1100)
 me.uv_layers.active_index=0
 records.append(dict(name=o.name,flipped_faces=before,downward_after=sum(p.normal.z<-.001 for p in me.polygons),restoredMicroUV=True,landcoverUVCorrected=land))
(R/'reports/R208_GROUND_SURFACE_REPAIR.json').write_text(json.dumps(dict(accepted=False,changes=records,method='Orient 2.5D authored ground upward; restore MicroUV at6m and global landcover atlas coordinates without changing vertex elevations',limits=['This repairs local candidate render/export defects; source geometry acceptance remains separate','Outside atlas extent landcover still extrapolated']),indent=2));print('FLIPPED',sum(r['flipped_faces'] for r in records),flush=True)
s=bpy.context.scene;t=Vector((370,440,20));s.camera.location=t+Vector((120,-190,140));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=170;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R208_DOGRU_ARAZI_YUZEYLERI_v001.blend'),compress=True);s.render.filepath=str(R/'renders/qa/R208_north_ground_repair_v001.png');bpy.ops.render.render(write_still=True)
