import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R392_KALE_BAGIMSIZ_TOPRAK_ORTU_ADAY_v001.blend'))
# R396's full perimeter blend worsened classified agreement and is rejected.
# Join only the already cut terrain boundary to the floor, without moving
# either measured floor or surrounding ground elevations.
floor=bpy.data.objects['R363_PAVILION_EAST_0_RUIN_FLOOR'];face=floor.data.polygons[1];outline=[floor.matrix_world@floor.data.vertices[i].co for i in face.vertices];segments=[(a,b) for a,b in zip(outline,outline[1:]+outline[:1]) if max(a.y,b.y)>-32];terrain=bpy.data.objects['R152_CLASS2_TERRAIN'];bm=bmesh.new();bm.from_mesh(terrain.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bm.normal_update();vs=[];fs=[];pairs=[]
def match(p):
 for a,b in segments:
  dx,dy=b.x-a.x,b.y-a.y;den=dx*dx+dy*dy;t=((p.x-a.x)*dx+(p.y-a.y)*dy)/den
  if -.0001<=t<=1.0001 and math.hypot(p.x-a.x-t*dx,p.y-a.y-t*dy)<.0001:return a.z+t*(b.z-a.z)
 return None
for e in bm.edges:
 if not e.is_boundary:continue
 a,b=[terrain.matrix_world@v.co for v in e.verts];za,zb=match(a),match(b)
 if za is None or zb is None or max(abs(a.z-za),abs(b.z-zb))<.001:continue
 # Existing floor thickness covers the lower edge; this closed narrow wedge
 # closes the numerical cut above its cap while leaving source ground intact.
 tangent=Vector((b.x-a.x,b.y-a.y,0)).normalized();off=Vector((-tangent.y,tangent.x,0))*.015;start=len(vs);pts=[a,b,Vector((b.x,b.y,zb)),Vector((a.x,a.y,za))];vs.extend([tuple(p+o) for o in [off,-off] for p in pts]);fs.extend([[start+i for i in [0,1,2,3]],[start+i for i in [7,6,5,4]]]+[[start+i,start+(i+1)%4,start+(i+1)%4+4,start+i+4] for i in range(4)]);pairs.append(dict(a=list(a),b=list(b),floorA=za,floorB=zb))
bm.free();me=bpy.data.meshes.new('R397_PAVILION_GROUND_CUT_CONTACT');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(terrain.data.materials[0]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
for l in me.loops:
 v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x/4,v.z/4)
o['level_id']='SITE';o['source']='Geometric closure of existing cut boundary only. Both measured floor and existing terrain heights unchanged. This is not acceptance of adjacent source grade.'
out=R/'scenes/MUDAM_R397_PAVYON_KESIT_KENAR_BAGLANTI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));eye=Vector((90,-105,55));direction=(Vector((28,-36,-3))-eye).normalized();rot=direction.to_track_quat('-Z','Y');right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));deps=bpy.context.evaluated_depsgraph_get();rays=[]
for px,py in [(590,441),(600,445),(620,452),(660,470),(680,480)]:
 origin=eye+right*((px/1000-.5)*75)+up*((.5-py/850)*63.75);hit,loc,n,idx,ob,mat=bpy.context.scene.ray_cast(deps,origin,direction,distance=1000);rays.append(dict(pixel=[px,py],hit=hit,name=ob.name if hit else None))
report=dict(scene=out.name,accepted=False,published=False,seamSegments=len(pairs),pairs=pairs,formerGapRays=rays,rejected='R396 perimeter grade blend worsened classified ground RMS .268 to .363m and was not carried forward',limits=['Local gap closure, not acceptance of existing source grade or full ring.','Existing surrounding heights and R363 floors preserved.']);(R/'reports/R397_GRADE_CONTACT.json').write_text(json.dumps(report,indent=2));print('R397_CONTACT',len(pairs),rays)
import sys
if '--no-render' in sys.argv: sys.exit(0)
s=bpy.context.scene;bpy.ops.object.camera_add(location=eye);s.camera=bpy.context.object;s.camera.rotation_euler=rot.to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=75;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R397_pavilion_contact_candidate.png');bpy.ops.render.render(write_still=True)


