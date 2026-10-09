from pathlib import Path
import bpy,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'));from release_utils import verified_current_scene
r=verified_current_scene();bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));S=bpy.context.scene;S.render.resolution_x=1600;S.render.resolution_y=1100;S.render.resolution_percentage=100;cam=bpy.data.objects['P07_PHOTO_087_CONDITIONAL'];vs=[];fs=[];owners=[];names=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in S.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices);idx=len(names);names.append(ob.name)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(idx)
 eo.to_mesh_clear()

C=json.loads((B/'config/foundation.json').read_text())['calibration']
def point(p):
 x,y,z=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
tree=BVHTree.FromPolygons(vs,fs);rows=[];S.render.resolution_x=1400;S.render.resolution_y=1050
for view,eye,target,pixels in [('east_end',(130,230,23),(325,390,10),[(385,440),(395,580),(500,550),(480,400),(650,500)]),('east_junction',(430,150,34),(400,435,10),[(390,280),(1110,680),(1220,720),(1040,650)]),('west_junction',(780,180,34),(750,420,10),[(750,530),(750,425),(580,650),(990,280)])]:
 cam.location=point(eye);t=point(target);cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=45;bpy.context.view_layer.update();f=cam.data.view_frame(scene=S);xmin=min(p.x for p in f);xmax=max(p.x for p in f);ymin=min(p.y for p in f);ymax=max(p.y for p in f)
 for x,y in pixels:
  d=Vector((xmin+(xmax-xmin)*x/1400,ymax-(ymax-ymin)*y/1050,f[0].z));d=cam.matrix_world.to_quaternion()@d.normalized();hit=tree.ray_cast(cam.location,d,500);rows.append(dict(view=view,pixel=[x,y],name=None if hit[0] is None else names[owners[hit[2]]],point=None if hit[0] is None else list(hit[0])))
(B/'reports/R94_picks.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
