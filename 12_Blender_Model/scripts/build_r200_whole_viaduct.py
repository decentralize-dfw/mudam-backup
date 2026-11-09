from pathlib import Path
import bpy,bmesh,json,math,numpy as np
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R199_KALE_BUTUN_BAGLANTILAR_v001.blend'))
for o in list(bpy.data.objects):
 if o.name.startswith('R175_'):bpy.data.objects.remove(o,do_unlink=True)
d=json.loads((R/'config/r200_bridge_alignment.json').read_text());q=json.loads((R/'reports/R200_BRIDGE_GRADE.json').read_text());path=np.array(d['centerline']);L=d['bridge_length'];stations=np.linspace(0,L,len(path));grade=q['grade']
raw=json.loads((R/'.local_source_cache/r154/terrain.json').read_text());gv=[];gf=[]
for m in raw['meshes']:
 k=len(gv);gv.extend(m['vertices']);gf.extend([k+i for i in f] for f in m['faces'])
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('R182_EXTENSION_GROUND'):
  o.data.calc_loop_triangles();k=len(gv);gv.extend(o.matrix_world@v.co for v in o.data.vertices);gf.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
ground=BVHTree.FromPolygons(gv,gf,all_triangles=True)
def deck(s):return grade[0]*s+grade[1]
def point(s,d,z):
 s=max(0,min(L,s));i=min(len(path)-2,max(0,int(s/L*(len(path)-1))));t=(s-stations[i])/(stations[i+1]-stations[i]);p=path[i]*(1-t)+path[i+1]*t;u=path[i+1]-path[i];u/=np.linalg.norm(u);p+=np.array([u[1],-u[0]])*d;return (float(p[0]),float(p[1]),float(z))
def floor(s):
 zs=[]
 for off in [-5.2,0,5.2]:
  p=point(s,off,100);h=ground.ray_cast(Vector(p),Vector((0,0,-1)),300)[0]
  if h:zs.append(h.z)
 if not zs:raise RuntimeError('Missing bridge ground')
 return min(zs)-.3
stone=bpy.data.materials['R154_FORT_STONE_PBR'];ballast=bpy.data.materials['R175_BALLAST'];steel=bpy.data.materials['R175_RAIL_STEEL'];sleeper=bpy.data.materials['R175_SLEEPERS'];col=bpy.data.collections.new('R200_CONTINUOUS_VIADUCT');bpy.context.scene.collection.children.link(col)
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(mat);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();uv=me.uv_layers.new()
 for l in me.loops:
  v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x+v.y)/4,v.z/4)
 o=bpy.data.objects.new(name,me);col.objects.link(o);return o
def prism(name,profile,ds,mat):
 n=len(profile);vs=[point(s,dd,z) for dd in ds for s,z in profile];fs=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];poly=[Vector((s,z,0)) for s,z in profile]
 for t in tessellate_polygon([poly]):fs.extend([tuple(reversed(t)),tuple(i+n for i in t)])
 return mesh(name,vs,fs,mat)
centers=np.arange(0,L-2,17.65);radius=7.15;arches=[]
for i,c in enumerate(centers):
 lo=max(0,c-radius);hi=min(L,c+radius);ss=np.linspace(lo,hi,25);spring=deck(c)-1.7-radius;curve=[(float(s),float(spring+math.sqrt(max(0,radius**2-(s-c)**2)))) for s in ss];prism('R200_ARCH_%02d'%i,[(lo,deck(lo)-.18),(hi,deck(hi)-.18)]+list(reversed(curve)),[-5.2,5.2],stone);arches.append(dict(center=float(c),sourceWithinCoverage=bool(c<q['sourceCoverage'][1]),rhythmInferred=True))
spans=[];cursor=0
for c in centers:
 lo=max(0,c-radius);hi=min(L,c+radius)
 if lo>cursor:spans.append((cursor,lo))
 cursor=hi
if cursor<L:spans.append((cursor,L))
for i,(lo,hi) in enumerate(spans):
 z=min(floor(lo),floor(hi));prism('R200_PIER_%02d'%i,[(lo,z),(hi,z),(hi,deck(hi)-.18),(lo,deck(lo)-.18)],[-5.2,5.2],stone)
def ribbon(name,ds,heights,mat):
 vs=[];fs=[]
 for s in stations:
  vs.extend(point(s,dd,deck(s)+zz) for dd,zz in [(ds[0],heights[0]),(ds[1],heights[0]),(ds[1],heights[1]),(ds[0],heights[1])])
 for i in range(len(stations)-1):
  k=i*4
  for j in range(4):fs.append((k+j,k+(j+1)%4,k+(j+1)%4+4,k+j+4))
 fs.extend([(3,2,1,0),tuple(range(len(vs)-4,len(vs)))]);return mesh(name,vs,fs,mat)
ribbon('R200_CONTINUOUS_BALLAST',[-5,5],[-.2,.02],ballast)
for sign in [-1,1]:ribbon('R200_PARAPET_'+str(sign),[sign*5.0-.2,sign*5.0+.2],[0,.65],stone)
for ti,track in enumerate([-1.82,1.82]):
 for ri,delta in enumerate([-.7175,.7175]):ribbon('R200_RAIL_%s_%s'%(ti,ri),[track+delta-.035,track+delta+.035],[.15,.28],steel)
 # Batch sleepers into one mesh per track.
 vs=[];fs=[]
 for s in np.arange(.3,L-.3,.75):
  k=len(vs);vs.extend(point(st,dd,deck(st)+zz) for zz in [.02,.14] for st,dd in [(s-.11,track-1.2),(s+.11,track-1.2),(s+.11,track+1.2),(s-.11,track+1.2)])
  fs.extend(tuple(k+i for i in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 mesh('R200_SLEEPERS_'+str(ti),vs,fs,sleeper)
report=dict(accepted=False,bridgeLength=L,sourceGrade=q,arches=arches,method='Independent closed analytic arches, piers and continuous curved rails on mapped bridge alignment',limits=['Outside164.83m ACT coverage longitudinal grade extrapolated','Repeated arch centers beyond visible elevation inferred; no full bridge fidelity acceptance','End railway approaches beyond mapped bridge still to connect'])
(R/'reports/R200_CONTINUOUS_VIADUCT.json').write_text(json.dumps(report,indent=2))
s=bpy.context.scene;t=Vector((-165,-365,-55));s.camera.location=t+Vector((-180,-200,140));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=340;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R200_BUTUN_VIYADUK_v001.blend'),compress=True);s.render.filepath=str(R/'renders/qa/R200_continuous_viaduct_v001.png');bpy.ops.render.render(write_still=True)

