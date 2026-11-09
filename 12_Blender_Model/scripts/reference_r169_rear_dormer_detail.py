from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r169/source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in f.vertices] for f in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);cam=Vector((-80,-285,-48));rot=(Vector((-67,-299,-64))-cam).to_track_quat('-Z','Y');hits=[]
for x,y in [(310,650),(500,720)]:
 start=cam+rot@Vector(((x-600)/60,(500-y)/60,0));h,*_=tree.ray_cast(start,rot@Vector((0,0,-1)),100);assert h is not None;hits.append(list(h))
(R/'.local_source_cache/r169/rear_dormer_locations.json').write_text(json.dumps(hits,indent=2));print('DORMER_HITS',hits)
c=sum([Vector(p) for p in hits],Vector())/2;s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(c.x,c.y,0);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=8;s.render.filepath=str(R/'renders/qa/R169_rear_dormers_top_detail.png');bpy.ops.render.render(write_still=True)
