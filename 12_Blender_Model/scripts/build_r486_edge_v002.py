import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R485_AVLU_SUR_ZEMIN_ADAY_v002.blend'))
def bvh(name):
 o=bpy.data.objects[name];o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[t.vertices for t in o.data.loop_triangles],all_triangles=True)
lawn=bvh('R485_NW_LAWN');court=bvh('R457_NORTH_LOADING_COURT');oldground=bvh('R152_FORECOURT_0')
D=json.loads((R/'reports/R485_COURT_PATH_DOMAINS.json').read_text());poly=D['lawn']['outline'];verts=[];faces=[];contacts=[]
# Close the real level-change at the court/lawn cut. Use existing court surface and grass surface exactly.
# A narrow independently authored backing wall, not source mesh, follows the architectural excavation edge.
for a,b in zip(poly,poly[1:]+poly[:1]):
 if not (min(a[0],b[0])>-52 and max(a[1],b[1])>31):continue
 av=Vector(a);bv=Vector(b);t=(bv-av).normalized();mid=(av+bv)/2
 normal=Vector((-t.y,t.x));lh=lawn.ray_cast(Vector((mid.x+normal.x*.02,mid.y+normal.y*.02,10)),Vector((0,0,-1)),30)[0]
 if lh is None:normal=-normal
 count=max(1,math.ceil((bv-av).length/.25));rings=[]
 for j in range(count+1):
  p=av.lerp(bv,j/count);inner=p+normal*.025;outer=p-normal*.035
  lower=lawn.ray_cast(Vector((inner.x,inner.y,10)),Vector((0,0,-1)),30)[0]
  upper=court.ray_cast(Vector((outer.x,outer.y,10)),Vector((0,0,-1)),30)[0]
  if upper is None:upper=oldground.ray_cast(Vector((outer.x,outer.y,10)),Vector((0,0,-1)),30)[0]
  if lower is None or upper is None:rings.append(None);continue
  zlo=lower.z-.12;zhi=max(upper.z,lower.z);k=len(verts);verts.extend([(inner.x,inner.y,zlo),(outer.x,outer.y,zlo),(outer.x,outer.y,zhi),(inner.x,inner.y,zhi)]);rings.append(k);contacts.append(abs(zhi-upper.z))
 for k,l in zip(rings,rings[1:]):
  if k is None or l is None:continue
  faces.extend([(k+i,k+(i+1)%4,l+(i+1)%4,l+i) for i in range(4)])
 for j,k in enumerate(rings):
  if k is None:continue
  if j==0 or rings[j-1] is None:faces.append((k+3,k+2,k+1,k))
  if j==len(rings)-1 or rings[j+1] is None:faces.append((k,k+1,k+2,k+3))
me=bpy.data.meshes.new('R486_NW_COURT_RETAINING_EDGE');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);o['level_id']='SITE';o['source']='Architectural retaining backing at source-visible courtyard level change; shared boundary with authored lawn and court. Thickness 0.06m is modeling envelope, not measured.';me.materials.append(bpy.data.objects['R457_NORTH_LOADING_COURT'].data.materials[0]);uv=me.uv_layers.new(name='UVMap')
for l in me.loops:
 v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x*.25,v.z*.25)
assert check['nonManifold']==0,check
out=R/'scenes/MUDAM_R486_AVLU_DUSEY_BAGLANTI_ADAY_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R486_EDGE_BUILD.json').write_text(json.dumps(dict(check=check,contacts=len(contacts),maxTopDifference=max(contacts),accepted=False,published=False),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-80,0,35));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-48,37,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=43;s.render.filepath=str(R/'renders/qa/R486_v002_northwest_oblique.png');bpy.ops.render.render(write_still=True)
