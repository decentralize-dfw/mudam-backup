import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
s=read('reports/R327_MUSEUM_RING_WORK_STATE.json');r=read('reports/R328_RUIN_FLOORS.json')
assert all(not c['nonManifold'] and not c['zeroArea'] for c in r['meshChecks'])
assert all(not c['nonFinite'] and not c['zeroArea'] for c in r['glbChecks'])
s['scene']='scenes/'+r['scene'];s['changes'].append('R328: two independent planar chamber floors fitted to classified ACT2024 LiDAR; old terrain and path faces clipped inside ruin outlines. Reopened and GLB round-trip checked.')
s['checks']['floorMesh']=r['meshChecks'];s['checks']['floorGlb']=r['glbChecks']
s['checks']['floorHeldOut']={k:v['heldOutCells'] for k,v in r['planes'].items()}
s['limitations'][1]='Ruin platform coping and courts remain provisional. Chamber floors now independently measured; central small recess depth not separately resolved.'
s['rejected'].append('R329 common coping planes: held-out RMS 0.132m north and 0.214m east; maximum errors 0.345m and 0.660m. Not applied. Segment-specific coping profiles required.')
s['photoReferencePolicy']='User explicitly directs use of site photographs wherever model reference is insufficient. Photos guide visible form, openings, materials and intersections; do not assume exact scale from uncalibrated photographs.'
s['inspectedPhotographs']=[{'path':'../05_Dis_Mekan/Havadan_Gorunum/116_Muze_havadan_genel_gorunum_Mudam.webp','evidence':'Pavilion-side stepped ruins, near facade wall, bridges and sunken planted strips; visible discontinuous historic wall tops.'},{'path':'../05_Dis_Mekan/Tarihi_Duvarlarla_Iliski/086_Muze_ve_tarihi_sur_duvarlari_ArchEyes.jpg','evidence':'Fort curved masonry wall, continuous dark coping, round upper apertures and lower rectangular openings, curved opposite retaining wall, grass moat floor. No exact dimensions inferred.'}]
s['nextGeometry']='Use R328 master. Resolve coping profiles by separate wall segments using classified LiDAR and photographs; then outer moat/path footprints, pavilion stepped moat and curved fort wall.'
s['exportReminder']=s['exportReminder'].replace('R327 SITE','R327, R328 SITE')
(R/'reports/R328_MUSEUM_RING_WORK_STATE.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
q=read('config/context_reconstruction_queue.json');q['current_local_checkpoint'].update(scene=s['scene'],report='reports/R328_MUSEUM_RING_WORK_STATE.json',accepted=False,published=False,next_geometry=s['nextGeometry']);q['next_actions']=[s['nextGeometry'],s['photoReferencePolicy'],s['exportReminder'],*s['limitations'][2:]]
(R/'config/context_reconstruction_queue.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
print('R328 recorded as technical candidate; whole-ring acceptance remains false.')
