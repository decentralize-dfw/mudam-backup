from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/station_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();polys=[('NORTH_CANOPY',[(459,553),(1030,446),(1096,782),(501,731)]),('SOUTH_CANOPY',[(506,788),(1107,836),(1137,1015),(567,1128)]),('CENTRAL_GLAZING',[(501,731),(1096,782),(1107,836),(506,788)])];rows=[]
for name,pixels in polys:
 xy=np.array([[-345+x*110/1600,290-y*110/1600] for x,y in pixels]);samples=[]
 for u in np.linspace(.15,.85,8):
  for v in np.linspace(.15,.85,8):
   p=xy[0]*(1-u)*(1-v)+xy[1]*u*(1-v)+xy[2]*u*v+xy[3]*(1-u)*v;hit,h,n,*_=bpy.context.scene.ray_cast(dg,Vector((*p,100)),Vector((0,0,-1)),distance=250)
   if hit and n.z>.7:samples.append([*p,h.z])
 a=np.array(samples);origin=a[:,:2].mean(0);X=np.c_[a[:,:2]-origin,np.ones(len(a))];c=np.linalg.lstsq(X,a[:,2],rcond=None)[0];err=abs(X@c-a[:,2]);rows.append(dict(name=name,xy=xy.tolist(),plane=c.tolist(),origin=origin.tolist(),residualP90=float(np.quantile(err,.9)),samples=samples));print(name,c,np.quantile(err,[.5,.9,1]))
(R/'config/r178_roof_planes.json').write_text(json.dumps(rows,indent=2));s=bpy.context.scene;t=Vector((-290,235,-10));s.camera.location=t+Vector((-80,-90,70));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=100;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.filepath=str(R/'renders/qa/R178_station_source_side.png');bpy.ops.render.render(write_still=True)
