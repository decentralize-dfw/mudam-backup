from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R155_MELIA_CEVRE_v002.blend'))
r=json.loads((R/'reports/R155_BUILD.json').read_text())
def signature(o):return hashlib.sha256(str((tuple(o.matrix_world),[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
changes=[n for n,h in r['inherited_signatures'].items() if n not in bpy.data.objects or signature(bpy.data.objects[n])!=h]
new=[o for o in bpy.context.scene.objects if o.name.startswith('R155_') and o.type=='MESH']
zero=[o.name for o in new if any(p.area<1e-9 for p in o.data.polygons)]
result=dict(reopened=True,scene=r['scene'],inherited_changes=changes,zero_area_objects=zero,new_objects=len(new),new_triangles=sum(len(p.vertices)-2 for o in new for p in o.data.polygons),scope='New hotel meshes and inherited museum/terrain geometry only; not full architectural acceptance')
(R/'reports/R155_QA.json').write_text(json.dumps(result,indent=2));assert not changes and not zero;print('R155_QA_PASS',flush=True)
