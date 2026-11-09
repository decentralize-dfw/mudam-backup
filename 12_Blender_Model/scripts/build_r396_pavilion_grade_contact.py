import bpy,json,math,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R392_KALE_BAGIMSIZ_TOPRAK_ORTU_ADAY_v001.blend'))
floors=[o for o in bpy.context.scene.objects if o.name.startswith('R363_PAVILION_EAST_')];boundaries=[]
for o in floors:
 # The top polygon is the second cap in the independent closed floor slab.
 face=o.data.polygons[1];vs=[o.matrix_world@o.data.vertices[i].co for i in face.vertices]
 for a,b in zip(vs,vs[1:]+vs[:1]):boundaries.append((a,b))
terrain=bpy.data.objects['R152_CLASS2_TERRAIN'];changes=[]
for v in terrain.data.vertices:
 p=terrain.matrix_world@v.co;best=None
 for a,b in boundaries:
  dx,dy=b.x-a.x,b.y-a.y;den=dx*dx+dy*dy
  if den<1e-12:continue
  t=max(0,min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/den));x,y=a.x+t*dx,a.y+t*dy;dist=math.hypot(p.x-x,p.y-y);z=a.z+t*(b.z-a.z)
  if best is None or dist<best[0]:best=(dist,z)
 if best and best[0]<1.5:
  t=1-best[0]/1.5;w=t*t*(3-2*t);z=p.z+(best[1]-p.z)*w
  if abs(z-p.z)>.0001:
   changes.append(dict(x=p.x,y=p.y,old=p.z,new=z,distance=best[0]));p.z=z;v.co=terrain.matrix_world.inverted()@p
terrain.data.update();terrain['R396_grade_contact']='Existing terrain boundary joined to measured R363 east pavilion floor; 1.5m continuous transition band, floor unchanged.'
out=R/'scenes/MUDAM_R396_PAVYON_ARAZI_KESINTISIZ_BAGLANTI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));eye=Vector((90,-105,55));direction=(Vector((28,-36,-3))-eye).normalized();rot=direction.to_track_quat('-Z','Y');right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));deps=bpy.context.evaluated_depsgraph_get();rays=[]
for px,py in [(590,441),(600,445),(620,452),(660,470),(680,480)]:
 origin=eye+right*((px/1000-.5)*75)+up*((.5-py/850)*63.75);hit,loc,n,idx,ob,mat=bpy.context.scene.ray_cast(deps,origin,direction,distance=1000);rays.append(dict(pixel=[px,py],hit=hit,name=ob.name if hit else None,xyz=list(loc) if hit else None))
report=dict(scene=out.name,accepted=False,published=False,changedVertices=len(changes),maxGradeChange=max(abs(v['new']-v['old']) for v in changes),changes=changes,formerGapRays=rays,limits=['Local east pavilion grass contact only. Wider perimeter and stone-wall fidelity remain unaccepted.']);(R/'reports/R396_GRADE_CONTACT.json').write_text(json.dumps(report,indent=2));print('R396_CONTACT',len(changes),rays)
s=bpy.context.scene;bpy.ops.object.camera_add(location=eye);s.camera=bpy.context.object;s.camera.rotation_euler=rot.to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=75;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R396_pavilion_contact_candidate.png');bpy.ops.render.render(write_still=True)
