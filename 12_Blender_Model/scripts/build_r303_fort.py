from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R301_ALT_MAHALLE_ZEMIN_BAGLANTISI_ADAY_v001.blend'));rows=json.loads((R/'config/r303_fort_geometry.json').read_text());changed=[]
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name in ['R154_FAR_GROUND','R182_EXTENSION_GROUND']:
  o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True)
for name in ['R181_CLOSED_NORTH_COURT','R172_AUTHORED_NORTH_PLATFORM','R172_NORTH_PLATFORM_TERRAIN_JOIN']:
 if name in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
# Polygon subtraction by each authored triangle; preserve all existing UV values outside footprint.
for row in rows:
 for triangle in row['faces']:
  xy=[row['vertices'][i][:2] for i in triangle]
  if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))<0:xy.reverse()
  edges=list(zip(xy,xy[1:]+xy[:1]));bounds=[min(p[0] for p in xy),max(p[0] for p in xy),min(p[1] for p in xy),max(p[1] for p in xy)]
  def split(poly,a,b):
   def d(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
   ins=[];outs=[]
   for p,q in zip(poly,poly[1:]+poly[:1]):
    dp,dq=d(p),d(q);(ins if dp>=0 else outs).append(p)
    if dp*dq<0:
     t=dp/(dp-dq);v=[u+(w-u)*t for u,w in zip(p,q)];ins.append(v);outs.append(v)
   return ins,outs
  for o in list(bpy.context.scene.objects):
   if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS','R182_EXTENSION_GROUND','R182_EXTENSION_ROADS'] or o.name.startswith('R152_PATH_')):continue
   me=o.data;me.calc_loop_triangles();uv=me.uv_layers.active;vout=[];fout=[];uout=[];mout=[];cut=0;M=o.matrix_world;inv=M.inverted()
   for tri in me.loop_triangles:
    poly=[]
    for vi,li in zip(tri.vertices,tri.loops):
     p=M@me.vertices[vi].co;poly.append([*p,*(uv.data[li].uv if uv else (0,0))])
    if max(p[0] for p in poly)<bounds[0] or min(p[0] for p in poly)>bounds[1] or max(p[1] for p in poly)<bounds[2] or min(p[1] for p in poly)>bounds[3]:pieces=[poly]
    else:
     remain=poly;pieces=[]
     for a,b in edges:
      if len(remain)<3:break
      remain,out=split(remain,a,b)
      if len(out)>=3:pieces.append(out)
     if len(remain)>=3:cut+=1
    for piece in pieces:
     k=len(vout);vout.extend(inv@Vector(p[:3]) for p in piece);uout.extend(p[3:] for p in piece)
     for j in range(1,len(piece)-1):fout.append((k,k+j,k+j+1));mout.append(tri.material_index)
   if not cut:continue
   new=bpy.data.meshes.new(me.name+'_R303');new.from_pydata(vout,[],fout);new.update()
   for m in me.materials:new.materials.append(m)
   layer=new.uv_layers.new()
   for p,mi in zip(new.polygons,mout):
    p.material_index=mi;p.use_smooth=True
    for li in p.loop_indices:layer.data[li].uv=uout[new.loops[li].vertex_index]
   o.data=new
   if o.name not in changed:changed.append(o.name)
 # Closed authored earthwork solid. Bottom is construction closure, not surveyed foundation.
 top=row['vertices'];n=len(top);bottom=[]
 for x,y,z in top:
  h,*_=ground.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),300);bottom.append((x,y,min(z-.3,h.z-.12) if h else z-2))
 counts={}
 for f in row['faces']:
  for a,b in zip(f,f[1:]+f[:1]):k=tuple(sorted((a,b)));counts[k]=counts.get(k,0)+1
 boundary=[e for e,c in counts.items() if c==1];faces=row['faces']+[tuple(n+i for i in reversed(f)) for f in row['faces']]+[(a,b,b+n,a+n) for a,b in boundary]
 name='R303_'+row['name'];me=bpy.data.meshes.new(name);me.from_pydata(top+bottom,[],faces);me.materials.append(bpy.data.materials['R234_DRY_FORT_EARTH']);me.materials.append(bpy.data.materials['R154_FORT_STONE_PBR']);me.update()
 for p in me.polygons:
  if p.index>=2*len(row['faces']):p.material_index=1
 uv=me.uv_layers.new()
 for p in me.polygons:
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((v.x+v.y)/4,v.z/3) if p.material_index else (v.x/8,v.y/8)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);changed.append(name)
path=R/'scenes/MUDAM_R303_KALE_KUZEY_DOGU_TERASLARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;t=Vector((-175,-135,-15));s.camera.location=t+Vector((100,-160,200));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=300;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R303_fort_candidate.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R303_'))
glb=R/'exports/r152_clean/r303_fort_terraces_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R303_FORT_TERRACES.json').write_text(json.dumps(dict(accepted=False,published=False,changed=changed,checks=checks,domains=rows,limits=['North court bank and internal ruins not completed','Eastern occluded bank corner interpolated; whole fort acceptance pending']),indent=2));print('R303_READY')
