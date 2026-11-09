from pathlib import Path
import bpy,json,bmesh,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_HENDEK_ADAY_v013.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and ('TERRAIN' in o.name or o.name in ['R154_FAR_GROUND','R154_FAR_ROADS'] or o.name.startswith(('R152_PATH_','R154_ROAD','R157_','R161_ROAD','R168_SOURCE_JUNCTION'))):
  o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);records=[]
for row in json.loads((R/'config/r171_hardscape_source.json').read_text()):
 if row['tags'].get('parking')=='underground':continue
 if bpy.data.objects.get('R171_HARDSCAPE_'+row['id']):continue
 ring=[Vector((x-293425,y-5499960,0)) for x,y in row['xy'][:-1]];faces=[]
 for tri in tessellate_polygon([ring]):faces.append([v if isinstance(v,int) else min(range(len(ring)),key=lambda j:(ring[j]-v).length_squared) for v in tri])
 m=bpy.data.meshes.new('R171_HARDSCAPE_'+row['id']);m.from_pydata(ring,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m)
 bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=10,use_grid_fill=True);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();missing=0
 for v in m.vertices:
  hit,*_=tree.ray_cast(Vector((v.co.x,v.co.y,160)),Vector((0,0,-1)),500)
  if hit:v.co.z=hit.z+.045
  else:missing+=1
 if missing:records.append(dict(id=row['id'],skippedGroundMisses=missing));bpy.data.meshes.remove(m);continue
 ob=bpy.data.objects.new(m.name,m);bpy.context.collection.objects.link(ob);mat=bpy.data.materials.new(m.name+'_MAT');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.35,.34,.31,1) if row['tags'].get('surface')=='paving_stones' else (.115,.12,.12,1);p.inputs['Roughness'].default_value=.95;m.materials.append(mat);ob['source']='OSM '+row['id'];ob['scope']='Mapped hardscape polygon; terrain drape, provisional material';records.append(dict(id=row['id'],vertices=len(m.vertices),footprintSource='OSM mapped parking/pedestrian area'))
# Normalize orientation and verify the new closed building masses after reopening.
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('R171_'):
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
out=R/'scenes/MUDAM_R173_SERT_ZEMINLER_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for o in bpy.context.scene.objects:
 o.select_set(o.type=='MESH' and o.name.startswith('R171_'))
 if o.type=='MESH' and o.name.startswith('R171_') and 'HARDSCAPE' not in o.name:
  bm=bmesh.new();bm.from_mesh(o.data);checks.append(dict(name=o.name,boundaryEdges=sum(e.is_boundary for e in bm.edges)));bm.free()
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r173_hardscape_REVIEW.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
(R/'reports/R173_HARDSCAPE_v001.json').write_text(json.dumps(dict(accepted=False,hardscape=records,buildings=checks,scope='Partial user regions2/3/11; full region and source visual validation still pending'),indent=2));print('HARDSCAPE',len(records),'BUILDINGS',len(checks),'BOUNDARIES',sum(v['boundaryEdges'] for v in checks))


