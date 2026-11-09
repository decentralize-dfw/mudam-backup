from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];b=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'][0];ring=[Vector((x,y,0)) for x,y in b['rings'][0][:-1]];a,bb=ring[1:3];t=(bb-a).normalized();inside=Vector((t.y,-t.x,0));out=-inside;right=Vector((-out.y,out.x,0));center=(a+bb)/2;base=b['base'];rects=[(1150,516,1212,633),(1300,513,1378,636),(1150,686,1224,807),(1300,687,1380,808)];windows=[((x0-800)*26/1600,(x1-800)*26/1600,base+7.5+(500-y1)*26/1600,base+7.5+(500-y0)*26/1600) for x0,y0,x1,y1 in rects]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_UST_CATI_YENIDEN_ADAY_v016.blend'));o=next(o for o in bpy.data.objects if o.name.startswith('R169_33_FRONT_REBUILT'));bm=bmesh.new();bm.from_mesh(o.data);old=[f for f in bm.faces if all(abs((v.co-center).dot(out))<1e-4 for v in f.verts)];assert len(old)>0;us=[(v.co-center).dot(right) for f in old for v in f.verts];zs=[v.co.z for f in old for v in f.verts];left,end=min(us),max(us);bottom,top=min(zs),max(zs);removed=len(old);bmesh.ops.delete(bm,geom=old,context='FACES');bm.to_mesh(o.data);bm.free();vv=[];ff=[];mi=[]
def pos(u,z,d=0):return tuple(center+right*u+out*d+Vector((0,0,z)))
def quad(q,m):
 n=len(vv);vv.extend(q);ff.append(list(range(n,n+4)));mi.append(m)
def panel(u0,u1,z0,z1,d,m):quad([pos(u0,z0,d),pos(u1,z0,d),pos(u1,z1,d),pos(u0,z1,d)],m)
xs=sorted(set([left,end]+[x for w in windows for x in w[:2]]));zz=sorted(set([bottom,top]+[z for w in windows for z in w[2:]]))
for u0,u1 in zip(xs,xs[1:]):
 for z0,z1 in zip(zz,zz[1:]):
  if not any(w[0]<(u0+u1)/2<w[1] and w[2]<(z0+z1)/2<w[3] for w in windows):panel(u0,u1,z0,z1,0,0)
for u0,u1,z0,z1 in windows:
 panel(u0,u1,z0,z1,-.12,2)
 for q in [[pos(u0,z0),pos(u0,z1),pos(u0,z1,-.12),pos(u0,z0,-.12)],[pos(u1,z0),pos(u1,z0,-.12),pos(u1,z1,-.12),pos(u1,z1)],[pos(u0,z0),pos(u0,z0,-.12),pos(u1,z0,-.12),pos(u1,z0)],[pos(u0,z1),pos(u1,z1),pos(u1,z1,-.12),pos(u0,z1,-.12)]]:quad(q,1)
 for x0,x1,zlo,zhi in [(u0,u0+.055,z0,z1),(u1-.055,u1,z0,z1),(u0,u1,z0,z0+.055),(u0,u1,z1-.055,z1)]:panel(x0,x1,zlo,zhi,-.035,1)
me=bpy.data.meshes.new('R169_33_REAR_VISIBLE_OPENINGS');me.from_pydata(vv,[],ff);me.update();obj=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(obj)
for prefix in ['R169_33_IVORY_RENDER','R169_33_PALE_WINDOW_REVEALS','R169_33_DARK_GLAZING']:me.materials.append(next(m for m in bpy.data.materials if m.name.startswith(prefix)))
for p,m in zip(me.polygons,mi):p.material_index=m
scene=R/'scenes/MUDAM_R169_ARKA_CEPHE_ADAY_v017.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));# Isolate the target for review only, after saving the complete scene.
context=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(context.data);drop=[f for f in bm.faces if not(25<f.calc_center_median().x<51 and -284<f.calc_center_median().y<-261)];bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(context.data);bm.free()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1600;s.render.resolution_y=1000;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=1;target=center+Vector((0,0,base+7.5));bpy.ops.object.light_add(type='AREA');bpy.context.object.location=target+out*20+Vector((0,0,8));bpy.context.object.rotation_euler=(target-bpy.context.object.location).to_track_quat('-Z','Y').to_euler();bpy.context.object.data.energy=5000;bpy.context.object.data.size=15;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=target+out*35;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=26;s.render.filepath=str(R/'renders/qa/R169_33_rear_windows_v017.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_REAR_FACADE_v017.json').write_text(json.dumps(dict(scene=scene.name,reopened=True,accepted=False,published=False,openings=4,source='R169_33_facade_1_source.png',source_pixels=rects,removed_plain_wall_faces=removed,assumptions=['0.12m recess, 0.055m frame are model assumptions','Upper left traced opening partly occluded in scan; extent needs independent validation','Existing rear wall depth retained; source facade camera depth offset does not affect orthographic lateral registration'],remaining=['Occluded left and middle rear facade','Roof/mansard and front dormers','Right balcony and entrances']),indent=2));print('REAR_OPENINGS_BUILT',removed)

