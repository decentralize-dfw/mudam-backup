"""Compare inherited geometry exactly; CLI: build-report output-report allowed names."""
from pathlib import Path
import bpy,json,sys,hashlib
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';args=sys.argv[sys.argv.index('--')+1:];r=json.loads((B/'reports'/args[0]).read_text());base=r['base_scene'];base=base if '/' in base else '12_Blender_Model/scenes/'+base;allowed=set(r['changed_inherited_objects']) if args[2:]==['@reported'] else set(args[2:])
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(R/path));result={}
 for ob in bpy.context.scene.objects:
  if ob.type not in ['MESH','CURVE']:continue
  geom=([list(v.co) for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]) if ob.type=='MESH' else [(s.type,[list(p.co) for p in s.points],s.use_cyclic_u) for s in ob.data.splines]
  modifiers=[]
  for m in ob.modifiers:
   row=[m.name,m.type,m.show_viewport,m.show_render]
   for attr in ['operation','solver','thickness','offset','width','segments']:
    if hasattr(m,attr):row += [attr,getattr(m,attr)]
   if hasattr(m,'object'):row+=['object',m.object.name if m.object else None]
   modifiers.append(row)
  payload=[geom,[list(row) for row in ob.matrix_world],[m.name if m else None for m in ob.data.materials],ob.hide_render,ob.hide_get(),modifiers]
  result[ob.name]=hashlib.sha256(repr(payload).encode()).hexdigest()
 return result
before=snapshot(base);after=snapshot(r['file']);changed=[n for n,v in before.items() if after.get(n)!=v];fail=[n for n in changed if n not in allowed];unused=allowed-set(changed);result=dict(file=r['file'],base_scene=base,inherited_objects_checked=len(before),changed_inherited_objects=changed,allowed_changes=sorted(allowed),allowed_but_unchanged=sorted(unused),new_objects=sorted(after.keys()-before.keys()),failures=fail,construction_acceptance=False);(B/'reports'/args[1]).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(inherited=len(before),changed=changed,failures=fail),indent=2));assert not fail,fail
