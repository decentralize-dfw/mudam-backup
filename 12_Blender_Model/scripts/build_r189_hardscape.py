from pathlib import Path
import bpy,json,bmesh,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R188_UZAK_CEVRE_v001.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and ('TERRAIN' in o.name or o.name in ['R154_FAR_GROUND','R154_FAR_ROADS'] or o.name.startswith(('R152_PATH_','R154_ROAD','R157_','R161_ROAD','R168_SOURCE_JUNCTION'))):
  o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);records=[]
for row in json.loads((R/'config/r184_north_hardscape_sources.json').read_text()):
 if row['tags'].get('parking')=='underground':continue
 if bpy.data.objects.get('R189_HARDSCAPE_'+row['id']):continue
 ring=[Vector((x,y,0)) for x,y in row['xy'][:-1]];faces=[]
 for tri in tessellate_polygon([ring]):faces.append([v if isinstance(v,int) else min(range(len(ring)),key=lambda j:(ring[j]-v).length_squared) for v in tri])
 m=bpy.data.meshes.new('R189_HARDSCAPE_'+row['id']);m.from_pydata(ring,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m)
 bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=10,use_grid_fill=True);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();missing=0
 for v in m.vertices:
  hit,*_=tree.ray_cast(Vector((v.co.x,v.co.y,160)),Vector((0,0,-1)),500)
  if hit:v.co.z=hit.z+.045
  else:missing+=1
 if missing:records.append(dict(id=row['id'],skippedGroundMisses=missing));bpy.data.meshes.remove(m);continue
 ob=bpy.data.objects.new(m.name,m);bpy.context.collection.objects.link(ob);mat=bpy.data.materials.new(m.name+'_MAT');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.35,.34,.31,1) if row['tags'].get('surface')=='paving_stones' else (.115,.12,.12,1);p.inputs['Roughness'].default_value=.95;m.materials.append(mat);ob['source']='OSM '+row['id'];ob['scope']='Mapped hardscape polygon; terrain drape, provisional material';records.append(dict(id=row['id'],vertices=len(m.vertices),footprintSource='OSM mapped parking/pedestrian area'))
out=R/'scenes/MUDAM_R189_KUZEY_SERT_ZEMIN_v001.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'reports/R189_HARDSCAPE_v001.json').write_text(json.dumps(dict(accepted=False,hardscape=records,limits=['Three mapped surface areas only; building apron coverage incomplete','Terrain drape needs source level comparison']),indent=2))
s=bpy.context.scene;t=Vector((370,390,15));s.camera.location=t+Vector((150,-230,210));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=250;s.render.filepath=str(R/'renders/qa/R189_hardscape_v001.png');bpy.ops.render.render(write_still=True)
