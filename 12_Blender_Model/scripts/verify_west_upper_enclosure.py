"""Accept only matching reopened-scene geometry, route and dense enclosure evidence."""
from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R85_build_report.json').read_text());fail=[];checks={}
for name in ['R85_global_audit.json','R85_inherited_verification.json','R23_regression_on_R85.json']:
 q=json.loads((B/'reports'/name).read_text());assert q['file']==r['file'];checks[name]=len(q['failures']);fail.extend(q['failures'])
d=json.loads((B/'reports/R85_enclosure_dense_summary.json').read_text());assert d['file']==r['file'];rows=[s for s in d['summaries'] if s['region'] in ['WEST_UPPER_LANDING','WEST_UPPER_RETURN_0','WEST_UPPER_RETURN_1']];assert len(rows)==3
for s in rows:
 if s['floor_missing'] or s['cover_missing'] or s['side_escape_samples']:fail.append(s)
q=dict(file=r['file'],reopened_evidence=checks,dense_regions=rows,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R85_verification.json').write_text(json.dumps(q,indent=2));print('R85',sum(s['samples'] for s in rows),'dense region samples',len(fail),'failures');assert not fail
