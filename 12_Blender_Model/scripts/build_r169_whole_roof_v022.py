from pathlib import Path
import bpy,bmesh,json,math,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'roof_planes_164179202.json').read_text());ang=float(np.load(D/'164179202.npz')['angle']);cs,sn=math.cos(ang),math.sin(ang);planes=[p['coeff'] for p in d['planes'][:3]];ring=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'][2]['rings'][0][:-1]
def local(p):return(cs*p[0]+sn*p[1],-sn*p[0]+cs*p[1])
def world(x,y,z):return(cs*x-sn*y,sn*x+cs*y,z)
def height(x,y):return min(a*x+b*y+c for a,b,c in planes)
def inside(p):
 hit=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>p.y)!=(b[1]>p.y) and p.x<(b[0]-a[0])*(p.y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
def clip(poly,a,b,c):
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp=a*p[0]+b*p[1]+c;dq=a*q[0]+b*q[1]+c
  if dp<=1e-8:out.append(p)
  if (dp<0)!=(dq<0):
   t=dp/(dp-dq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return out
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_SIRA_CATI_ADAY_v019.blend'));o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data)
# Split footprint boundaries before removing slope fragments; leave adjacent houses untouched.
for a,b in zip(ring,ring[1:]+ring[:1]):
 fs=[f for f in bm.faces if -74<f.calc_center_median().x<-59 and -308<f.calc_center_median().y<-290 and f.calc_center_median().z>-66]
 es=set(e for f in fs for e in f.edges);vs=set(v for f in fs for v in f.verts);bmesh.ops.bisect_plane(bm,geom=list(fs)+list(es)+list(vs),dist=1e-6,plane_co=Vector((a[0],a[1],0)),plane_no=Vector((b[1]-a[1],a[0]-b[0],0)))
drop=[];retained=0
for f in bm.faces:
 p=f.calc_center_median()
 if not inside(p):continue
 h=height(*local(p));delta=p.z-h
 if -.65<delta<.28 and f.normal.z>.15:drop.append(f)
 elif delta>=.28:retained+=1
removed=len(drop);bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(o.data);bm.free()
verts=[];faces=[]
for i,p in enumerate(planes):
 poly=[local(v) for v in ring]
 for j,q in enumerate(planes):
  if i!=j and poly:poly=clip(poly,*[a-b for a,b in zip(p,q)])
 if len(poly)<3:continue
 off=len(verts);verts.extend(world(x,y,height(x,y)) for x,y in poly);faces.append(list(range(off,off+len(poly))))
me=bpy.data.meshes.new('R169_ROW_CONTINUOUS_HIP');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);m=bpy.data.materials.new('R169_ROW_SLATE');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.19,.225,.24,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;me.materials.append(m);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));
for f in bm.faces:
 if f.normal.z<0:f.normal_flip()
bm.to_mesh(me);bm.free();out=R/'scenes/MUDAM_R169_SIRA_BUTUN_CATI_ADAY_v022.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R169_WHOLE_ROOF_v022.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,removed_fragments=removed,retained_raised_faces=retained,new_roof_faces=len(faces),limits=['Source fitted three slopes clipped to OSM footprint; eave offset not yet verified','Raised source features retained; joins require review','Slate color provisional']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-320,-45);s.camera.rotation_euler=(Vector((-67,-299,-66))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_row_roof_v022.png');bpy.ops.render.render(write_still=True);print('WHOLE_ROOF_BUILT',removed,len(faces),flush=True)
