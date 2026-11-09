from pathlib import Path
import bpy,json,numpy as np,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R198_KALE_BATI_KALINTI_v002.blend'))
raw=json.loads((R/'.local_source_cache/r154/terrain.json').read_text());vs=[];fs=[]
for m in raw['meshes']:
 k=len(vs);vs.extend(m['vertices']);fs.extend([k+i for i in f] for f in m['faces'])
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def ground(x,y):
 h=g.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),300)[0]
 if h is None:raise RuntimeError('Missing terrain')
 return h.z
changes=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith('R198_RUIN_WALL'):continue
 low=min(v.co.z for v in o.data.vertices);new=min(low,min(ground(v.co.x,v.co.y) for v in o.data.vertices)-.4)
 for v in o.data.vertices:
  if abs(v.co.z-low)<.001:v.co.z=new
 changes.append(dict(name=o.name,old_bottom=low,new_bottom=new))
stone=bpy.data.materials.get('R154_FORT_STONE_PBR') or bpy.data.materials['R172_MOAT_EARTH']
def prism(name,xy,tops,bots,mat):
 n=len(xy);verts=[(x,y,z) for zs in (bots,tops) for (x,y),z in zip(xy,zs)];faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(mat);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();uv=me.uv_layers.new()
 for l in me.loops:
  v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x+v.y)/3,v.z/2)
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
floor=bpy.data.objects.get('R198_RUIN_FLOOR');xy=[tuple(v.co[:2]) for v in floor.data.vertices];z=floor.data.vertices[0].co.z;mat=floor.data.materials[0];bpy.data.objects.remove(floor,do_unlink=True);prism('R199_RUIN_CLOSED_FLOOR',xy,[z]*len(xy),[z-.2]*len(xy),mat)
d=json.loads((R/'reports/R199_FORT_LINK_MEASUREMENTS.json').read_text())[0];xy=d['xy'];a=np.array(d['samples']);# Source shows a connecting masonry wall, not a flat-deck bridge.
# Broad upper ridge estimate rejects lower flank/ground hits; retain source uncertainty.
upper=float(np.quantile(a[:,2],.88));bottom=min(-20.6,min(ground(x,y) for x,y in xy)-.2)
prism('R199_CENTRAL_CONNECTING_MASONRY',xy,[upper]*4,[bottom]*4,stone)
(R/'reports/R199_FORT_LINKS.json').write_text(json.dumps(dict(accepted=False,ruin_foundations=changes,crossing=dict(source=d,classification='Connecting masonry wall visible in source oblique; not claimed pedestrian bridge',upper_ridge=upper,bottom=bottom),limits=['Wall upper ridge flattened within scan uncertainty','Full fort terrain and source fidelity remain under review']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R199_KALE_BUTUN_BAGLANTILAR_v001.blend'),compress=True)
s=bpy.context.scene;t=Vector((-210,-175,-20));s.camera.location=t+Vector((90,-150,180));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=260;s.render.filepath=str(R/'renders/qa/R199_fort_whole_v001.png');bpy.ops.render.render(write_still=True)
