from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R194_KALE_YURUYUSLER_v001.blend'))
raw=json.loads((R/'.local_source_cache/r154/terrain.json').read_text());vs=[];fs=[]
for m in raw['meshes']:
 k=len(vs);vs.extend(m['vertices']);fs.extend([k+i for i in f] for f in m['faces'])
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True)
rows=json.loads((R/'config/r195_sw_boundary.json').read_text())
def height(row,x,y):
 for t in row['triangles']:
  a,b,c=t;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-10:continue
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
  v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
  if min(u,v,1-u-v)>=-1e-6:
   def z(p):return -11.52 if row['name']=='OUTER_BASTIONS' else -20.23+.8*max(0,min(1,(p[0]+190)/28))-.46*max(0,min(1,(-p[1]-180)/20))
   return u*z(a)+v*z(b)+(1-u-v)*z(c)
 return None
report=[]
for row in rows:
 verts=[];faces=[];shared=0
 for ring,zs in zip([row['xy']]+row['holes'],row['boundary_heights']):
  for i,(aa,bb) in enumerate(zip(ring,ring[1:]+ring[:1])):
   a,b=Vector(aa),Vector(bb);n=max(1,math.ceil((b-a).length/.75))
   for j in range(n):
    p=a.lerp(b,j/n);q=a.lerp(b,(j+1)/n);mid=(p+q)/2
    other=next((r for r in rows if r is not row and height(r,mid.x,mid.y) is not None),None)
    top=[zs[i]+(zs[(i+1)%len(zs)]-zs[i])*t for t in (j/n,(j+1)/n)]
    if other:
     bottom=[height(other,v.x,v.y) for v in (p,q)]
     if any(v is None for v in bottom):other=None
     elif sum(top)<=sum(bottom)+.001:continue
     else:shared+=1
    if not other:
     bottom=[]
     for v in (p,q):
      hit=ground.ray_cast(Vector((v.x,v.y,100)),Vector((0,0,-1)),400)[0]
      if hit is None:raise RuntimeError('Missing terrain at fort boundary')
      bottom.append(hit.z)
    k=len(verts);verts.extend([(p.x,p.y,top[0]),(q.x,q.y,top[1]),(q.x,q.y,bottom[1]),(p.x,p.y,bottom[0])]);faces.extend([(k,k+1,k+2),(k,k+2,k+3)])
 me=bpy.data.meshes.new('R195_BOUNDARY_'+row['name']);me.from_pydata(verts,[],faces);me.update()
 me.materials.append(bpy.data.materials.get('R154_FORT_STONE_PBR') or bpy.data.materials['R172_MOAT_EARTH'])
 uv=me.uv_layers.new()
 for l in me.loops:
  v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x+v.y)/4,v.z/3)
 ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
 report.append(dict(name=ob.name,triangles=len(faces),shared_boundary_segments=shared))
(R/'reports/R195_BOUNDARY_v002.json').write_text(json.dumps(dict(accepted=False,boundaries=report,limits=['Architectural grade interpolation between measured source levels','Boundary faces join original DEM; masonry face alignment and material require source comparison','No full fort acceptance']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R195_KALE_BATI_BAGLANTI_v001.blend'),compress=True)
bpy.context.scene.render.filepath=str(R/'renders/qa/R195_fort_west_join_v001.png');bpy.ops.render.render(write_still=True)


