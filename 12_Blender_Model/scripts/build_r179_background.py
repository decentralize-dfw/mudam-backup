from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R178_STATION_v002.blend'))
rows=json.loads((R/'config/r179_background_domains.json').read_text());vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.name not in ['R154_FAR_GROUND','R154_FAR_ROADS']:continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True)
wall=bpy.data.materials.new('R179_BACKGROUND_MINERAL');wall.use_nodes=True;wall.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.42,.41,.36,1)
roof=bpy.data.materials.new('R179_BACKGROUND_ROOF');roof.use_nodes=True;roof.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.22,.24,.24,1)
records=[]
for row in rows:
 z=[]
 for x,y in row['outer']:
  hit,*_=ground.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),350)
  if hit:z.append(hit.z)
 if len(z)!=len(row['outer']):raise RuntimeError('Missing terrain '+row['id'])
 base=min(z)-.3;top=float(np.median(z))+row['height'];vs=[];fs=[];mi=[]
 for ring in [row['outer']]+row['holes']:
  for a,b in zip(ring,ring[1:]+ring[:1]):
   if np.linalg.norm(np.array(a)-b)<1e-5:continue
   k=len(vs);vs.extend([(a[0],a[1],base),(b[0],b[1],base),(b[0],b[1],top),(a[0],a[1],top)]);fs.append((k,k+1,k+2,k+3));mi.append(0)
 for tri in row['triangles']:
  for zz,rev in [(top,False),(base,True)]:
   k=len(vs);vs.extend((x,y,zz) for x,y in tri);fs.append(tuple(range(k,k+3))[::(-1 if rev else 1)]);mi.append(1)
 me=bpy.data.meshes.new('R179_BACKGROUND_'+row['id']);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);me.materials.append(wall);me.materials.append(roof)
 for p,i in zip(me.polygons,mi):p.material_index=i
 o['source']='OSM exact footprint and tagged height; simple background mass per user regions7-8';records.append(dict(id=row['id'],base=base,top=top,height_tag=row['height'],terrain_range=[min(z),max(z)]))
(R/'reports/R179_BACKGROUND_v001.json').write_text(json.dumps(dict(accepted=False,buildings=records,limits=['Simple mass representation explicitly allowed for outside-scan regions','Current OSM footprint dates may differ from ACT','No detailed facade claim','Western EIB exceeds current terrain extent and remains pending']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R179_UZAK_CEVRE_v001.blend'),compress=True)
s=bpy.context.scene;t=Vector((260,520,20));s.camera.location=t+Vector((400,-600,500));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=750;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R179_background_v001.png');bpy.ops.render.render(write_still=True)
print('R179_DONE',len(records))
