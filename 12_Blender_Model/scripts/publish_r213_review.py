from pathlib import Path
import json,hashlib,datetime
R=Path('12_Blender_Model');v=json.loads((R/'reports/R213_RELEASE_VALIDATION.json').read_text());assert len(v['files'])==3
m=Path('demo/data/cevre3.json');d=json.loads(m.read_text());d['revision']='R213-current-model-user-review';d['source']='Current independent modeling work through R213, published at explicit user request for review. Full eleven-region acceptance remains false. Existing ARCH row preserved. Inherited scan-derived older buildings/road patches still require replacement; this is not a fully authored or 90 percent matching completion.';d['reviewOnly']=True
for key,a in v['files'].items():
 assert a['decoded'] and a['zero']==0
 raw=Path(a['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==a['sha256']
 target=Path('demo/model/cevre3')/('authored-'+key+'.glb');target.write_bytes(raw)
 d['files'][key]=dict(file='model/cevre3/'+target.name+'?v='+a['sha256'][:12],bytes=a['bytes'],sha256=a['sha256'],triangles=a['triangles'],bounds=a['bounds'],textures=a['textures'],reviewOnly=True)
m.write_text(json.dumps(d,indent=2)+'\n')
p=R/'reports/R171_11_REGION_STATUS.json';s=json.loads(p.read_text());s.update(updatedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionRevision=d['revision'],productionCommit='pending current explicit push',localMaster=v['sourceScene'],fullScopeAccepted=False,similarityPercent=None)
for row in s['regions']:
 row['state']='published_review_incomplete'
 if row['id'] in [2,3]:row['state']='abstract_massing_published_ground_incomplete'
 if row['id'] in [7,8]:row['state']='simple_background_massing_published_connections_incomplete'
 if row['id']==9:row['state']='bounded_overhang_correction_published'
 if row['id'] in [5,6]:row['remaining']='Erasmus and other missing coverage; source-accurate facades, openings, roof details and hardscape. Six independent building shells technically closed; full source fidelity not accepted.'
 if row['id']==11:row['implemented']+='; R210 fourteen accidental ground holes repaired; R213 three source-traced access road surfaces added, southern concrete terrace unresolved'
s['technicalValidation']='Current three GLB payloads decoded after Draco/WebP, finite positions and zero degenerate triangles. Source fidelity acceptance is separate and incomplete.'
p.write_text(json.dumps(s,indent=2)+'\n')
q=R/'config/context_reconstruction_queue.json';j=json.loads(q.read_text());j['production_context']='R213 current model published for explicit user review; all eleven regions not accepted. See R213_RELEASE_VALIDATION.json and R171_11_REGION_STATUS.json.';j['next_actions'].insert(0,'Current master R213 v002. Resume missing Erasmus architecture (R214 measurements only), outstanding fort and bridge source checks, full hardscape and inherited scan-derived building replacements. User requested immediate current-state push and eleven-item status.');q.write_text(json.dumps(j,indent=2)+'\n')
print({k:a['bytes'] for k,a in v['files'].items()})
