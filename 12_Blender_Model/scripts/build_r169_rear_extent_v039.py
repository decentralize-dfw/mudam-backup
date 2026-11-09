from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
R=Path(__file__).resolve().parents[1];rows=json.loads((R/'.local_source_cache/r169/row_rear_extent_samples.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_YAN_BAGLANTI_ADAY_v038.blend'));vs=[];fs=[];used=[]
for j in range(1,10):
 t=j/10;a=next(r for r in rows if r['t']==t and r['inset']==0);b=next(r for r in rows if r['t']==t and r['inset']==-.5);assert abs(b['delta'])<.17
 vs.extend([(a['x'],a['y'],a['plane']),(b['x'],b['y'],b['source'])]);used.append(b)
for j in range(8):fs.append([2*j,2*j+1,2*j+3,2*j+2])
me=bpy.data.meshes.new('R169_ROW_REAR_ROOF_EXTENT');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.objects['R169_ROW_CONTINUOUS_HIP'].data.materials[0]);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.normal_update()
for f in bm.faces:
 if f.normal.z<0:f.normal_flip()
bm.to_mesh(me);bm.free();me.calc_loop_triangles();assert all(t.area>1e-9 for t in me.loop_triangles)
out=R/'scenes/MUDAM_R169_ARKA_CATI_UZANTI_ADAY_v039.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R169_REAR_EXTENT_v039.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,source_samples=used,width_m=.5,scope='Source-supported rear slope extension, t0.1..0.9 only',limits=['Full rear eave unresolved; .5m is verified sample distance, not actual total overhang','Inherited source fragments retained pending exact clipping; overlaps remain possible','Dormer caps/fronts still not reconstructed','No full-building acceptance']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-285,-48);s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_rear_extent_v039.png');bpy.ops.render.render(write_still=True)





