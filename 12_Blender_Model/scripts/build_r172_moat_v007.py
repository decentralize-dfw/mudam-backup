from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_SUR_ADAY_v001.blend'))
row=next(r for r in json.loads((R/'reports/R172_TERRACES_v003.json').read_text())['terraces'] if r['name']=='MOAT_EAST')
xy=row['xy'];area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))
if area<0:xy.reverse()
edges=list(zip(xy,xy[1:]+xy[:1]));bounds=[min(p[0] for p in xy),max(p[0] for p in xy),min(p[1] for p in xy),max(p[1] for p in xy)]
def split(poly,a,b):
 def d(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 inside=[];outside=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=d(p),d(q)
  (inside if dp>=0 else outside).append(p)
  if (dp>0 and dq<0) or (dp<0 and dq>0):
   t=dp/(dp-dq);v=[u+(w-u)*t for u,w in zip(p,q)];inside.append(v);outside.append(v)
 return inside,outside
changes=[]
for obj in list(bpy.context.scene.objects):
 if obj.type!='MESH' or not (obj.name in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN'] or obj.name.startswith('R152_PATH_')):continue
 mesh=obj.data;mesh.calc_loop_triangles();uv=mesh.uv_layers.active;verts=[];faces=[];uvs=[];mats=[];cut=0;mw=obj.matrix_world;inv=mw.inverted()
 for tri in mesh.loop_triangles:
  poly=[]
  for vi,li in zip(tri.vertices,tri.loops):
   p=mw@mesh.vertices[vi].co;tex=uv.data[li].uv if uv else (0,0);poly.append([*p,*tex])
  if max(p[0] for p in poly)<bounds[0] or min(p[0] for p in poly)>bounds[1] or max(p[1] for p in poly)<bounds[2] or min(p[1] for p in poly)>bounds[3]:pieces=[poly]
  else:
   remaining=poly;pieces=[]
   for a,b in edges:
    if len(remaining)<3:break
    remaining,out=split(remaining,a,b)
    if len(out)>=3:pieces.append(out)
   if len(remaining)>=3:cut+=1
  for piece in pieces:
   base=len(verts);verts.extend(inv@Vector(p[:3]) for p in piece);uvs.extend(p[3:5] for p in piece)
   for j in range(1,len(piece)-1):faces.append((base,base+j,base+j+1));mats.append(tri.material_index)
 if not cut:continue
 new=bpy.data.meshes.new(mesh.name+'_PLANAR_CUT');new.from_pydata(verts,[],faces);new.update()
 for m in mesh.materials:new.materials.append(m)
 layer=new.uv_layers.new(name=uv.name if uv else 'UVMap')
 for p,mi in zip(new.polygons,mats):
  p.material_index=mi;p.use_smooth=True
  for li in p.loop_indices:layer.data[li].uv=uvs[new.loops[li].vertex_index]
 obj.data=new;changes.append({'object':obj.name,'intersected_triangles':cut,'faces':len(faces)})
plane=row['plane'];origin=row['origin']
vs=[Vector((x,y,plane[0]*(x-origin[0])+plane[1]*(y-origin[1])+plane[2])) for x,y in xy]
tris=tessellate_polygon([vs]);fs=[list(t) for t in tris]
me=bpy.data.meshes.new('R172_AUTHORED_EAST_MOAT_FLOOR');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
mat=bpy.data.materials.new('R172_MOAT_EARTH');mat.diffuse_color=(.24,.21,.15,1);mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=mat.diffuse_color;mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95;me.materials.append(mat)
s=bpy.context.scene;target=Vector((-161,-160,-19));s.camera.location=target+Vector((65,-90,105));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=95;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_HENDEK_ADAY_v007.blend'),compress=True)
(R/'reports/R172_MOAT_v007.json').write_text(json.dumps({'accepted':False,'method':'Independent planar floor; 2D terrain clipping, UV interpolation, no open-surface boolean','changes':changes,'pending':['Retaining junctions','Other moat and terrace regions','Source visual acceptance']},indent=2))
s.render.filepath=str(R/'renders/qa/R172_fort_moat_v007.png');bpy.ops.render.render(write_still=True)
print('R172_V007_DONE',changes)

