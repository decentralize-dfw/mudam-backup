from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent
r=json.loads((B/'reports/R115_build_report.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/r['file']))
fail=[];checks=[]
for row in r['parts']:
    ob=bpy.data.objects[row['name']];bm=bmesh.new();bm.from_mesh(ob.data)
    if any(not e.is_manifold for e in bm.edges) or bm.calc_volume()<=0:fail.append(ob.name)
    bm.free()
    u0,u1,d0,d1,v0,v1=row['bounds'];p=Vector(row['origin']);x=Vector(row['x']);y=Vector(row['y']);z=Vector((0,0,1))
    # Test the physical retention chain through the glass overlap, at each edge.
    u=(u0+u1)/2;v=(v0+v1)/2
    if row['name'].endswith('_LEFT'):u=.004
    elif row['name'].endswith('_RIGHT'):u=u0+.004
    elif row['name'].endswith('_BOTTOM'):v=.004
    else:v=v0+.004
    target=p+x*u+z*v
    for kind,host in [('glass',bpy.data.objects[row['host']])]:
        inv=host.matrix_world.inverted();a=target+y*.1;d=-y
        hit=host.ray_cast(inv@a,(inv.to_3x3()@d).normalized(),distance=.2)[0]
        checks.append(dict(part=ob.name,glass_overlap=hit))
        if not hit:fail.append(ob.name+' misses glass')
result=dict(file=r['file'],failures=fail,parts=len(r['parts']),panes=len(r['panes']),glass_contact_checks=checks,construction_acceptance=False)
(B/'reports/R115_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('R115 verification',len(checks),'contacts; failures',fail)
assert not fail
