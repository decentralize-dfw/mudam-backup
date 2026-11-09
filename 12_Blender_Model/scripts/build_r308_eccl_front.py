import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R305_VIYADUK_KUZEY_RAY_YAKLASIMI_ADAY_v001.blend'));a=Vector((178.3125,26.625));b=Vector((332.4375,282.375));u=(b-a).normalized();normal=Vector((-u.y,u.x));L=(b-a).length
# Architectural curtain-wall assembly. ACT roof-edge trace controls placement;
# facade system is evidenced by the architect, dimensions not measurable in the scan remain explicit assumptions.
V={};F={};M={}
def material(n,c,rough,metal=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
glass=material('R308_ECCL_GLASS',(.11,.24,.21),.18,.3);metal=material('R308_ECCL_FRAME',(.38,.43,.43),.3,.7);wing=material('R308_ECCL_WING',(.42,.43,.41),.38,.65);floor=material('R308_ECCL_FLOOR',(.28,.29,.27),.8)
def point(s,d,z):p=a+u*s+normal*d;return (p.x,p.y,z)
def prism(name,s0,s1,profile,mat):
 n=len(profile);vs=[point(s,d,z) for s in [s0,s1] for d,z in profile];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];k=len(V.setdefault(name,[]));V[name]+=vs;F.setdefault(name,[]).extend(tuple(k+i for i in f) for f in fs);M[name]=mat
setback=-1.5;bayCount=math.ceil(L/2.5);width=L/bayCount;levels=[7,9.5,12,14.5,17,19.5,21.6]
for i in range(bayCount):
 s0=i*width;s1=(i+1)*width
 for j,(z0,z1) in enumerate(zip(levels,levels[1:])):
  prism('R308_FRONT_GLASS',s0+.03,s1-.03,[(setback-.045,z0+.025),(setback+.045,z0+.025),(setback+.045,z1-.025),(setback-.045,z1-.025)],glass)
for i in range(bayCount+1):
 s=i*width;prism('R308_VERTICAL_FRAMES',max(0,s-.035),min(L,s+.035),[(setback-.1,7),(setback+.1,7),(setback+.1,21.65),(setback-.1,21.65)],metal)
for z in levels:prism('R308_HORIZONTAL_FRAMES',0,L,[(setback-.085,z-.035),(setback+.085,z-.035),(setback+.085,z+.035),(setback-.085,z+.035)],metal)
prism('R308_WING_CANOPY',0,L,[(0,22.45),(-12,22.45),(-12,21.9),(-1.5,21.6),(0,22.28)],wing)
for z in [7,12,17]:prism('R308_FRONT_FLOOR_'+str(z),0,L,[(-12,z-.24),(-1.6,z-.24),(-1.6,z),(-12,z)],floor)
# Replace the entire inherited 300m frontage strip, retaining UVs outside it.
quad=[a+normal*3,b+normal*3,b-normal*12,a-normal*12];xy=[list(p) for p in quad]
if sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(xy,xy[1:]+xy[:1]))<0:xy.reverse()
def split(poly,p,q):
 def d(v):return (q[0]-p[0])*(v[1]-p[1])-(q[1]-p[1])*(v[0]-p[0])
 ins=[];outs=[]
 for v,w in zip(poly,poly[1:]+poly[:1]):
  dv,dw=d(v),d(w);(ins if dv>=0 else outs).append(v)
  if dv*dw<0:
   t=dv/(dv-dw);r=[x+(y-x)*t for x,y in zip(v,w)];ins.append(r);outs.append(r)
 return ins,outs
removed=[]
for o in list(bpy.context.scene.objects):
 if not o.name.startswith('R166_MEASURED_ENVELOPE') or o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();uv=me.uv_layers.active;vs=[];fs=[];us=[];ms=[];cut=0;W=o.matrix_world;inv=W.inverted()
 for tri in me.loop_triangles:
  poly=[]
  for vi,li in zip(tri.vertices,tri.loops):v=W@me.vertices[vi].co;poly.append([*v,*(uv.data[li].uv if uv else (0,0))])
  if min(v[2] for v in poly)>24:pieces=[poly]
  else:
   remain=poly;pieces=[]
   for p,q in zip(xy,xy[1:]+xy[:1]):
    if len(remain)<3:break
    remain,out=split(remain,p,q)
    if len(out)>=3:pieces.append(out)
   if len(remain)>=3:cut+=1
  for poly in pieces:
   k=len(vs);vs.extend(inv@Vector(v[:3]) for v in poly);us.extend(v[3:] for v in poly)
   for j in range(1,len(poly)-1):fs.append((k,k+j,k+j+1));ms.append(tri.material_index)
 new=bpy.data.meshes.new(me.name+'_R308');new.from_pydata(vs,[],fs);new.update()
 for m in me.materials:new.materials.append(m)
 uv=new.uv_layers.new()
 for p,mi in zip(new.polygons,ms):
  p.material_index=mi
  for li in p.loop_indices:uv.data[li].uv=us[new.loops[li].vertex_index]
 bm=bmesh.new();bm.from_mesh(new);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-10],context='FACES');bm.to_mesh(new);bm.free();o.data=new;removed.append(dict(name=o.name,intersectedFaces=cut))
for name,vs in V.items():
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],F[name]);me.materials.append(M[name]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
path=R/'scenes/MUDAM_R308_ECCL_BUTUN_CAM_CEPHE_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;t=Vector((225,104,15));s.camera.location=t+Vector((-90,-65,45));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=180;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R308_frontage_candidate.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R308_'))
glb=R/'exports/r152_clean/r308_eccl_front_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R308_ECCL_FRONTAGE.json').write_text(json.dumps(dict(accepted=False,published=False,length=L,bays=bayCount,glassPanels=bayCount*6,removedInherited=removed,checks=checks,sourceUrl='https://swaa.lu/projekt/european-convention-center-luxemburg/',evidence='Architect describes a glazed hall under projecting metallic wing,300m glazed plaza facade; official photos show vertical glass and horizontal bands. Scan dark underside must not be treated as inclined glazed wall.',assumptions=['1.5m glass setback,2.5m approximate bays,7/12/17floorlevels and canopy underside section provisional','Forest side, end returns, innerBelvedere and ground connections still need completion','R306/R307 general facade fits rejected due canopy/occlusion contamination']),indent=2));print('R308_READY')
