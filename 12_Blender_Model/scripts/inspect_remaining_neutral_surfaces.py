from pathlib import Path
import bpy,json,sys
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;rev=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'R143';r=json.loads((B/'reports'/f'{rev}_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get():continue
 groups={};nm=o.matrix_world.to_3x3().inverted().transposed()
 for f in o.data.polygons:
  m=o.data.materials[f.material_index].name
  if m not in ['P05_NEUTRAL_ENVELOPE','P05_FLOOR_REFERENCE']:continue
  n=(nm@f.normal).normalized();kind='top' if n.z>.9 else 'bottom' if n.z<-.9 else 'side';groups[kind]=groups.get(kind,0)+f.area
 if groups:out.append(dict(name=o.name,areas=groups,sources=o.get('source_ids',''),limits=o.get('status','')))
(B/'.local_source_cache'/f'{rev.lower()}_remaining_neutral.json').write_text(json.dumps(out,indent=2))
for x in out:
 if x['areas'].get('top',0)>1:print(x)
