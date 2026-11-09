import bpy,bmesh,json,math
from mathutils.geometry import tessellate_polygon,delaunay_2d_cdt
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R323_BATI_RAMPA_SUR_ADAY_v001.blend'))
outer=json.loads((R/'reports/R323_WEST_CREST_CONTROLS.json').read_text());poly=[p['measuredCrest'][:2] for p in outer]
inner_pixels=[(849,859),(790,805),(796,652),(748,605),(670,548),(600,540),(495,522)]
poly += [[-120+x*220/1400,95-y*220/1400] for x,y in inner_pixels]
stations=json.loads((R/'reports/R322_WEST_TERRACE_SAMPLES.json').read_text())['source'];extra=json.loads((R/'reports/R322_INDEPENDENT_GROUND_CHECK.json').read_text())['source'];stations=stations[:8]+extra[7:9];path=[Vector((*p['xy'],p['medianZ'])) for p in stations]
def inside(p):
 result=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>p.y)!=(b[1]>p.y) and p.x<(b[0]-a[0])*(p.y-a[1])/(b[1]-a[1])+a[0]:result=not result
 return result
def elevation(p):
 best=(1e30,None)
 for a,b in zip(path,path[1:]):
  d=(b-a).to_2d();t=max(0,min(1,(p-a.to_2d()).dot(d)/d.length_squared));dist=(p-a.to_2d()-d*t).length
  if dist<best[0]:best=(dist,a.z+(b.z-a.z)*t)
 near=(1e30,None)
 for row0,row1 in zip(outer,outer[1:]):
  a=Vector(row0['measuredCrest']);b=Vector(row1['measuredCrest']);d=(b-a).to_2d();t=max(0,min(1,(p-a.to_2d()).dot(d)/d.length_squared));dist=(p-a.to_2d()-d*t).length
  if dist<near[0]:near=(dist,a.z+(b.z-a.z)*t-.15)
 w=max(0,1-near[0]/1.3);w=w*w*(3-2*w)
 value=best[1]*(1-w)+near[1]*w
 px=(p.x+120)*1400/220;py=(95-p.y)*1400/220
 if 598<=px<=669 and py>=568:
  t=(px-598)/71
  ramp=-6.02+(-3.73+6.02)*t
  cross=max(0,min(1,(py-568)/13))
  value=-3.34*(1-cross)+ramp*cross
 return value

tri=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]])
regions=[]
for face in tri:
 regions.append([poly[i] if isinstance(i,int) else (i.x,i.y) for i in face])
records=[]
def clip(points,a,b,sign,inside):
 out=[]
 for j,P in enumerate(points):
  Q=points[(j+1)%len(points)];f=lambda X:sign*((b[0]-a[0])*(X[1]-a[1])-(b[1]-a[1])*(X[0]-a[0]));dp=f(P);dq=f(Q);ip=dp>=-1e-8 if inside else dp<=1e-8;iq=dq>=-1e-8 if inside else dq<=1e-8
  if ip:out.append(P)
  if ip!=iq:
   t=dp/(dp-dq);out.append(tuple(p+(q-p)*t for p,q in zip(P,Q)))
 return out
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or ob.name not in ['R152_CLASS2_TERRAIN']:continue
 me=ob.data;me.calc_loop_triangles();uvs=list(me.uv_layers);verts=[];faces=[];mis=[];attrs=[];changed=0
 for tr in me.loop_triangles:
  points=[]
  for li in tr.loops:
   q=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;points.append(tuple(q)+tuple(v for layer in uvs for v in layer.data[li].uv))
  chunks=[points]
  for region in regions:
   sign=1 if sum(region[i][0]*region[(i+1)%len(region)][1]-region[(i+1)%len(region)][0]*region[i][1] for i in range(len(region)))>0 else -1;result=[]
   for chunk in chunks:
    if max(p[0] for p in chunk)<min(p[0] for p in region) or min(p[0] for p in chunk)>max(p[0] for p in region) or max(p[1] for p in chunk)<min(p[1] for p in region) or min(p[1] for p in chunk)>max(p[1] for p in region):result.append(chunk);continue
    remaining=chunk
    for i,a in enumerate(region):
     if len(remaining)<3:break
     b=region[(i+1)%len(region)];outside=clip(remaining,a,b,sign,False)
     if len(outside)>2:result.append(outside)
     remaining=clip(remaining,a,b,sign,True)
    if len(remaining)>2:changed+=1
   chunks=result
  for chunk in chunks:
   for i in range(1,len(chunk)-1):
    tri=[chunk[0],chunk[i],chunk[i+1]]
    if (Vector(tri[1][:3])-Vector(tri[0][:3])).cross(Vector(tri[2][:3])-Vector(tri[0][:3])).length<1e-8:continue
    k=len(verts);verts.extend(tuple(ob.matrix_world.inverted()@Vector(p[:3])) for p in tri);attrs.extend(p[3:] for p in tri);faces.append((k,k+1,k+2));mis.append(tr.material_index)
 if changed:
  new=bpy.data.meshes.new(ob.name+'_COURT_CUT');new.from_pydata(verts,[],faces);new.update()
  for ma in me.materials:new.materials.append(ma)
  for i,ma in enumerate(mis):new.polygons[i].material_index=ma
  for j,layer in enumerate(uvs):
   dst=new.uv_layers.new(name=layer.name)
   for l in new.loops:dst.data[l.index].uv=attrs[l.vertex_index][j*2:j*2+2]
  ob.data=new;records.append(dict(name=ob.name,cutTriangles=changed))

points=list(poly)
for py in [568,581]:
 for px in range(598,670,2):
  p=(-120+px*220/1400,95-py*220/1400)
  if inside(Vector(p)):points.append(p)

for a,b in zip(poly,poly[1:]+poly[:1]):
 a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/.7))
 points.extend(tuple(a.lerp(b,i/n)) for i in range(1,n))
for x in range(-52,18):
 for y in range(-50,16):
  if inside(Vector((x,y))):points.append((x,y))
vv,ee,ff,*_=delaunay_2d_cdt([Vector(p) for p in points],[(i,(i+1)%len(poly)) for i in range(len(poly))],[list(range(len(poly)))],1,1e-5)
vs=[(p.x,p.y,elevation(p)) for p in vv];me=bpy.data.meshes.new('R322_WEST_MUSEUM_TERRACE');me.from_pydata(vs,[],ff);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.objects['R152_CLASS2_TERRAIN'].data.materials[0])
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();u=me.uv_layers.new(name='UVMap');micro=me.uv_layers.new(name='MicroUV');me.uv_layers.active=u
for l in me.loops:
 q=me.vertices[me.loops[l.index].vertex_index].co;u.data[l.index].uv=((q.x+500)/1150,(q.y+450)/1100);micro.data[l.index].uv=(q.x/2,q.y/2)
for f in me.polygons:f.use_smooth=True
o['level_id']='SITE';o['source']='Independent terrace surface with nine level controls and source-traced boundary; exact terrain cut. No scan geometry.'
edits=records
out=R/'scenes/MUDAM_R323_BATI_RAMPA_TERAS_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));bpy.ops.object.select_all(action='DESELECT');bpy.data.objects['R152_CLASS2_TERRAIN'].select_set(True);bpy.data.objects['R322_WEST_MUSEUM_TERRACE'].select_set(True)
glb=R/'exports/r152_clean/r323_west_ramp_terrain_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-140,-140,75));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-45,-40,-2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=120;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('R322_Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R323_west_ramp_terrace_v001.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':checks.append(dict(name=o.name,nonFinite=sum(not all(math.isfinite(x) for x in v.co) for v in o.data.vertices),zeroArea=sum(p.area<1e-10 for p in o.data.polygons)))
(R/'reports/R323_WEST_RAMP_TERRACE.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,polygon=poly,stations=stations,edits=edits,glb=checks,limits=['Ramp and upper terrace are separate analytic grade domains; width and adjoining limits remain candidates','Boundary triangulation and materials need source comparison','Source controls do not prove entire ring exact']),indent=2));print('R322_READY',len(edits),checks)


