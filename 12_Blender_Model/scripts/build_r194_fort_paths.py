from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R193_KALE_BATI_AVLU_v001.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not (o.name in ['R154_FAR_GROUND','R154_FAR_ROADS'] or o.name.startswith(('R187_OUTER_BASTIONS','R187_CONNECTED_MOAT','R193_SOUTHWEST_COURT'))):continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);m=bpy.data.materials.new('R194_FORT_MINERAL_PATH');m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.43,.39,.31,1);p.inputs['Roughness'].default_value=.95;report=[]
for row in json.loads((R/'config/r194_fort_paths.json').read_text()):
 vs=[];fs=[];miss=0
 for tri in row['triangles']:
  coords=[]
  for x,y in tri:
   h=g.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),300)[0]
   if h is None:miss+=1;break
   coords.append((x,y,h.z+.025))
  if len(coords)!=3:continue
  k=len(vs);vs.extend(coords);fs.append((k,k+1,k+2))
 assert not miss,(row['name'],miss)
 me=bpy.data.meshes.new('R194_'+row['name']);me.from_pydata(vs,[],fs);me.update();me.materials.append(m);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);report.append(dict(name=row['name'],triangles=len(fs),source=row['source'],width=row['width']))
(R/'reports/R194_FORT_PATHS_v001.json').write_text(json.dumps(dict(accepted=False,paths=report,limits=['Source image traced paths, widths approximate at image resolution','Fort southwest retaining boundaries, ruin and interior access still incomplete','No full fort acceptance']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R194_KALE_YURUYUSLER_v001.blend'),compress=True)
bpy.context.scene.render.filepath=str(R/'renders/qa/R194_fort_paths_v001.png');bpy.ops.render.render(write_still=True)
