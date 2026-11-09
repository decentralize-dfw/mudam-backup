from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';caps=json.loads((D/'dormer_caps_33.json').read_text())['caps'][:4];base=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'][0]['base'];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_CATI_CIKMALARI_ADAY_v012.blend'));o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data);vv=[];ff=[];mm=[];removed=[]
def face(v,m):
 n=len(vv);vv.extend(tuple(x) for x in v);ff.append(list(range(n,n+len(v))));mm.append(m)
for c,py in zip(caps,[401,399,397,395]):
 q=[Vector((*p,z)) for p,z in zip(c['xy'],c['z'])];bottom=base+7.5+(500-py)*26/1600
 def inside(v):return all((b.x-a.x)*(v.y-a.y)-(b.y-a.y)*(v.x-a.x)<1e-5 for a,b in zip(q,q[1:]+q[:1]))
 fs=[f for f in bm.faces if inside(f.calc_center_median()) and bottom-.08<f.calc_center_median().z<max(p.z for p in q)+.4];removed.append(len(fs));bmesh.ops.delete(bm,geom=fs,context='FACES')
 lower=[Vector((p.x,p.y,bottom)) for p in q]
 for i,j in [(1,2),(2,3),(3,0)]:face([lower[i],lower[j],q[j],q[i]],0)
 # Front border is traced cap width; 0.10m frame is an explicit modeling assumption.
 a,b=q[0],q[1];t=(b-a).normalized();out=Vector((t.y,-t.x,0)).normalized();ia=a+t*.1+Vector((0,0,-.1));ib=b-t*.1+Vector((0,0,-.1));la=Vector((ia.x,ia.y,bottom+.1));lb=Vector((ib.x,ib.y,bottom+.1))
 face([lower[0],lower[1],lb,la],1);face([la,lb,ib,ia],2);face([a,ia,ib,b],1);face([lower[0],la,ia,a],1);face([lb,lower[1],b,ib],1)
bm.to_mesh(o.data);bm.free();o.data.update();me=bpy.data.meshes.new('R169_33_REAR_DORMER_FRONTS');me.from_pydata(vv,[],ff);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
for name in ['R169_33_CLEAN_UPPER_ROOF','R169_33_PALE_WINDOW_REVEALS','R169_33_DARK_GLAZING']:me.materials.append(next(m for m in bpy.data.materials if m.name.startswith(name)))
for p,m in zip(me.polygons,mm):p.material_index=m
scene=R/'scenes/MUDAM_R169_CATI_CIKMALARI_ADAY_v013.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(23,-240,-47);s.camera.rotation_euler=(Vector((38,-273,-65))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=30;s.render.filepath=str(R/'renders/qa/R169_33_rear_dormers_v013.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_DORMERS_v013.json').write_text(json.dumps(dict(scene=scene.name,accepted=False,published=False,reopened=True,removed_faces=removed,source='Top cap footprints + R169_33_roof_elevation_1_source.png bottom pixels 401,399,397,395',assumptions=['0.10m frame section','Opaque glazing proxy material'],remaining=['Dormer-to-mansard junction needs correction','Front roof dormers','Right balcony','Rear lower facade and entrances','Other six buildings']),indent=2));print('REAR_DORMERS_BUILT',removed)

