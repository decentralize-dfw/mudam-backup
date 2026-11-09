from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r169/row_rear_dormer_cap_trials.json').read_text())[0];a,b,c=d['plane'];ring=[Vector((-68.10883331298828+(x-700)/175,-293.02964782714844+(700-y)/175,0)) for x,y in d['pixels']]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_PENCERE_ORTUSU_ADAY_v041.blend'));stats=[];vs=[];fs=[]
def inside(p):
 cr=[(q.x-v.x)*(p.y-v.y)-(q.y-v.y)*(p.x-v.x) for v,q in zip(ring,ring[1:]+ring[:1])];return min(cr)>-1e-5 or max(cr)<1e-5
for name in ['R169_ROW_CONTINUOUS_HIP','R169_ROW_REAR_ROOF_EXTENT']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data)
 for p,q in zip(ring,ring[1:]+ring[:1]):bmesh.ops.bisect_plane(bm,geom=list(bm.faces)+list(bm.edges)+list(bm.verts),dist=1e-6,plane_co=p,plane_no=Vector((q.y-p.y,p.x-q.x,0)))
 drop={f for f in bm.faces if inside(f.calc_center_median())};joins=0
 for e in bm.edges:
  if not any(f in drop for f in e.link_faces) or not any(f not in drop for f in e.link_faces):continue
  p,q=[v.co.copy() for v in e.verts];pp=Vector((p.x,p.y,a*p.x+b*p.y+c));qq=Vector((q.x,q.y,a*q.x+b*q.y+c));off=len(vs);vs.extend([tuple(p),tuple(q),tuple(qq),tuple(pp)]);fs.append([off+i for i in range(4)]);joins+=1
 stats.append(dict(object=name,removed_faces=len(drop),interface_edges=joins));bmesh.ops.delete(bm,geom=list(drop),context='FACES');bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(o.data);bm.free()
assert sum(r['removed_faces'] for r in stats)>0
me=bpy.data.meshes.new('R169_REAR_CAP_ROOF_INTERFACE');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.objects['R169_ROW_CONTINUOUS_HIP'].data.materials[0]);ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.normal_update();bm.to_mesh(me);bm.free()
out=R/'scenes/MUDAM_R169_ARKA_ORTU_BIRLESIM_ADAY_v042.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R169_REAR_INTERFACE_v042.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changes=stats,limits=['Interfaces connect existing authored roof to measured cap; not measured construction details','Source-visible front glazing remains unbuilt','Whole roof geometry remains unaccepted']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-285,-48);s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_rear_interface_v042.png');bpy.ops.render.render(write_still=True)







