"""Portable static web folder; no authoring scene or unbatched archives."""
from pathlib import Path
import json,zipfile
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'config/r151_web_lod.json').read_text())
checks=[json.loads((R/ (l['url'].removeprefix('../').removesuffix('.gz')+'.verification.json')).read_text()) for l in manifest['layers']]
assert all(not r['failures'] for r in checks)
assert not json.loads((R/'reports/R151_WEB_LOD_verification.json').read_text())['failures']
out=R/'exports/MUDAM_R151_WEB_CLEAN_PAKETI_v002.zip'
files=[R/'WEB_HAFIF.html',R/'assets/web-lod-viewer.mjs',R/'assets/performance-review.mjs',R/'config/r151_web_lod.json']+list((R/'assets/vendor/three').glob('*.js'))+[R/l['url'].removeprefix('../') for l in manifest['layers']]
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:
  if p.name=='WEB_HAFIF.html':z.writestr(p.name,p.read_text().replace('MODEL_INCELEME.html','WEB_HAFIF.html'))
  else:z.write(p,p.relative_to(R).as_posix())
 z.writestr('README.txt','MUDAM R151 WEB LOD\nServe this folder using HTTP/HTTPS and open WEB_HAFIF.html.\nExample: python -m http.server 8000\nBuilding and near context load first. Far context loads on demand.\nContext source: ACT Luxembourg mesh3D 2020, CC0.\nOriginal v011 authoring scene is not modified or included.\nThis package is a visual LOD, not a completed architectural survey.\n')
print('WEB_PACKAGE',out.stat().st_size,str(out))
