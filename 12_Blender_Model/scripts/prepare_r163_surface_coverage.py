from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[1]
source=Image.open(R/'textures/R163_ACT_registered_surface.png').convert('RGBA')
old=Image.open(R/'textures/R157_landcover_atlas.jpg').convert('RGB')
w,h=source.size;xs=np.linspace(0,old.width-1,w);ys=np.clip((675-np.linspace(675,-475,h)-25)/1100*(old.height-1),0,old.height-1)
# Existing material only outside actual source coverage; no invented scan data.
a=np.asarray(old);fallback=Image.fromarray(a[np.rint(ys).astype(int)[:,None],np.rint(xs).astype(int)[None,:]]).convert('RGBA');fallback.alpha_composite(source);fallback.convert('RGB').save(R/'textures/R163_surface_with_existing_fallback.png')
report={'source_covered_pixels':int((np.asarray(source)[:,:,3]>0).sum()),'total_pixels':w*h,'outside_source':'Existing R157 landcover material retained; not scan-matched.'}
(R/'reports/R163_COVERAGE.json').write_text(json.dumps(report,indent=2));print(report)
