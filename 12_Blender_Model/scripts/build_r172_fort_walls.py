from pathlib import Path
import bpy,json,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'))
vs=[];faces=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
source=BVHTree.FromPolygons(vs,faces,all_triangles=True)
def sample(x,y):
 hit,n,idx,d=source.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),350);return (hit.z,abs(n.z)) if hit else None
features=json.loads((R/'config/r171_fort_source_features.json').read_text());segments=[];rejected=[]
for row in features:
 if row['tags'].get('barrier')!='city_wall':continue
 for index,(a,b) in enumerate(zip(row['xy'],row['xy'][1:])):
  a=np.array(a);b=np.array(b);length=np.linalg.norm(b-a)
  if length<.3:continue
  n=np.array([-(b-a)[1],(b-a)[0]])/length
  measures=[]
  for t in [.12,.3,.5,.7,.88]:
   p=a*(1-t)+b*t;section=[]
   for offset in [-3,-2,-1,-.5,0,.5,1,2,3]:
    q=p+n*offset;h=sample(*q)
    if h:section.append([offset,*h])
   crest=[v[1] for v in section if abs(v[0])<=1 and v[2]>.5];feet=[v[1] for v in section if abs(v[0])>=2]
   if crest and feet:measures.append([t,float(np.quantile(crest,.65)),min(feet)])
  if len(measures)<3:rejected.append([row['id'],index,'insufficient source support']);continue
  arr=np.array(measures);coef=np.polyfit(arr[:,0],arr[:,1],1);res=abs(np.polyval(coef,arr[:,0])-arr[:,1]);height=float(np.median(arr[:,1]-arr[:,2]))
  if np.quantile(res,.8)>.75 or height<.5 or height>12:rejected.append([row['id'],index,'source section ambiguous',height,float(np.quantile(res,.8))]);continue
  segments.append(dict(id=row['id'],segment=index,a=a.tolist(),b=b.tolist(),top=[float(np.polyval(coef,0)),float(np.polyval(coef,1))],bottom=float(np.min(arr[:,2]))-.15,sourceSection=measures,provisionalThickness=.8))
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R171_ALT_MAHALLE_SERT_ZEMIN_v002.blend'))
col=bpy.data.collections.new('R172_FORT_SOURCE_ALIGNED_WALLS');bpy.context.scene.collection.children.link(col)
mat=bpy.data.materials.get('R154_FORT_STONE_PBR')
if mat is None:
 mat=bpy.data.materials.new('R172_HISTORIC_STONE');mat.diffuse_color=(.37,.34,.27,1)
for r in segments:
 a=Vector(r['a']);b=Vector(r['b']);t=(b-a).normalized();n=Vector((-t.y,t.x))*.4;ring=[a-n,b-n,b+n,a+n];verts=[(p.x,p.y,r['bottom']) for p in ring]+[(p.x,p.y,r['top'][i%3!=0]) for i,p in enumerate(ring)]
 # Vertex top order is a,b,b,a.
 for j in range(4):verts[4+j]=(ring[j].x,ring[j].y,r['top'][0 if j in [0,3] else 1])
 fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 me=bpy.data.meshes.new('R172_WALL');me.from_pydata(verts,[],fs);me.update();o=bpy.data.objects.new('R172_FORT_'+r['id']+'_'+str(r['segment']),me);col.objects.link(o);me.materials.append(mat);uv=me.uv_layers.new()
 for face in me.polygons:
  for li in face.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((p.x*t.x+p.y*t.y)/4,p.z/3)
 o['source']='OSM wall alignment; five ACT cross-sections reduced to planar architectural segment';o['limitation']='Thickness0.8m provisional; not full fort acceptance'
scene=R/'scenes/MUDAM_R172_ON_KALE_SUR_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True)
(R/'reports/R172_FORT_WALLS_v001.json').write_text(json.dumps(dict(accepted=False,segments=segments,rejected=rejected,pending=['Cross-sections may contain vegetation; source visual review required','Terraces, stairs and paths not yet rebuilt','Existing terrain may obscure wall toes; terrain integration required','Thickness provisional']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;target=Vector((-210,-175,-35));s.camera.location=target+Vector((70,-150,180));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=280;s.render.filepath=str(R/'renders/qa/R172_fort_walls_v001.png');bpy.ops.render.render(write_still=True)
print('FORT_SEGMENTS',len(segments),'REJECTED',len(rejected))
