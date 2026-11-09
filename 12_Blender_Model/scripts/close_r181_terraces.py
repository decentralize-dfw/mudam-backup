from pathlib import Path
import bpy,json,math,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R181_KALE_TERASLARI_v001.blend'))
d=json.loads((R/'.local_source_cache/r154/terrain.json').read_text());vs=[];fs=[]
for row in d['meshes']:
 k=len(vs);vs.extend(row['vertices']);fs.extend([k+i for i in t] for t in row['faces'])
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True)
for o in list(bpy.data.objects):
 if o.name.startswith('R181_TERRACE_'):bpy.data.objects.remove(o,do_unlink=True)
report=[]
for row in json.loads((R/'config/r181_architectural_terraces.json').read_text()):
 xy=[]
 for aa,bb in zip(row['xy'],row['xy'][1:]+row['xy'][:1]):
  a,b=Vector(aa),Vector(bb);n=max(1,math.ceil((b-a).length))
  xy.extend(a.lerp(b,j/n) for j in range(n))
 c=row['plane'];origin=row['origin'];top=[];bottom=[]
 for p in xy:
  z=c[0]*(p.x-origin[0])+c[1]*(p.y-origin[1])+c[2];h,*_=ground.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),400)
  if h is None:raise RuntimeError('No foundation ground')
  top.append((p.x,p.y,z));bottom.append((p.x,p.y,h.z-.05))
 n=len(xy);tris=tessellate_polygon([[Vector((p.x,p.y,0)) for p in xy]]);faces=[tuple(t) for t in tris]+[tuple(n+i for i in reversed(t)) for t in tris]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new('R181_CLOSED_'+row['name']);me.from_pydata(top+bottom,[],faces);me.update();me.materials.append(bpy.data.materials['R172_MOAT_EARTH']);me.materials.append(bpy.data.materials.get('R154_FORT_STONE_PBR') or bpy.data.materials['R172_MOAT_EARTH'])
 for p in me.polygons:
  if p.index>=2*len(tris):p.material_index=1
 uv=me.uv_layers.new()
 for p in me.polygons:
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((v.x+v.y)/4,v.z/3) if p.material_index else (v.x/8,v.y/8)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);boundary=sum(e.is_boundary for e in bm.edges);bm.free()
 o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);report.append(dict(name=row['name'],boundary_edges=boundary,top_range=[min(p[2] for p in top),max(p[2] for p in top)],source_support=row['support']))
(R/'reports/R181_CLOSED_TERRACES_v002.json').write_text(json.dumps(dict(accepted=False,terraces=report,limits=['Closed foundation joins to previous DEM terrain; not surveyed wall thickness','Source residual clusters include ruins and earth slopes; full fort still needs remaining southern/northern connections']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R181_KALE_TERASLARI_v002.blend'),compress=True)
s=bpy.context.scene;s.render.filepath=str(R/'renders/qa/R181_fort_terraces_v002.png');bpy.ops.render.render(write_still=True);print('R181_CLOSED_DONE',report)
