from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';rows=[r for r in json.loads((D/'row_eave_normal_samples.json').read_text()) if r['edge']==2 and r['inset']==0];a=Vector((rows[0]['x'],rows[0]['y'],0));b=Vector((rows[-1]['x'],rows[-1]['y'],0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));n=n if (Vector((-67,-299,0))-a).dot(n)>0 else -n
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_KAYNAK_SACAK_ADAY_v026.blend'));o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data);out=[]
for e in bm.edges:
 if not e.is_boundary:continue
 p=(e.verts[0].co+e.verts[1].co)/2;u=(p-a).dot(t);d=(p-a).dot(n)
 if 0<u<(b-a).length and abs(d)<1 and -67<p.z<-62:out.append(dict(u=u,d=d,z=p.z,coords=[list(v.co) for v in e.verts],normal=list(e.link_faces[0].normal)))
(D/'row_wall_top_boundary.json').write_text(json.dumps(out,indent=2));print('BOUNDARY',len(out));print(json.dumps(out[:12],indent=1))
