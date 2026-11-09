from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r169/row_rear_dormer_cap_trials.json').read_text())[0];assert d['p90']<.02;a,b,c=d['plane'];ring=[Vector((-68.10883331298828+(x-700)/175,-293.02964782714844+(700-y)/175,0)) for x,y in d['pixels']]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_CATI_UZANTI_ADAY_v039.blend'));o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data)
for p,q in zip(ring,ring[1:]+ring[:1]):
 fs=[f for f in bm.faces if -73<f.calc_center_median().x<-68 and -296<f.calc_center_median().y<-291 and f.calc_center_median().z>-65]
 es={e for f in fs for e in f.edges};vs={v for f in fs for v in f.verts};bmesh.ops.bisect_plane(bm,geom=list(fs)+list(es)+list(vs),dist=1e-6,plane_co=p,plane_no=Vector((q.y-p.y,p.x-q.x,0)))
def inside(p):
 cr=[(q.x-v.x)*(p.y-v.y)-(q.y-v.y)*(p.x-v.x) for v,q in zip(ring,ring[1:]+ring[:1])];return min(cr)>-1e-5 or max(cr)<1e-5
drop=[f for f in bm.faces if inside(f.calc_center_median()) and f.normal.z>.5 and abs(f.calc_center_median().z-(a*f.calc_center_median().x+b*f.calc_center_median().y+c))<.12];count=len(drop);assert count>0
bmesh.ops.delete(bm,geom=drop,context='FACES');bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(o.data);bm.free()
me=bpy.data.meshes.new('R169_ROW_MEASURED_REAR_CAP');me.from_pydata([(p.x,p.y,a*p.x+b*p.y+c) for p in ring],[],[(0,1,2,3)]);me.materials.append(bpy.data.objects['R169_ROW_CONTINUOUS_HIP'].data.materials[0]);ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);bm=bmesh.new();bm.from_mesh(me);bm.normal_update()
for f in bm.faces:
 if f.normal.z<0:f.normal_flip()
bm.to_mesh(me);bm.free();out=R/'scenes/MUDAM_R169_ARKA_PENCERE_ORTUSU_ADAY_v041.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R169_REAR_CAP_v041.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,removed_faces=count,source=d,limits=['One shallow source-supported cap only; outline manually traced and approximate','Second proposed cap has steep slope and is excluded as potentially main roof','Glazed front and side joints not reconstructed; no whole dormer acceptance','Cap thickness unknown; no invented solid section']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-285,-48);s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_rear_cap_v041.png');bpy.ops.render.render(write_still=True)






