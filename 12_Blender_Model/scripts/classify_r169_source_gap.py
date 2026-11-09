from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);p=Vector((-82.1481476,-294.4232483,-63.783638));nearest=tree.find_nearest(p);rings=[]
for radius in [.01,.025,.05,.1,.2,.4]:
 heights=[]
 for i in range(24):
  a=i*math.tau/24;h,*_=tree.ray_cast(Vector((p.x+radius*math.cos(a),p.y+radius*math.sin(a),40)),Vector((0,0,-1)),200);heights.append(h.z if h else None)
 rings.append(dict(radius=radius,heights=heights))
r=dict(model_point=list(p),nearest_source=list(nearest[0]),nearest_distance=nearest[3],rings=rings);(R/'reports/R169_SOURCE_GAP_CLASSIFICATION.json').write_text(json.dumps(r,indent=2));print(r)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.world=bpy.data.worlds.new('Black');bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=2;s.camera.location=(p.x,p.y,0);s.camera.rotation_euler=(p-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/qa/R169_source_gap_close.png');bpy.ops.render.render(write_still=True)
