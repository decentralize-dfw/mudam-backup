import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
inheritance=read('reports/R327_INHERITANCE.json')
north=read('reports/R326_NORTH_RUIN_PLAN.json');east=read('reports/R327_EAST_RUIN_PLAN.json')
assert inheritance['museumGeometryPreserved'] and not inheritance['unexpected']
assert all(not c['nonManifold'] and not c['zeroArea'] for r in [north,east] for c in r['meshChecks'])
assert all(not c['nonFinite'] and not c['zeroArea'] for r in [north,east] for c in r['glbChecks'])
state=dict(scene='scenes/MUDAM_R327_DOGU_KALINTI_PLAN_ADAY_v001.blend',accepted=False,published=False,
 scope='Only museum perimeter walls, moats, bridges, terraces and ruins in R316 user green marks. Distant surroundings deferred.',
 changes=[
  'R323: west ramp differentiated from upper terrace; three retaining controls relocated to outer ramp edge using source sections.',
  'R324: 84 of 100 terrace-edge stations matched to existing museum exterior walls; 25mm contact overlap; 16 unmatched preserved for follow-up. Museum untouched.',
  'R326: north ruin raised masonry platform, five-bay connected corridor, three side chambers, central recess and court independently rebuilt from matched orthographic reference; old partitions 01-09 replaced.',
  'R326: four false trees inside the source-visible open court hidden; tree source meshes and local transforms preserved.',
  'R327: east ruin raised masonry platform, three-bay connected corridor, three side chambers, central recess, lower masonry remnant and court independently reconstructed; old partitions 11-18 replaced.'
 ],
 rejected=['R325 platform v001: one nonmanifold edge and visually misaligned chambers; replaced by R326. Do not use.'],
 checks=dict(inheritance=inheritance,northMesh=north['meshChecks'],eastMesh=east['meshChecks'],northGlb=north['glbChecks'],eastGlb=east['glbChecks']),
 matchedViews=['renders/qa/R325_north_ruin_source.png','renders/qa/R326_north_ruin_candidate.png','renders/qa/R327_east_ruin_source.png','renders/qa/R327_east_ruin_candidate.png'],
 limitations=[
  'Matched-view plan reconstruction is not survey-grade height acceptance. Sparse scan chamber hits frequently lie on walls or noisy surfaces.',
  'New ruin platform top -0.08m and deep buried foundations remain candidates; chamber floors still inherit prior terrain. Do not claim measured chamber depths.',
  'Outer moat road R152_PATH_824216705 is visually too broad/bright around ruins; first-hit tests do not by themselves prove the correct moat floor. Resolve its footprint/material and source sections before publication.',
  'North old outer partition00 and east partition10 remain; their outlines/levels need comparison with newly reconstructed inner works.',
  'West ramp grade transitions, remaining 16 terrace contact points, pavilion stepped moat floors, fort roof/curved walls and eastern historic facade still unresolved.',
  'Court and wall materials remain visibly different from reference; no full-ring fidelity or 100 percent claim.'
 ],
 nextGeometry='Resolve outer ruin moat/path overlaps and levels; then pavilion stepped moat domains and fort curved-wall/coping boundaries. Use R327 master. Do not repeat northern/eastern chamber plan reconstruction.',
 exportReminder='Include R321, R322, R325, R326, R327 SITE objects in near-site GLB; skip hide_render and replaced old partitions. Existing R314 exporter excludes these new prefixes.')
(R/'reports/R327_MUSEUM_RING_WORK_STATE.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
q=read('config/context_reconstruction_queue.json')
q['current_local_checkpoint']=dict(scene=state['scene'],report='reports/R327_MUSEUM_RING_WORK_STATE.json',accepted=False,published=False,museum_geometry_preserved=True,authored_row_already_in_master=True,next_geometry=state['nextGeometry'])
q['next_actions']=[state['nextGeometry'],*state['limitations'][2:5],state['exportReminder'],'Verify source-matched views, reopened scene and GLB before any accepted publication; no whole-ring accuracy claim.']
(R/'config/context_reconstruction_queue.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
print('R327_WORK_STATE_RECORDED; geometry and GLB checks passed; visual acceptance pending')
