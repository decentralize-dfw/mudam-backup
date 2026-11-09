from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R280_DOGU_KULE_CEPHE_ADAY_v001.blend'))
parts=json.loads((R/'config/r233_courtyard_roof_planes.json').read_text())['parts'];poly=parts[2]['polygon'];light=parts[0]
mat=bpy.data.materials.new('R247_ROOF_MEMBRANE');mat.diffuse_color=(.13,.15,.14,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Roughness'].default_value=.83
glass=bpy.data.materials['R221_BLUE_GREY_GLASS'];wall=bpy.data.materials['R227_UNRESOLVED_FACADE']
def prism(name,p,bot,top,material):
 n=len(p);vs=[(x,y,z[i] if isinstance(z,list) else z) for z in [bot,top] for i,(x,y) in enumerate(p)];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(material);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def boolean(o,c):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Architectural opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)

bays=json.loads((R/'config/r281_roof_bays.json').read_text());gaps=json.loads((R/'config/r282_roof_gaps.json').read_text());extent=[bays[0]['polygon'][0],bays[0]['polygon'][1],gaps[-1]['polygon'][2],gaps[-1]['polygon'][3]]
# Independently drawn roof bays, each an analytic planar architectural solid.
mineral=bpy.data.materials.new('R284_MINERAL_GRAVEL');mineral.use_nodes=True;mineral.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.42,.35,.26,1);mineral.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.88
base=18.5;body=prism('R284_NORTH_HALL',extent,2.1,base,wall)
for i,d in enumerate(bays):
 p=d['polygon'];z=d['cornerRoofs'];prism(f'R284_MINERAL_ROOF_BAY_{i:02}',p,base-.05,z,mineral)
 # Continuous glass strip fills the remaining interval to the following bay, with shared endpoints.
 nextp=bays[i+1]['polygon'] if i+1<len(bays) else [gaps[-1]['polygon'][3],gaps[-1]['polygon'][2]]
 glasspoly=[p[3],p[2],nextp[1],nextp[0]];g=gaps[i];origin=g['origin'];c=g['plane'];gz=[c[0]*(x-origin[0])+c[1]*(y-origin[1])+c[2] for x,y in glasspoly]
 prism(f'R284_GLAZED_ROOF_STRIP_{i:02}',glasspoly,base-.05,gz,glass)
 # Mineral end curbs close the seams without making an unsupported extra canopy.
 for j in [0,2]:
  a=Vector(glasspoly[j]);b=Vector(glasspoly[(j+1)%4]);n=(b-a).normalized();q=Vector((-n.y,n.x))*.035;pp=[tuple(a-q),tuple(b-q),tuple(b+q),tuple(a+q)];zz=[gz[j]+.04,gz[(j+1)%4]+.04,gz[(j+1)%4]+.04,gz[j]+.04];prism(f'R284_STRIP_FRAME_{i:02}_{j}',pp,[v-.08 for v in zz],zz,bpy.data.materials['R221_DARK_FRAMES'])
def inside(p):
 cs=[(extent[(i+1)%4][0]-a[0])*(p.y-a[1])-(extent[(i+1)%4][1]-a[1])*(p.x-a[0]) for i,a in enumerate(extent)];return min(cs)>=0 or max(cs)<=0
regions=[extent];records=[]
def clip(points,a,b,sign,inside):
 out=[]
 for j,P in enumerate(points):
  Q=points[(j+1)%len(points)];f=lambda X:sign*((b[0]-a[0])*(X[1]-a[1])-(b[1]-a[1])*(X[0]-a[0]));dp=f(P);dq=f(Q);ip=dp>=-1e-8 if inside else dp<=1e-8;iq=dq>=-1e-8 if inside else dq<=1e-8
  if ip:out.append(P)
  if ip!=iq:
   t=dp/(dp-dq);out.append(tuple(p+(q-p)*t for p,q in zip(P,Q)))
 return out
for ob in [bpy.data.objects['R166_MEASURED_ENVELOPE']]:
 me=ob.data;me.calc_loop_triangles();uvs=list(me.uv_layers);verts=[];faces=[];mis=[];attrs=[];changed=0
 for tr in me.loop_triangles:
  points=[]
  for li in tr.loops:
   q=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;points.append(tuple(q)+tuple(v for layer in uvs for v in layer.data[li].uv))
  chunks=[points]
  for region in regions:
   sign=1 if sum(region[i][0]*region[(i+1)%4][1]-region[(i+1)%4][0]*region[i][1] for i in range(4))>0 else -1;result=[]
   for chunk in chunks:
    if max(p[0] for p in chunk)<min(p[0] for p in region) or min(p[0] for p in chunk)>max(p[0] for p in region) or max(p[1] for p in chunk)<min(p[1] for p in region) or min(p[1] for p in chunk)>max(p[1] for p in region):result.append(chunk);continue
    remaining=chunk
    for i,a in enumerate(region):
     if len(remaining)<3:break
     b=region[(i+1)%4];outside=clip(remaining,a,b,sign,False)
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
  new=bpy.data.meshes.new(ob.name+'_ROOF_CUT');new.from_pydata(verts,[],faces);new.update()
  for ma in me.materials:new.materials.append(ma)
  for i,ma in enumerate(mis):new.polygons[i].material_index=ma
  for j,layer in enumerate(uvs):
   dst=new.uv_layers.new(name=layer.name)
   for l in new.loops:dst.data[l.index].uv=attrs[l.vertex_index][j*2:j*2+2]
  ob.data=new;records.append(dict(name=ob.name,cutTriangles=changed))
count=sum(r["cutTriangles"] for r in records)
path=R/'scenes/MUDAM_R284_DOGU_UZUN_CATI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.camera.location=(340,235,180);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=100;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R284_north_roof_authored.png');bpy.ops.render.render(write_still=True)
for ob in s.objects:ob.select_set(ob.name.startswith('R284_'))
glb=R/'exports/r152_clean/r284_roof_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R284_NORTH_ROOF.json').write_text(json.dumps(dict(accepted=False,published=False,removedReferenceVertices=count,checks=checks,bays=bays,gaps=gaps,limits=['Seven bays have p90 over0.25m and need source refinement before acceptance','Hidden hall base provisional','Whole low podium and adjoining facades still inherited and require independent reconstruction']),indent=2));print('R284_READY',checks,flush=True)
