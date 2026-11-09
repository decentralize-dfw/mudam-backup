from pathlib import Path
import bpy,json,math,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';b=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'][0];p=[Vector((x,y,0)) for x,y in b['rings'][0][:-1]];t=(p[0]-p[3]).normalized();inside=Vector((t.y,-t.x,0));out=-inside;right=Vector((-out.y,out.x,0));center=(p[0]+p[3])*.5+inside*(-.45);base=b['base']
rows=np.array(json.loads((D/'balcony_profile_33.json').read_text())['profile']);q=rows[(rows[:,0]>=-10.5)&(rows[:,0]<=-6.3)];coef=np.polyfit(q[:,0],q[:,1],3);us=np.linspace(q[0,0],q[-1,0],25);ds=np.polyval(coef,us);rmse=float(np.sqrt(np.mean((np.polyval(coef,q[:,0])-q[:,1])**2)))
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_CEPHE_CATI_ADAY_v007.blend'))
v=[];f=[];mi=[]
def pos(u,d,z):return tuple(center+right*float(u)+out*float(d)+Vector((0,0,float(z))))
def face(points,mat):
 k=len(v);v.extend(points);f.append(list(range(k,k+len(points))));mi.append(mat)
for z in [base+2.3,base+5.35]:
 for i in range(len(us)-1):
  u0,u1=us[i:i+2];d0,d1=ds[i:i+2]
  face([pos(u0,0,z),pos(u1,0,z),pos(u1,d1,z),pos(u0,d0,z)],0)
  face([pos(u0,d0,z-.12),pos(u1,d1,z-.12),pos(u1,d1,z),pos(u0,d0,z)],0)
  face([pos(u0,0,z-.12),pos(u0,d0,z-.12),pos(u1,d1,z-.12),pos(u1,0,z-.12)],0)
  face([pos(u0,d0,z+.14),pos(u1,d1,z+.14),pos(u1,d1,z+1.08),pos(u0,d0,z+1.08)],1)
  for h in [.15,.58,1.08]:
   face([pos(u0,d0+.012,z+h),pos(u1,d1+.012,z+h),pos(u1,d1+.012,z+h+.055),pos(u0,d0+.012,z+h+.055)],0)
 for i in [0,-1]:
  u,d=us[i],ds[i];face([pos(u,0,z-.12),pos(u,d,z-.12),pos(u,d,z),pos(u,0,z)],0);face([pos(u,0,z+.14),pos(u,d,z+.14),pos(u,d,z+1.08),pos(u,0,z+1.08)],1)
me=bpy.data.meshes.new('R169_33_LEFT_BALCONIES');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o)
for n in ['R169_33_PALE_WINDOW_REVEALS','R169_33_BALCONY_DARK_INFILL']:me.materials.append(bpy.data.materials[n])
for poly,m in zip(me.polygons,mi):poly.material_index=m
# Preserve transparent evidence on which dimensions are traced versus provisional.
o['source']='ACT front profile u=-10.5..-6.3m, z=base+5.0..6.2m; cubic least-squares curve';o['assumptions']='0.12m slab thickness, railing construction and lower-level depth reused pending separate evidence'
outfile=R/'scenes/MUDAM_R169_CEPHE_BALKON_ADAY_v008.blend';bpy.ops.wm.save_as_mainfile(filepath=str(outfile),compress=True);bpy.ops.wm.open_mainfile(filepath=str(outfile))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('QA');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
bpy.ops.object.light_add(type='AREA');light=bpy.context.object;light.location=center+out*25+Vector((0,0,base+18));target=center+Vector((0,0,base+6));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=4500;light.data.shape='DISK';light.data.size=15
bpy.ops.object.camera_add();s.camera=bpy.context.object;target=center+Vector((0,0,base+7.5));s.camera.location=target+out*35;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=26;s.render.filepath=str(R/'renders/qa/R169_33_front_geometry_v008.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_BALCONY_GEOMETRY_v008.json').write_text(json.dumps(dict(scene=outfile.name,accepted=False,published=False,reopened=True,curve_sample_count=len(q),curve_fit_rmse_m=rmse,balcony_levels_relative_m=[2.3,5.35],assumptions=['Slab thickness 0.12m, railing band dimensions are modeling assumptions','Lower balcony depth repeats upper sampled curve pending verification'],remaining=['Right balcony and entrances','Other facades','Roof dormers and junctions','Full source comparison and GLB validation before publication']),indent=2));print('BALCONY_GEOMETRY',rmse)
