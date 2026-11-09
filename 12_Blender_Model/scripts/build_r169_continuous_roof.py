from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';import numpy as np
a=np.load(D/'164179154.npz');ang=float(a['angle']);cs,sn=math.cos(ang),math.sin(ang);zr,yr,xl,xr,af,ab,al,ar=json.loads((D/'hip_roof_fit_33.json').read_text())['parameters'];planes=[(0,-af,zr+af*yr),(0,ab,zr-ab*yr),(al,0,zr-al*xl),(-ar,0,zr+ar*xr)]
def h(x,y):return min(a*x+b*y+c for a,b,c in planes)
def local(p):return (cs*p.x+sn*p.y,-sn*p.x+cs*p.y)
def world(x,y,z):return (cs*x-sn*y,sn*x+cs*y,z)
# Preserve raised source features around chimneys / roof penetrations; no inferred deletion.
boxes=[(11.1,12.7,274.3,275.6),(14.7,16.3,274.0,275.6),(18.7,20.3,275.2,276.8),(19.9,22.7,276.4,278)]
xs=sorted(set([8.,23.]+[v for b in boxes for v in b[:2]]));ys=sorted(set([271.7,278.]+[v for b in boxes for v in b[2:]]))
def active(x,y):return 8<x<23 and 271.7<y<278 and not any(x0<x<x1 and y0<y<y1 for x0,x1,y0,y1 in boxes)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_CATI_BIRLESIM_ADAY_v014.blend'));o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data)
for axis,values in [(0,xs),(1,ys)]:
 for v in values:
  fs=[f for f in bm.faces if 25<f.calc_center_median().x<51 and -284<f.calc_center_median().y<-261 and f.calc_center_median().z>-64.2];es=set(e for f in fs for e in f.edges);vs=set(v for f in fs for v in f.verts);normal=Vector((cs,sn,0)) if axis==0 else Vector((-sn,cs,0));bmesh.ops.bisect_plane(bm,geom=list(fs)+list(es)+list(vs),dist=1e-6,plane_co=normal*v,plane_no=normal)
drop=[f for f in bm.faces if active(*local(f.calc_center_median())) and f.calc_center_median().z>-64.2];removed=len(drop);bmesh.ops.delete(bm,geom=drop,context='FACES');small=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=small,context='FACES');bm.to_mesh(o.data);bm.free()
verts=[];faces=[]
def clip(poly,a,b,c):
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp=a*p[0]+b*p[1]+c;dq=a*q[0]+b*q[1]+c
  if dp<=1e-9:out.append(p)
  if (dp<0)!=(dq<0):
   t=dp/(dp-dq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return out
for x0,x1 in zip(xs,xs[1:]):
 for y0,y1 in zip(ys,ys[1:]):
  if not active((x0+x1)/2,(y0+y1)/2):continue
  for i,P in enumerate(planes):
   poly=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
   for j,Q in enumerate(planes):
    if i!=j and poly:poly=clip(poly,*[p-q for p,q in zip(P,Q)])
   if len(poly)<3:continue
   area=abs(sum(p[0]*q[1]-p[1]*q[0] for p,q in zip(poly,poly[1:]+poly[:1])))/2
   if area<1e-8:continue
   n=len(verts);verts.extend(world(x,y,h(x,y)) for x,y in poly);faces.append(list(range(n,n+len(poly))))
me=bpy.data.meshes.new('R169_33_CONTINUOUS_HIP_ROOF');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);me.materials.append(bpy.data.materials['R169_33_CLEAN_UPPER_ROOF']);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.dissolve_limit(bm,angle_limit=.0001,verts=list(bm.verts),edges=list(bm.edges));bm.to_mesh(me);bm.free()
scene=R/'scenes/MUDAM_R169_UST_CATI_YENIDEN_ADAY_v015.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=1;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(23,-240,-40);s.camera.rotation_euler=(Vector((38,-273,-65))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=32;s.render.filepath=str(R/'renders/qa/R169_33_upper_roof_v015.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_UPPER_ROOF_v015.json').write_text(json.dumps(dict(scene=scene.name,accepted=False,published=False,reopened=True,removed_faces=removed,new_faces=len(me.polygons) if False else len(faces),protected_features=boxes,limits=['Central upper roof only; retained chimney/penetration envelopes and mansard are still rough','Fitted source roof planes are model estimates, not survey','Boundary seams require visual review']),indent=2));print('ROOF_REBUILT',removed)
