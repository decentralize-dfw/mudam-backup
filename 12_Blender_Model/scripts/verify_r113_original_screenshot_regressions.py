"""Re-run the original marked-issue probes on R113, retaining original source data."""
from pathlib import Path
import json
B=Path(__file__).resolve().parents[1];scene=json.loads((B/'reports/R113_build_report.json').read_text())['file'];results=[]
for script,revision in [('verify_five_screenshot_repairs.py','R95'),('verify_north_frame_alignment.py','R93')]:
 p=B/'scripts'/script;s=p.read_text();needle="bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))"
 assert needle in s
 s=s.replace(needle,"r['file']="+repr(scene)+";"+needle,1)
 output=f'R113_{revision}_screenshot_regression.json';s=s.replace(f'{revision}_verification.json',output)
 exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
 q=json.loads((B/'reports'/output).read_text());assert q['file']==scene and not q['failures'];results.append(output)
(B/'reports/R113_original_screenshot_regressions.json').write_text(json.dumps(dict(file=scene,reports=results,failures=[],limits=['Original issue probes only; not whole-building acceptance.']),indent=2))
