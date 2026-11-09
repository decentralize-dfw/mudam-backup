import bpy,bmesh,json,math,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R420_KULE_AVLU_ESKI_ORTU_TEMIZLIGI_ADAY_v001.blend'));o=bpy.data.objects['R154_FORT_ROUNDED_EARTH_ROOF'];o.hide_render=True;o.hide_viewport=True;o.hide_set(True);o['R422_superseded']='Independent R417 cover, R402 court, R389/R401 decks and tower architecture replace whole legacy roof. Remaining legacy mesh was 3.493m2 of clipping slivers; visibly crosses door.';names=['R420_CENTRE_LOW_COURT_CONTACT','R420_SOUTH_LOW_COURT_CONTACT'];records=[]
out=R/'scenes/MUDAM_R422_KALE_ESKI_ORTU_ARTIKLARI_KALDIRILDI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(x['nonManifold']==0 and x['zeroArea']==0 for x in checks)
(R/'reports/R422_LEGACY_ROOF_REMOVAL.json').write_text(json.dumps(dict(scene=out.name,clipped=records,checks=checks,accepted=False,published=False,limits=['Removes demonstrated false legacy surface crossing south door. Does not establish source fidelity of provisional tower facade.','West tower architecture and other immediate ring tasks remain.']),indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-53,-47,4.6));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-57.4,-63.1,3.1))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=35;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R422_south_court_candidate.png');bpy.ops.render.render(write_still=True)
