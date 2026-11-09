from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R319_SUR_ZEMIN_TEMAS_ADAY_v001.blend'))
plane=json.loads((R/'reports/R317_NORTH_WALL_RECONSTRUCTION.json').read_text())['groundPlane'];a,b,c=plane['coefficients']
pixels=[(705,217),(863,220),(863,263),(705,257)];poly=[Vector((-120+x*220/1400,95-y*220/1400)) for x,y in pixels]
# Preserve existing mesh/UV/edge topology. Analytic plane in the interior,
# smooth transition over the last1m to unchanged adjacent terrain.
def inside(p):
 signs=[(q-p0).cross(p-p0) for p0,q in zip(poly,poly[1:]+poly[:1])];return all(x>=0 for x in signs) or all(x<=0 for x in signs)
def distance(p):
 ds=[]
 for u,v in list(zip(poly,poly[1:]+poly[:1]))[1:]:
  d=v-u;t=max(0,min(1,(p-u).dot(d)/d.length_squared));ds.append((p-u-d*t).length)
 return min(ds)
o=bpy.data.objects['R152_CLASS2_TERRAIN'];changes=[]
for v in o.data.vertices:
 q=o.matrix_world@v.co;p=Vector((q.x,q.y))
 if not inside(p):continue
 w=min(1,distance(p)/1.0);w=w*w*(3-2*w);old=q.z;q.z+=(a*q.x+b*q.y+c-q.z)*w
 if abs(q.z-old)>1e-6:v.co=o.matrix_world.inverted()@q;changes.append(dict(index=v.index,before=old,after=q.z,weight=w))
assert changes;o.data.update();o['R320']='Independent fitted grass terrace plane,1m smooth edge transition. No scan mesh transfer.'
out=R/'scenes/MUDAM_R320_KUZEY_SUR_HENDEK_BIRLESIM_ADAY_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));bpy.ops.object.select_all(action='DESELECT');bpy.data.objects['R152_CLASS2_TERRAIN'].select_set(True)
glb=R/'exports/r152_clean/r320_north_terrain_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(0,46,5));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((0,61,-2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=45;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=650;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('R318_Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R320_north_moat_v002.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 checks.append(dict(name=ob.name,nonFinite=sum(not all(math.isfinite(v) for v in q.co) for q in ob.data.vertices),zeroArea=sum(f.area<1e-10 for f in ob.data.polygons)))
(R/'reports/R320_NORTH_MOAT_CONTACT.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changes=changes,pixelOutline=pixels,groundPlane=plane,glb=checks,topologyUnchanged=True,previousCandidateRejected='v001 had visible slab edge and clipped shading seams',limits=['Only north grass terrace; complete museum ring unaccepted','Boundary transition preserves neighboring levels','No geodetic accuracy claim']),indent=2));print('R320_READY',len(changes),checks)
