from pathlib import Path
import bpy,json,math,numpy as np,bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R204_ARAZI_SUREKLILIGI_v001.blend'));r=json.loads((R/'config/r205_river_crossing_measured.json').read_text());xy=r['footprint'];c=r['plane'];ox,oy=r['origin']
def z(p):return c[0]*(p[0]-ox)+c[1]*(p[1]-oy)+c[2]
stone=bpy.data.materials['R154_FORT_STONE_PBR'];asphalt=bpy.data.materials.get('R191_COURT_ASPHALT') or bpy.data.materials['R175_BALLAST']
def mesh(name,vs,fs,material):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(material);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();uv=me.uv_layers.new()
 for l in me.loops:v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x+v.y)/4,v.z/4)
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
def extrude(name,ring,low,high,mat):
 n=len(ring);vs=[(p[0],p[1],z(p)+off) for off in [low,high] for p in ring];fs=[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
 for t in tessellate_polygon([[Vector((p[0],p[1],0)) for p in ring]]):fs.extend([tuple(reversed(t)),tuple(i+n for i in t)])
 mesh(name,vs,fs,mat)
extrude('R205_FORT_OLISY_ROAD_DECK',xy,-.45,0,asphalt)
# Long mapped sides carry masonry parapets, leaving approach edges open.
center=np.mean(xy,axis=0)
for i,(aa,bb) in enumerate(zip(xy,xy[1:]+xy[:1])):
 a,b=Vector(aa),Vector(bb)
 if (b-a).length<7:continue
 u=(b-a).normalized();n=Vector((-u.y,u.x))
 if n.dot(Vector(center)-(a+b)/2)<0:n=-n
 ring=[list(a),list(b),list(b+n*.22),list(a+n*.22)];extrude('R205_ROAD_PARAPET_%02d'%i,ring,0,.7,stone)
# Single independent masonry arch; crown follows measured deck. Hidden intrados is explicitly inferred.
a=np.array([-180.2,-373.5]);b=np.array([-190.3,-353.0]);u=(b-a)/np.linalg.norm(b-a);normal=np.array([u[1],-u[0]]);L=np.linalg.norm(b-a);radius=(L-3)/2;mid=L/2;spring=z(a+u*mid)-.9-radius
profile=[(0,z(a)-.4),(L,z(b)-.4),(L,-78),(mid+radius,-78),(mid+radius,spring)]
profile +=[(mid+radius*math.cos(t),spring+radius*math.sin(t)) for t in np.linspace(0,math.pi,33)[1:]]
profile +=[(mid-radius,-78),(0,-78)]
n=len(profile);vs=[]
for d in [-1.75,1.75]:
 for s,h in profile:
  p=a+u*s+normal*d;vs.append((p[0],p[1],h))
fs=[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
for t in tessellate_polygon([[Vector((s,h,0)) for s,h in profile]]):fs.extend([tuple(reversed(t)),tuple(i+n for i in t)])
mesh('R205_ROAD_MASONRY_ARCH',vs,fs,stone)
(R/'reports/R205_ROAD_CROSSING.json').write_text(json.dumps(dict(accepted=False,source=r,method='Independent mapped roadway slab and masonry crossing; no scan mesh',source_deck_support=r['support'],limits=['Concealed arch intrados and parapet section inferred, not measured','Approach grading and source visual comparison pending']),indent=2))
s=bpy.context.scene;t=Vector((-184,-368,-73));s.camera.location=t+Vector((-35,-50,35));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=50;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R205_ALT_YOL_KOPRUSU_v001.blend'),compress=True);s.render.filepath=str(R/'renders/qa/R205_road_bridge_v001.png');bpy.ops.render.render(write_still=True)
