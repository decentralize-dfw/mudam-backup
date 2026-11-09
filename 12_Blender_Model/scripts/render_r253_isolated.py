import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));ring=json.loads((R/'config/r252_oval_architecture.json').read_text())['outer']
def inside(x,y):
 if x<288 or x>350 or y<363 or y>434:return False
 hit=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 if hit:return True
 p=Vector((x,y))
 for aa,bb in zip(ring,ring[1:]+ring[:1]):
  a,b=Vector(aa),Vector(bb);d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared))
  if (p-a-d*t).length<1.5:return True
 return False
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bad=[]
 for v in bm.verts:
  p=o.matrix_world@v.co
  if not inside(p.x,p.y):bad.append(v)
 bmesh.ops.delete(bm,geom=bad,context='VERTS');bm.to_mesh(o.data);bm.free()
s=bpy.context.scene;t=Vector((320,398,18));s.camera.location=t+Vector((80,-100,0));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=80;s.render.resolution_x=1600;s.render.resolution_y=800;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R253_oval_isolated_front_source.png');bpy.ops.render.render(write_still=True)
