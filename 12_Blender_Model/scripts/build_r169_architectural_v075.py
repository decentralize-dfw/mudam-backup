from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169'
samples=np.array(json.loads((D/'row_whole_roof_samples_v061.json').read_text())['vertices']);xy=samples[:,:2];center=xy.mean(0)
fits=json.loads((D/'row_whole_roof_samples_v065.json').read_text())['plane_cleaning']['models']
def pix(p):return np.array([-80+(p[0]-700)/25,-301+(700-p[1])/25])
def inside(points,poly):
 result=np.zeros(len(points),bool)
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  cross=((a[1]>points[:,1])!=(b[1]>points[:,1])) & (points[:,0]<(b[0]-a[0])*(points[:,1]-a[1])/(b[1]-a[1]+1e-20)+a[0]);result^=cross
 return result
planes=[np.array(fits[i]['coeff']) for i in [0,1]];evidence=[]
for pixels in [[(260,660),(355,766),(326,888)],[(1064,490),(1128,721),(1035,630)]]:
 poly=np.array([pix(p) for p in pixels]);pts=samples[inside(xy,poly)];A=np.c_[pts[:,:2]-center,np.ones(len(pts))];rng=np.random.default_rng(175);best=None;score=0
 for _ in range(800):
  ids=rng.choice(len(A),3,replace=False)
  try:c=np.linalg.solve(A[ids],pts[ids,2])
  except:continue
  good=abs(A@c-pts[:,2])<.08
  if good.sum()>score:best=c;score=good.sum()
 for _ in range(3):
  good=abs(A@best-pts[:,2])<.10;best=np.linalg.lstsq(A[good],pts[good,2],rcond=None)[0]
 planes.append(best);evidence.append(dict(points=len(pts),support=int(good.sum()),coeff=best.tolist()))
q=np.array([pix(p) for p in [(255,642),(1065,468),(1140,733),(325,907)]])
def height(c,p):return float((p-center)@c[:2]+c[2])
def clip(poly,c):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  fa=height(c,a);fb=height(c,b)
  if fa<=1e-8:out.append(a)
  if (fa<0)!=(fb<0):out.append(a+(b-a)*fa/(fa-fb))
 return out
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,color,rough):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m
slate=mat('Authored slate - neutral unlit source color not copied',(.15,.18,.19),.78);plaster=mat('Mineral plaster provisional palette',(.62,.57,.44),.85)
def mesh(name,verts,faces,material):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(material);o['method']='Independent architectural polygons; source used for dimensions only';return o
areas=[]
for i,c in enumerate(planes):
 poly=list(q.copy())
 for j,other in enumerate(planes):
  if i!=j and poly:poly=clip(poly,c-other)
 if len(poly)>=3:
  verts=[(*p,height(c,p)) for p in poly];o=mesh('ARCH_MAIN_ROOF_'+str(i),verts,[list(reversed(range(len(verts))))],slate);mod=o.modifiers.new('Authored roof thickness 0.12m provisional','SOLIDIFY');mod.thickness=.12;areas.append(len(poly))
# Wall shell deliberately lacks openings at this massing stage; never publish as completed facade.
f=json.loads((D/'facade_planes_v062.json').read_text());walls=[]
for k in range(4):
 a=f['sides'][(k-1)%4];b=f['sides'][k];na=np.array(a['normal']);nb=np.array(b['normal']);walls.append(np.linalg.solve(np.array([na,nb]),[na@q[(k-1)%4]+a['offset'],nb@q[k]+b['offset']]))
for k in range(4):
 a=walls[k];b=walls[(k+1)%4];za=min(height(c,a) for c in planes);zb=min(height(c,b) for c in planes)
 mesh('ARCH_WALL_MASS_'+str(k),[(*a,-75),(*b,-75),(*b,zb),(*a,za)],[(0,1,2,3)],plaster)
s=bpy.context.scene;s['acceptance']='UNACCEPTED massing only. Openings, dormers, roof windows, chimneys and ground validation pending.'
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('World');s.world.color=(.25,.25,.25)
bpy.ops.object.light_add(type='SUN',location=(-60,-350,0));bpy.context.object.rotation_euler=(.4,-.5,-.5);bpy.context.object.data.energy=3
bpy.ops.object.camera_add();s.camera=bpy.context.object;target=Vector((-80,-301,-67));s.camera.location=target+Vector((22,-40,27));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=46
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_YENIDEN_KURULUM_v075.blend'))
s.render.filepath=str(R/'renders/qa/R169_architectural_massing_v075.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_ARCHITECTURAL_REBUILD_v075.json').write_text(json.dumps(dict(accepted=False,method='Independent four planar hip-roof polygons and measured facade planes. No scan mesh or scan texture imported.',hip_plane_evidence=evidence,roof_polygon_sizes=areas,pending=['Source-traced openings and frames','Roof extensions, rooflights, chimneys','Ground contact','Visual and export acceptance']),indent=2))
print('ARCHITECTURAL_MASSING_SAVED',areas,evidence)
