from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R273_ERASMUS_SAG_AVLU_ADAY_v002.blend'))
parts=json.loads((R/'config/r233_courtyard_roof_planes.json').read_text())['parts'];poly=parts[2]['polygon'];light=parts[0]
mat=bpy.data.materials.new('R247_ROOF_MEMBRANE');mat.diffuse_color=(.13,.15,.14,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Roughness'].default_value=.83
glass=bpy.data.materials['R221_BLUE_GREY_GLASS'];wall=bpy.data.materials['R227_UNRESOLVED_FACADE']
def prism(name,p,bot,top,material):
 n=len(p);vs=[(x,y,z[i] if isinstance(z,list) else z) for z in [bot,top] for i,(x,y) in enumerate(p)];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(material);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def boolean(o,c):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Architectural opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)

poly=[(82.45,389.866667),(90.033333,397.2),(99.533333,386.2),(92.033333,379.7)]
# Robust vegetation height is a provisional envelope, not a surveyed flat plane.
body=prism('R275_LEFT_COURT_HALL',poly,.5,5.85,wall)
cx=sum(x for x,y in poly)/4;cy=sum(y for x,y in poly)/4;inner=[(cx+(x-cx)*.94,cy+(y-cy)*.94) for x,y in poly];boolean(body,prism('Cavity',inner,.85,5.55,wall));prism('R275_LEFT_COURT_ROOF',poly,5.85,5.9,mat)
p=json.loads((R/'config/r274_left_court_planes.json').read_text())[0]['polygon'];o=prism('R275_LEFT_GREEN_ROOF',p,5.9,5.98,bpy.data.materials['R262_SEDUM_ROOF']);uv=o.data.uv_layers.new()
for l in o.data.loops:
 q=o.data.vertices[l.vertex_index].co;uv.data[l.index].uv=((q.x-82.7)/20,(q.y-377.2)/20)
# Remove only terrain triangles inside these two authored hall footprints. Interpolate UV at exact cut edges.
right=[(155.65,453.216667),(163.233333,460.55),(172.733333,449.55),(165.233333,443.05)]
regions=[poly,right];records=[]
def clip(points,a,b,sign,inside):
 out=[]
 for j,P in enumerate(points):
  Q=points[(j+1)%len(points)];f=lambda X:sign*((b[0]-a[0])*(X[1]-a[1])-(b[1]-a[1])*(X[0]-a[0]));dp=f(P);dq=f(Q);ip=dp>=-1e-8 if inside else dp<=1e-8;iq=dq>=-1e-8 if inside else dq<=1e-8
  if ip:out.append(P)
  if ip!=iq:
   t=dp/(dp-dq);out.append(tuple(p+(q-p)*t for p,q in zip(P,Q)))
 return out
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or ob.name not in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN','R182_EXTENSION_GROUND']:continue
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
  new=bpy.data.meshes.new(ob.name+'_COURT_CUT');new.from_pydata(verts,[],faces);new.update()
  for ma in me.materials:new.materials.append(ma)
  for i,ma in enumerate(mis):new.polygons[i].material_index=ma
  for j,layer in enumerate(uvs):
   dst=new.uv_layers.new(name=layer.name)
   for l in new.loops:dst.data[l.index].uv=attrs[l.vertex_index][j*2:j*2+2]
  ob.data=new;records.append(dict(name=ob.name,cutTriangles=changed))
print('TERRAIN_CUT',records,flush=True)
out=R/'scenes/MUDAM_R275_AVLU_ZEMIN_BIRLESIM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));s=bpy.context.scene;s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=8
for name,loc in [('left',(92.7,387.2,100)),('right',(165.9,450.55,100))]:
 s.camera.location=loc;s.render.filepath=str(R/f'renders/qa/R275_{name}_court_authored.png');bpy.ops.render.render(write_still=True)
for ob in s.objects:ob.select_set(ob.name.startswith(('R273_','R275_')))
glb=R/'exports/r152_clean/r275_courts_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R275_COURT_GROUND.json').write_text(json.dumps(dict(accepted=False,published=False,terrainCuts=records,checks=checks,limits=['Left vegetation height fitting is not sufficiently planar: provisional 5.9m envelope','Hall footprints traced visually, concealed lower walls provisional','Whole first-six-region acceptance incomplete']),indent=2));print('R275_READY',checks,flush=True)
