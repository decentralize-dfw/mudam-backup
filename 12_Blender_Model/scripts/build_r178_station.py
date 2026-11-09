from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R177_TASAN_YOL_YENIDEN_v002.blend'))
rows=json.loads((R/'config/r178_roof_planes.json').read_text())
col=bpy.data.collections.new('R178_INDEPENDENT_STATION');bpy.context.scene.collection.children.link(col)
def mat(name,color,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
roof=mat('R178_LIGHT_CANOPY',(.63,.75,.72),.4);metal=mat('R178_FRAME',(.25,.31,.31),.3,.6);glass=mat('R178_DARK_GLAZING',(.045,.11,.13),.18,.35);stone=mat('R178_PLATFORM',(.36,.36,.34),.9)
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(m);return o
def beam(name,a,b,w,m):
 a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.01:u=Vector((1,0,0))
 u.normalize();v=axis.cross(u).normalized();vs=[p+u*i*w/2+v*j*w/2 for p in [a,b] for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
def ground(p):return -6.0+(p[0]+270)*.12
for row in rows:
 xy=[Vector(p) for p in row['xy']];a,b,c=row['plane'];ox,oy=row['origin']
 def pt(u,v):
  p=xy[0]*(1-u)*(1-v)+xy[1]*u*(1-v)+xy[2]*u*v+xy[3]*(1-u)*v
  return Vector((p.x,p.y,a*(p.x-ox)+b*(p.y-oy)+c))
 corners=[pt(0,0),pt(1,0),pt(1,1),pt(0,1)]
 vs=corners+[p-Vector((0,0,.18)) for p in corners]
 mesh('R178_'+row['name'],vs,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],glass if row['name']=='CENTRAL_GLAZING' else roof)
 nu=22 if row['name']=='CENTRAL_GLAZING' else 32;nv=1 if row['name']=='CENTRAL_GLAZING' else 15
 for i in range(nu+1):beam('R178_ROOF_SEAM',pt(i/nu,0)+Vector((0,0,.012)),pt(i/nu,1)+Vector((0,0,.012)),.045,metal)
 if nv>1:
  for j in range(1,nv):beam('R178_ROOF_SEAM',pt(0,j/nv)+Vector((0,0,.012)),pt(1,j/nv)+Vector((0,0,.012)),.025,metal)
 if row['name']=='CENTRAL_GLAZING':continue
 # Three enclosed glazed sides; the west edge is the real funicular opening.
 for k in [0,1,2]:
  p=corners[k];q=corners[(k+1)%4];n=max(1,round((q-p).length/1.7))
  for j in range(n):
   l=p.lerp(q,j/n);r=p.lerp(q,(j+1)/n);lz=ground(l);rz=ground(r)
   mesh('R178_FACADE_GLASS',[(l.x,l.y,lz),(r.x,r.y,rz),(r.x,r.y,r.z-.22),(l.x,l.y,l.z-.22)],[(0,1,2,3)],glass)
   beam('R178_FACADE_POST',(l.x,l.y,lz),(l.x,l.y,l.z-.18),.14,metal)
   beam('R178_FACADE_TRANSOM',(l.x,l.y,-2.5),(r.x,r.y,-2.5),.1,metal)
  beam('R178_FASCIA',p,q,.22,metal)
 p=corners[3];q=corners[0]
 for t in [0,.5,1]:
  h=p.lerp(q,t);beam('R178_RAIL_BAY_PIER',(h.x,h.y,ground(h)),(h.x,h.y,h.z-.18),.45,metal)
 # Structural floor follows the station longitudinal slope; geometry is provisional between measured endpoints.
 floor=[(p.x,p.y,ground(p)) for p in corners];mesh('R178_PLATFORM_SLAB',floor,[(0,1,2,3)],stone)
 for v in [.25,.75]:
  p=pt(0,v);q=pt(1,v);direction=(q-p).normalized();p=p-direction*14
  lateral=Vector((-direction.y,direction.x,0)).normalized()
  for side in [-.7175,.7175]:
   l=p+lateral*side;r=q+lateral*side;beam('R178_TRACK_RAIL',(l.x,l.y,ground(l)+.12),(r.x,r.y,ground(r)+.12),.08,metal)
report={'accepted':False,'source':'ACT traced independent roof domains; no source mesh or facade textures','roof_plane_residuals':[{'name':r['name'],'p90':r['residualP90']} for r in rows],'limits':['Facade base interpolated from exterior ground reference endpoints; requires section comparison','Facade module spacing is provisional; exact opening count not yet accepted','Forecourt and terrain cut still required; station not accepted as complete']}
(R/'reports/R178_STATION_v001.json').write_text(json.dumps(report,indent=2))
s=bpy.context.scene;t=Vector((-290,235,-10));s.camera.location=t+Vector((-80,-90,70));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=100;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R178_STATION_v001.blend'),compress=True)
s.render.filepath=str(R/'renders/qa/R178_authored_station_v001.png');bpy.ops.render.render(write_still=True)
print('R178_DONE')
