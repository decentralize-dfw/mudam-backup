from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1];repo=R.parent
report=json.loads((R/'reports/R185_R188_COMPRESSED_CANDIDATE.json').read_text())
reopen=json.loads((R/'reports/R185_R188_COMPRESSED_REOPEN.json').read_text())
assert reopen['reopened'] and reopen['degenerate']==0 and reopen['triangles']==report['triangles']
assert len(reopen['background_buildings'])==7
target=repo/'demo/model/cevre3/authored-district.glb';data=(R/'exports/r152_clean/r185_r188_district_draco_webp_REVIEW.glb').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(target.read_bytes())==report['baseSha256'],'Production base changed'
assert sha(data)==report['sha256'] and len(data)==report['bytes']
m=repo/'demo/data/cevre3.json';manifest=json.loads(m.read_text())
manifest['revision']='R185-R188-road9-background-masses'
manifest['source']='Existing Context3 and134 abstract lower-district masses preserved. Region9 copied overhang replaced with independently modeled OSM road/footway/marking geometry. Added7 closed, source-footprint simple outside-scan masses with OSM tagged heights as requested for regions7-8. Full11-region work remains incomplete; detailed fort, northern buildings, station and courtyard candidates are excluded.'
manifest['files']['district'].update(bytes=len(data),sha256=sha(data),triangles=report['triangles'],sourceTriangles=report['triangles'],bounds=report['bounds'],sourceSha256=sha(data),degenerateRemoved=4)
target.write_bytes(data);m.write_text(json.dumps(manifest,indent=2)+'\n')
report.update(acceptedForPublication=True,acceptedScope='Region9 bounded correction and7 explicitly permitted abstract outside-scan masses; not full11-region acceptance',dateUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),revision=manifest['revision'])
(R/'reports/R185_R188_PUBLICATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(manifest['revision'],len(data),sha(data))
