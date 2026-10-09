from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R45_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=json.loads((B/'reports/R04_build_report.json').read_text())['upper_level'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
cd=bpy.data.cameras.new('R45_DIAGNOSTIC');cam=bpy.data.objects.new(cd.name,cd);S.collection.objects.link(cam);T=json.loads((B/'reports/R04_build_report.json').read_text());st=T['steps'][2];cam.location=pt(*[sum(st[k][i] for k in ['outer0','outer1','inner0','inner1'])/4 for i in range(2)],st['z']+1.6);cam.rotation_euler=(Vector(r['cavity_samples'][13]['front'])-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=23;S.camera=cam;S.render.resolution_x=1500;S.render.resolution_y=1000;S.render.resolution_percentage=100;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();bvhs=[]
for ob in S.objects:
 if ob.type not in ['MESH','CURVE'] or ob.hide_render:continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh()
 if me and me.polygons:bvhs.append((ob.name,BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons],all_triangles=False)))
 ev.to_mesh_clear()
frame=cd.view_frame(scene=S);xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame);rows=[]
for px,py in [(355,264),(370,285),(385,286),(362,299),(330,280)]:
 direction=cam.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*px/1500,ymax-(ymax-ymin)*py/1000,-1)).normalized();hits=[]
 for name,bvh in bvhs:
  p,n,idx,d=bvh.ray_cast(cam.location,direction,100)
  if p is not None:hits.append(dict(name=name,position=list(p),distance=d))
 rows.append(dict(pixel=[px,py],hits=sorted(hits,key=lambda v:v['distance'])[:6]))
(B/'reports/R45_grip_pixel_diagnosis.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print(json.dumps(rows,indent=2))
