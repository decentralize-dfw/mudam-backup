"""Reopen saved deliverables in a fresh Blender process and check geometric contracts."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
checks=json.loads((B/'reports/P03_coordinate_checks.json').read_text())['checks']
results=[]
for filename in ['MUDAM_P03_REFERANS_v002.blend','MUDAM_P04_KOT_ETUDU_v002.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/filename));S=bpy.context.scene
 assert S.unit_settings.scale_length==1 and S.unit_settings.system=='METRIC'
 assert not any(min(o.scale)<0 for o in S.objects)
 errs=[(Vector(c['local_xy'])-Vector(bpy.data.objects['CONTROL_'+c['name']].location[:2])).length for c in checks]
 assert max(errs)<1e-4
 assert all(i.packed_file for i in bpy.data.images if i.source=='FILE' and i.type=='IMAGE')
 assert all(o['source_ids']=='PDF2016' for o in S.objects if o.name.startswith('INK_'))
 assert not any(len(bpy.data.collections[n].objects) for n in ['02_STRUCTURE','03_ENVELOPE','04_ROOFS','06_CIRCULATION'])
 res=dict(file=filename,objects=len(S.objects),packed_images=sum(bool(i.packed_file) for i in bpy.data.images),coordinate_error_m=max(errs),unit_scale=1,unresolved_production_collections_empty=True)
 if 'P04' in filename:
  z=json.loads(S['draft_floor_levels']);assert z['LM1']!=z['PAV_LM1']
  walls=bpy.data.objects['P04_PAV_WALL_ENVELOPE'];slope=bpy.data.objects['P04_PAV_ROOF_SLOPE'];lantern=bpy.data.objects['P04_PAV_LANTERN'];cap=bpy.data.objects['P04_PAV_CAP']
  seams=[]
  for a,b in [(walls,slope),(slope,lantern),(lantern,cap)]:
   seams.extend((a.data.vertices[i+8].co-b.data.vertices[i].co).length for i in range(8))
  assert max(seams)<1e-6
  for ob in [walls,slope,lantern,cap]:
   assert all(p.area>1e-6 for p in ob.data.polygons)
   assert ob['status']=='study_not_accepted'
  res['pavilion_max_join_gap_m']=max(seams);res['pavilion_faces']=sum(len(o.data.polygons) for o in [walls,slope,lantern,cap]);res['draft_levels']=z
 results.append(res)
(B/'reports/SAVED_SCENE_VERIFICATION.json').write_text(json.dumps(dict(status='pass',fresh_process=True,results=results),indent=2),encoding='utf8')
print('SAVED_SCENE_VERIFICATION_PASS',json.dumps(results))
