import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R321_BATI_HENDEK_ISTINAT_ADAY_v001.blend'))
outer=json.loads((R/'reports/R321_WEST_CREST_MEASUREMENTS.json').read_text());poly=[p['measuredCrest'][:2] for p in outer]
inner_pixels=[(849,859),(790,805),(796,652),(748,605),(670,548),(600,540),(495,522)]
poly += [[-120+x*220/1400,95-y*220/1400] for x,y in inner_pixels]
stations=json.loads((R/'reports/R322_WEST_TERRACE_SAMPLES.json').read_text())['source'];path=[Vector((*p['xy'],p['medianZ'])) for p in stations]
def inside(p):
 result=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p.y)!=(b[1]>p.y) and p.x<(b[0]-a[0])*(p.y-a[1])/(b[1]-a[1])+a[0]:result=not result
 return result
def elevation(p):
 best=(1e30,None)
 for a,b in zip(path,path[1:]):
  d=(b-a).to_2d();t=max(0,min(1,(p-a.to_2d()).dot(d)/d.length_squared));dist=(p-a.to_2d()-d*t).length
  if dist<best[0]:best=(dist,a.z+(b.z-a.z)*t)
 return best[1]
o=bpy.data.objects['R152_CLASS2_TERRAIN'];edits=[]
for v in o.data.vertices:
 q=o.matrix_world@v.co;p=q.to_2d()
 if not inside(p):continue
 z=elevation(p);old=q.z;q.z=z;v.co=o.matrix_world.inverted()@q;edits.append(dict(vertex=v.index,before=old,after=z))
assert edits;o.data.update();o['R322']='Independent piecewise terrace grade from9 visible ground stations, bounded by source-traced outer wall and museum footprint; no scan mesh transfer'
out=R/'scenes/MUDAM_R322_BATI_MUZE_TERAS_KOT_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));bpy.ops.object.select_all(action='DESELECT');bpy.data.objects['R152_CLASS2_TERRAIN'].select_set(True)
glb=R/'exports/r152_clean/r322_west_terrain_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-140,-140,75));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-45,-40,-2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=120;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('R322_Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R322_west_terrace.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':checks.append(dict(name=o.name,nonFinite=sum(not all(math.isfinite(x) for x in v.co) for v in o.data.vertices),zeroArea=sum(p.area<1e-10 for p in o.data.polygons)))
(R/'reports/R322_WEST_TERRACE.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,polygon=poly,stations=stations,edits=edits,glb=checks,limits=['Retaining station6 crest needs independent refinement','Boundary triangulation and materials need source comparison','Source controls do not prove entire ring exact']),indent=2));print('R322_READY',len(edits),checks)
