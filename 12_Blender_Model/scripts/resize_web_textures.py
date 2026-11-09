"""Resize copied texture payloads without modifying source images."""
import json,sys
from pathlib import Path
from PIL import Image
p=Path(sys.argv[1]);rows=json.loads(p.read_text())
for r in rows:
 im=Image.open(r['input']);im.thumbnail((r['cap'],r['cap']),Image.Resampling.LANCZOS)
 if r['jpeg']:
  im.convert('RGB').save(r['output'],quality=82,optimize=True,subsampling=0)
 else:im.save(r['output'],format='PNG',optimize=True)
 r.update(after_size=list(im.size),after_bytes=Path(r['output']).stat().st_size)
p.write_text(json.dumps(rows,indent=2))
