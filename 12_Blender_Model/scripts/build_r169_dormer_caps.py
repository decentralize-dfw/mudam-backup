from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';data=json.loads((D/'dormer_caps_33.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_TEMIZ_CATI_ADAY_v011.blend'));o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data);verts=[];faces=[];counts=[]
for cap in data['caps'][:4]:
 q=[Vector((*p,z)) for p,z in zip(cap['xy'],cap['z'])];normal=(q[1]-q[0]).cross(q[2]-q[0]).normalized()
 def height(v):return q[0].z-(normal.x*(v.x-q[0].x)+normal.y*(v.y-q[0].y))/normal.z
 def inside(v,tol=1e-5):return all((b.x-a.x)*(v.y-a.y)-(b.y-a.y)*(v.x-a.x)<tol for a,b in zip(q,q[1:]+q[:1]))
 for a,b in zip(q,q[1:]+q[:1]):
  n=Vector((-(b.y-a.y),b.x-a.x,0)).normalized();fs=[f for f in bm.faces if 25<f.calc_center_median().x<51 and -284<f.calc_center_median().y<-261 and f.calc_center_median().z>-64];es=set(e for f in fs for e in f.edges);vs=set(v for f in fs for v in f.verts);bmesh.ops.bisect_plane(bm,geom=list(fs)+list(es)+list(vs),dist=1e-6,plane_co=a,plane_no=n)
 fs=[f for f in bm.faces if inside(f.calc_center_median()) and abs(f.calc_center_median().z-height(f.calc_center_median()))<.4];counts.append(len(fs));bmesh.ops.delete(bm,geom=fs,context='FACES')
 for v in bm.verts:
  if inside(v.co,1e-4) and abs(v.co.z-height(v.co))<.4:v.co.z=height(v.co)
 i=len(verts);verts.extend(tuple(p) for p in q);faces.append([i+3,i+2,i+1,i])
# Split operations can leave zero-area fragments; remove only these fragments.
small=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=small,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update()
mesh=bpy.data.meshes.new('R169_33_TRACED_REAR_DORMER_CAPS');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(bpy.data.materials['R169_33_CLEAN_UPPER_ROOF'])
scene=R/'scenes/MUDAM_R169_CATI_CIKMALARI_ADAY_v012.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(38,-273,0);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=29;s.render.filepath=str(R/'renders/qa/R169_33_roof_v012.png');bpy.ops.render.render(write_still=True)
report=dict(scene=scene.name,reopened=True,accepted=False,published=False,reconstructed_caps=4,removed_faces=counts,source=data,limits=['Front three cap samples mix slope surfaces; excluded','Roof skirt, dormer cheeks/glazing, right balcony, rear and entrances unfinished','Manual trace is source-grounded candidate, not survey'])
(R/'reports/R169_DORMER_CAPS_v012.json').write_text(json.dumps(report,indent=2));print('DORMER_CAPS_BUILT',counts)
