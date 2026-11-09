from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R186_KUZEY_CEPHELER_v001.blend'))
rows=json.loads((R/'config/r187_cut_planes.json').read_text())
for o in list(bpy.data.objects):
 if o.name in ['R172_AUTHORED_EAST_MOAT_FLOOR','R172_MOAT_TERRAIN_JOIN'] or o.name.startswith(('R181_CLOSED_WEST','R181_CLOSED_CENTRAL')):bpy.data.objects.remove(o,do_unlink=True)
changes=[]
for row in rows:
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
 for obj in list(bpy.context.scene.objects):
  if obj.type!='MESH' or not (obj.name in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN','R154_FAR_ROADS','R161_ROAD_CONNECTIONS'] or obj.name.startswith('R152_PATH_')):continue
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
 if row['name']=='STATION_FOOTPRINT':continue
 c=row['plane'];origin=row['origin'];vs=[Vector((x,y,c[0]*(x-origin[0])+c[1]*(y-origin[1])+c[2])) for x,y in xy]
 me=bpy.data.meshes.new('R187_'+row['name']);me.from_pydata(vs,[],[list(t) for t in tessellate_polygon([vs])]);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);me.materials.append(bpy.data.materials['R172_MOAT_EARTH'])
 uv=me.uv_layers.new()
 for l in me.loops:v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x/3,v.y/3)
(R/'reports/R187_WHOLE_FORT_v001.json').write_text(json.dumps(dict(accepted=False,changes=changes,source_planes=rows,limits=['Boundary terrain transitions require visual check','West apron source contaminated by small objects']),indent=2))
s=bpy.context.scene;t=Vector((-210,-175,-20));s.camera.location=t+Vector((90,-150,180));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=260;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R187_BUTUN_KALE_v001.blend'),compress=True)
s.render.filepath=str(R/'renders/qa/R187_whole_fort_v001.png');bpy.ops.render.render(write_still=True)
print('R178_APRONS_DONE')
