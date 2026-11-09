import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R308_ECCL_BUTUN_CAM_CEPHE_ADAY_v001.blend'))
a=Vector((178.3125,26.625));b=Vector((332.4375,282.375));u=(b-a).normalized();n=Vector((-u.y,u.x));L=(b-a).length
V={};F={};M={}
def p(s,d,z):
 q=a+u*s+n*d;return(q.x,q.y,z)
def box(name,s0,s1,d0,d1,z0,z1,mat):
 vs=[p(s,d,z) for z in (z0,z1) for s,d in ((s0,d0),(s1,d0),(s1,d1),(s0,d1))];k=len(V.setdefault(name,[]));V[name]+=vs;F.setdefault(name,[]).extend(tuple(k+i for i in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);M[name]=mat
ma=bpy.data.materials;glass=ma['R308_ECCL_GLASS'];frame=ma['R308_ECCL_FRAME'];floor=ma['R308_ECCL_FLOOR']
# End returns close the previously exposed floor edges; their bay subdivision
# is provisional, not a measurement or a claim about entrance locations.
for end,s in [('SOUTH',0),('NORTH',L)]:
 for i in range(5):
  d0=-12+i*2.1;d1=d0+2.1
  for z0,z1 in zip([7,9.5,12,14.5,17,19.5],[9.5,12,14.5,17,19.5,21.9]):box('R309_'+end+'_RETURN_GLASS',s-.045,s+.045,d0+.03,d1-.03,z0+.025,z1-.025,glass)
 for i in range(6):
  d=-12+i*2.1;box('R309_'+end+'_RETURN_FRAMES',s-.1,s+.1,d-.035,d+.035,6.76,21.93,frame)
 for z in [7,9.5,12,14.5,17,19.5,21.9]:box('R309_'+end+'_RETURN_TRANSOMS',s-.085,s+.085,-12,-1.5,z-.035,z+.035,frame)
# Continuous roof-to-glass junction and floor-to-glass edge, not open slots.
box('R309_ROOF_FRONT_JUNCTION',0,L,-1.6,-1.4,21.6,21.92,frame)
for z in [7,12,17]:box('R309_FLOOR_FRONT_JUNCTION',0,L,-1.61,-1.455,z-.24,z,floor)
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS'] or o.name.startswith(('R182_EXTENSION_','R210_GROUND_CONTINUITY_'))):continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);contacts=[];missing=[]
# Extend only supporting plinth below existing ground floor. Do not flatten
# terrain or fabricate a plaza, and do not fill through-storey openings.
for i in range(math.ceil(L)):
 s0=L*i/math.ceil(L);s1=L*(i+1)/math.ceil(L);zs=[]
 for s in [s0,(s0+s1)/2,s1]:
  q=p(s,-1.5,120);h,*_=bvh.ray_cast(Vector(q),Vector((0,0,-1)),300)
  if h:zs.append(h.z)
  else:missing.append(s)
 if len(zs)==3:
  low=min(zs)-.15
  if low<6.76:box('R309_FRONT_FOUNDATION',s0,s1,-1.8,-1.4,low,6.77,floor)
  contacts.append(dict(station=(s0+s1)/2,groundMin=min(zs),groundMax=max(zs)))
for name,vs in V.items():
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],F[name]);me.materials.append(M[name]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
scene=R/'scenes/MUDAM_R309_ECCL_UC_CEPHE_BIRLESIM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene))
s=bpy.context.scene;t=Vector((200,55,15));s.camera.location=t+Vector((-70,-90,45));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=105;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=16;s.render.filepath=str(R/'renders/qa/R309_end_return.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.type=='MESH' and o.name.startswith(('R308_','R309_')))
glb=R/'exports/r152_clean/r309_eccl_front_closed_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R309_ECCL_CLOSURE.json').write_text(json.dumps(dict(accepted=False,published=False,scene=str(scene),checks=checks,contacts=contacts,missing=missing,limitations=['End return bays provisional; entrances and Belvedere not source verified','Forest side and full building enclosure remain incomplete','Ground above floor7 requires actual graded plaza design; no flattening performed']),indent=2))
print('R309_READY')
