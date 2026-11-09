from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R197_ISTASYON_TEMIZ_KORIDOR_v001.blend'))
d=json.loads((R/'reports/R198_RUIN_MEASUREMENTS.json').read_text());xy=d['xy'];floor=float(np.median([p[2] for p in d['floor']]));tops=[float(np.median([max(v[1] for v in s) for s in e['samples']])) for e in d['edges']]
if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))<0:xy.reverse()
def split(poly,a,b):
 ins=[];out=[]
 def dt(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=dt(p),dt(q);(ins if dp>=0 else out).append(p)
  if dp*dq<0:
   t=dp/(dp-dq);v=[u+(w-u)*t for u,w in zip(p,q)];ins.append(v);out.append(v)
 return ins,out
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or not o.name.startswith('R193_SOUTHWEST_COURT'):continue
 old=o.data;old.calc_loop_triangles();uv=old.uv_layers.active;vs=[];fs=[];tex=[]
 for tri in old.loop_triangles:
  poly=[]
  for vi,li in zip(tri.vertices,tri.loops):v=old.vertices[vi].co;poly.append([*v,*(uv.data[li].uv if uv else (0,0))])
  parts=[];remain=poly
  for a,b in zip(xy,xy[1:]+xy[:1]):
   if len(remain)<3:break
   remain,out=split(remain,a,b)
   if len(out)>=3:parts.append(out)
  for p in parts:
   k=len(vs);vs.extend(v[:3] for v in p);tex.extend(v[3:] for v in p);fs.extend((k,k+j,k+j+1) for j in range(1,len(p)-1))
 me=bpy.data.meshes.new(o.name+'_RUIN_CUT');me.from_pydata(vs,[],fs);me.update()
 for m in old.materials:me.materials.append(m)
 u=me.uv_layers.new()
 for l in me.loops:u.data[l.index].uv=tex[l.vertex_index]
 o.data=me
stone=bpy.data.materials.get('R154_FORT_STONE_PBR') or bpy.data.materials['R172_MOAT_EARTH'];earth=bpy.data.materials['R172_MOAT_EARTH']
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(m);uv=me.uv_layers.new()
 for l in me.loops:v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x+v.y)/3,v.z/2)
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
mesh('R198_RUIN_FLOOR',[(x,y,floor) for x,y in xy],[(0,1,2),(0,2,3)],earth)
center=sum((Vector(p) for p in xy),Vector((0,0)))/4
for i,e in enumerate(d['edges']):
 a,b=Vector(e['a']),Vector(e['b']);n=Vector((-(b-a).y,(b-a).x)).normalized()
 if n.dot(center-(a+b)/2)<0:n=-n
 ring=[a,b,b+n*.65,a+n*.65];vs=[(p.x,p.y,z) for z in (floor-.25,tops[i]) for p in ring]
 fs=[(3,2,1,0),(4,5,6,7)]+[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)]
 mesh('R198_RUIN_WALL_'+str(i),vs,fs,stone)
(R/'reports/R198_RUIN_v001.json').write_text(json.dumps(dict(accepted=False,source=d,floor=floor,wall_tops=tops,limits=['Independent four-wall ruin from traced source outline','Wall thickness0.65m approximate from image; internal partition and broken wall profiles remain pending','Whole fort still not accepted']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R198_KALE_BATI_KALINTI_v001.blend'),compress=True)
s=bpy.context.scene;t=Vector((-229.6,-192.1,-18));s.camera.location=t+Vector((30,-45,38));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=42;s.render.filepath=str(R/'renders/qa/R198_fort_ruin_v001.png');bpy.ops.render.render(write_still=True)
