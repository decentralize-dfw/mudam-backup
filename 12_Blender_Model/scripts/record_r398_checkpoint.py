from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
state=dict(scene='scenes/MUDAM_R398_KALE_CATI_VE_PAVYON_BAGLANTI_ADAY_v001.blend',accepted=False,published=False,publicRevision='R314 unchanged',museumGeometryPreserved=True,changes=[
 'Corrected Fort metal-roof outline using R336 visual boundary and classified transverse sections R385/R386; independently authored two metal planes, ledge, inner parapet and coping.',
 'Independent four-zone analytic earth cover replaces inherited sampled surface above x+y=-100; 225 held-out classified controls, RMS 0.055868m, max 0.226968m. Regular architectural tessellation, no scan vertices/faces/photo texture transferred.',
 '29 inherited fort exterior masonry eave vertices joined to the new analytic roof profile.',
 '38 closed contact wedges join the previously cut pavilion terrain boundary to R363 floor. All five former gap rays now hit geometry; surrounding terrain and measured floors remain unchanged.',
 '118 independent standing-seam strips on metal roof. Spacing 0.55m is visual estimate, not surveyed.'
],verification=dict(inheritance='reports/R398_INHERITANCE.json',unchangedInheritedMeshes=18104,unexpectedChanges=[],meshAndGLB='reports/R398_ROOF_CONTACT.json',newClosedMeshObjects=8,glbErrors=[],gapRays='reports/R397_GRADE_CONTACT.json'),rejected=[
 'R388 whole-earth cubic field failed; not applied.',
 'R394 whole tower-end shoulder failed; not applied.',
 'R396 all-edge terrain blend worsened independent grade RMS .268 to .363m; not inherited by R397/R398.'
],remaining=[
 'Tower-end earth cover below x+y=-100 is still inherited. R399 shows a separate approximately 1.5m forecourt plane (28 held-out controls RMS .0191m/max .0376m); its exact outline and transition to the raised shoulders must be traced before replacement. Do not fit the whole end as one continuous shoulder: distinct levels exist.',
 'Historic fort side-wall round/arched openings and coping forms visible in photo086 remain missing or simplified. Independent architectural reconstruction still required.',
 'Pavilion inner retaining continuation, west terrace grade contact, museum base interfaces, northern/eastern ruin coping and all marked perimeter not yet source-accepted.',
 'R397 closes artificial terrain-cut gaps only; it is not proof that all adjacent terrain elevations are correct.',
 'Material fidelity, end junction, source views and whole-ring visual acceptance remain incomplete. No full/birebir/100% claim.'
],sourceViews=['renders/qa/R336_fort_roof_source.png','renders/qa/R368_pavilion_oblique_source.png'],candidateViews=['renders/qa/R398_fort_roof_candidate.png','renders/qa/R397_pavilion_contact_candidate.png'],photo='05_Dis_Mekan/Tarihi_Duvarlarla_Iliski/086_Muze_ve_tarihi_sur_duvarlari_ArchEyes.jpg',localGLB='exports/r152_clean/r398_fort_pavilion_REVIEW.glb')
(R/'reports/R398_MUSEUM_RING_WORK_STATE.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
p=R/'config/context_reconstruction_queue.json';q=json.loads(p.read_text(encoding='utf-8-sig'));q['current_local_checkpoint']=dict(scene=state['scene'],report='reports/R398_MUSEUM_RING_WORK_STATE.json',accepted=False,published=False,museum_geometry_preserved=True,authored_row_already_in_master=True,next_geometry=state['remaining'][0]);q['next_actions']=[
 'Use R398 local technical candidate. R389 corrected stepped metal roof/ledge/parapet, R392 four-zone independent earth cover, R397 pavilion cut-edge closure and R398 standing seams included. Source acceptance of whole ring is still absent.',
 state['remaining'][0],
 'Use source photo086 for visible fort wall openings/coping; photo088 for pavilion levels. Keep source-derived openings; do not seal real voids.',
 'Do not apply R396 terrain smoothing: it made classified ground agreement worse. R398 terrain is identical to R378, only a separate closed contact object was added.',
 'Exporter must include R321,R322,R325,R326,R327,R328,R331,R348,R361,R363,R378,R389,R392,R397,R398 SITE layers and respect hidden replaced R154 metal/upstand. Do not duplicate authored row.',
 *state['remaining'][1:]
];q['completion_claim']=False;p.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');print('R398 checkpoint recorded; no completion/publication claim.')
