from pathlib import Path
import json,numpy as np
R=Path('12_Blender_Model');D=R/'.local_source_cache/r169'
a=json.loads((R/'config/r169_building_targets.json').read_text());m={b['id']:b for b in json.loads((D/'facade_plane_modes.json').read_text())};changes=[]
for b in a['buildings']:
 p=np.array(b['rings'][0][:-1]);norm=[];rhs=[];used=[]
 for i,(v,w) in enumerate(zip(p,np.roll(p,-1,axis=0))):
  t=(w-v)/np.linalg.norm(w-v);n=np.array([t[1],-t[0]]);e=next((x for x in m[b['id']]['edges'] if x['edge']==i),None);offset=0
  if e and e['support']>=.7 and e['area']>=20 and e['samples']>=50:
   offset=e['mode'];used.append(dict(edge=i,offset=offset,support=e['support']))
  norm.append(n);rhs.append(n@v+offset)
 q=[np.linalg.solve(np.array([norm[(i-1)%len(p)],norm[i]]),np.array([rhs[(i-1)%len(p)],rhs[i]] )).tolist() for i in range(len(p))]
 b['rings']=[q+[q[0]]];b['source']='OSM starting outline; only coherent ACT facade plane offsets applied (70% area support within 0.25m, >=20m2). Candidate, not survey.';changes.append(dict(id=b['id'],applied=used))
(D/'targets_v004.json').write_text(json.dumps(a,indent=2));(D/'geometry_changes_v004.json').write_text(json.dumps(changes,indent=2));print(changes)
s=(R/'scripts/prepare_r169_buildings.py').read_text().replace("R/'config/r169_building_targets.json'","D/'targets_v004.json'").replace("D/'mesh.json'","D/'mesh_v004.json'")
s=s.replace('Clipped grid covers exact OSM outline; OSM/ACT survey alignment not guaranteed.','Selected coherent ACT wall planes adjust starting OSM footprint. Roof samples are interpolated on corrected outline; candidate only.')
(R/'scripts/prepare_r169_v004.py').write_text(s)
s=(R/'scripts/build_r169_buildings.py').read_text().replace("D/'mesh.json'","D/'mesh_v004.json'").replace('ADAY_v001.blend','ADAY_v004.blend').replace('R169_source_color.png','R169_source_color_v004.png').replace('R169_CANDIDATE.json','R169_CANDIDATE_v004.json')
(R/'scripts/build_r169_v004.py').write_text(s)
