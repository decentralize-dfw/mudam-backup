from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r169/row_whole_roof_samples_v053.json').read_text());targets=json.loads((R/'config/r169_building_targets.json').read_text()); ring=[Vector((*p,0)) for p in next(t for t in targets['buildings'] if t['id']=='164179202')['rings'][0][:-1]]; center=sum(ring,Vector())/len(ring); ring=[center+(p-center)*1.005 for p in ring]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v054.blend'))
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name not in ['R169_WHOLE_SOURCE_ROOF','R169_MEASURED_ENVELOPE']:bpy.data.objects.remove(ob,do_unlink=True)
o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data)
for a,b in zip(ring,ring[1:]+ring[:1]):
 bmesh.ops.bisect_plane(bm,geom=list(bm.faces)+list(bm.edges)+list(bm.verts),dist=1e-6,plane_co=a,plane_no=Vector((b.y-a.y,a.x-b.x,0)))
def inside(p):
 cr=[(b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x) for a,b in zip(ring,ring[1:]+ring[:1])];return min(cr)>-1e-5 or max(cr)<1e-5
bmesh.ops.delete(bm,geom=[f for f in bm.faces if not inside(f.calc_center_median())],context='FACES');bm.to_mesh(o.data);bm.free();o.name='R169_ROW_164179202_BODY'
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);roof=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];roof.select_set(True);bpy.context.view_layer.objects.active=roof;bpy.ops.object.join();roof.name='R169_WHOLE_SOURCE_ROOF'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_TEK_BINA_ADAY_v056.blend'),compress=True)
print('SINGLE_HOUSE',len(roof.data.vertices),len(roof.data.polygons))

