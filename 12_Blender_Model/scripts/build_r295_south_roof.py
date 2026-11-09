from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R289_DOGU_IKI_BUYUK_CATI_ADAY_v001.blend'))
parts=json.loads((R/'config/r233_courtyard_roof_planes.json').read_text())['parts'];poly=parts[2]['polygon'];light=parts[0]
mat=bpy.data.materials.new('R247_ROOF_MEMBRANE');mat.diffuse_color=(.13,.15,.14,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Roughness'].default_value=.83
glass=bpy.data.materials['R221_BLUE_GREY_GLASS'];wall=bpy.data.materials['R227_UNRESOLVED_FACADE']
def prism(name,p,bot,top,material):
 n=len(p);vs=[(x,y,z[i] if isinstance(z,list) else z) for z in [bot,top] for i,(x,y) in enumerate(p)];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(material);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def boolean(o,c):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Architectural opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)


ds=json.loads((R/'config/r295_south_roof.json').read_text());regions=[];records=[]
for i,d in enumerate(ds):
 assert d['samples']>2000 # Equipment/openings contaminate whole-roof residual; not source acceptance
 p=d['polygon'];z=d['cornerRoofs'];ma=bpy.data.materials.new('R295_BLACK_MEMBRANE' if i==0 else 'R295_PALE_ROOF');ma.use_nodes=True;bs=ma.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.31,.30,.26,1);bs.inputs['Roughness'].default_value=.85
 slab=prism(f'R295_ROOF_SLAB_{i}',p,[h-.25 for h in z],z,ma);regions.append(p)
 # Source-visible perimeter coping; cross-section provisional, measured perimeter retained.
 center=sum((Vector(q) for q in p),Vector((0,0)))/len(p)
 for j in range(len(p)):
  if j in d['unresolvedCropEdges']:continue
  a=Vector(p[j]);b=Vector(p[(j+1)%len(p)]);u=(b-a).normalized();n=Vector((-u.y,u.x))
  if n.dot(center-(a+b)/2)<0:n=-n
  pp=[tuple(a),tuple(b),tuple(b+n*.16),tuple(a+n*.16)];zz=[z[j],z[(j+1)%len(p)],z[(j+1)%len(p)],z[j]];prism(f'R295_COPING_{i}_{j}',pp,zz,[h+.16 for h in zz],bpy.data.materials['R262_PALE_COPING'])

# Independently traced visible rooflights; opening and reveal dimensions remain image-derived candidates.
lights=[(630, 240, 15, 24, [0.55, -0.835]), (659, 226, 15, 24, [0.55, -0.835]), (676, 236, 15, 24, [0.55, -0.835]), (700, 224, 15, 24, [0.55, -0.835]), (740, 250, 15, 24, [0.55, -0.835]), (631, 270, 15, 24, [0.55, -0.835]), (685, 275, 15, 24, [0.55, -0.835]), (590, 305, 15, 24, [0.55, -0.835]), (630, 330, 15, 24, [0.55, -0.835]), (538, 360, 15, 24, [0.55, -0.835]), (565, 377, 15, 24, [0.55, -0.835]), (486, 447, 15, 24, [0.55, -0.835]), (511, 432, 15, 24, [0.55, -0.835]), (442, 511, 15, 24, [0.55, -0.835]), (391, 595, 15, 24, [0.55, -0.835]), (390, 627, 15, 24, [0.55, -0.835]), (365, 669, 15, 24, [0.55, -0.835]), (351, 691, 15, 24, [0.55, -0.835]), (350, 717, 15, 24, [0.55, -0.835]), (390, 717, 15, 24, [0.55, -0.835]), (390, 745, 15, 24, [0.55, -0.835]), (372, 848, 14, 40, [0.835, -0.55]), (421, 805, 15, 24, [0.835, -0.55]), (445, 800, 15, 24, [0.835, -0.55]), (469, 791, 15, 24, [0.835, -0.55]), (472, 749, 15, 24, [0.835, -0.55]), (533, 746, 15, 24, [0.835, -0.55]), (797, 286, 15, 24, [0.835, -0.55]), (820, 270, 15, 24, [0.835, -0.55]), (880, 323, 15, 24, [0.835, -0.55]), (868, 349, 15, 24, [0.835, -0.55]), (895, 391, 15, 24, [0.835, -0.55]), (926, 388, 15, 24, [0.835, -0.55]), (884, 420, 15, 24, [0.835, -0.55]), (927, 428, 15, 24, [0.835, -0.55]), (952, 428, 15, 24, [0.835, -0.55]), (884, 459, 15, 24, [0.835, -0.55]), (901, 488, 15, 24, [0.835, -0.55]), (921, 475, 15, 24, [0.835, -0.55]), (860, 518, 15, 24, [0.835, -0.55])]
lights.append((650,188,15,24,[.55,-.835]))
lightRecords=[]
def xy(px,py):return Vector((175+px*.125,152-py*.125))
for k,(px,py,w,l,axis) in enumerate(lights):
 center=xy(px,py);u=Vector((axis[0],-axis[1])).normalized();v=Vector((-u.y,u.x));u*=l*.125/2;v*=w*.125/2
 pp=[tuple(center-u-v),tuple(center+u-v),tuple(center+u+v),tuple(center-u+v)]
 zz=[ds[0]['plane'][0]*(x-ds[0]['origin'][0])+ds[0]['plane'][1]*(y-ds[0]['origin'][1])+ds[0]['plane'][2] for x,y in pp]
 cutter=prism('TEMP_APERTURE',pp,[h-1 for h in zz],[h+1 for h in zz],ma);boolean(slab,cutter)
 prism(f'R295_ROOFLIGHT_GLASS_{k:02}',pp,[h-.06 for h in zz],[h-.02 for h in zz],glass)
 for j in range(4):
  aa=Vector(pp[j]);bb=Vector(pp[(j+1)%4]);normal=(center-(aa+bb)/2).normalized()*.12
  edge=[tuple(aa),tuple(bb),tuple(bb+normal),tuple(aa+normal)];h=(zz[j]+zz[(j+1)%4])/2
  prism(f'R295_ROOFLIGHT_REVEAL_{k:02}_{j}',edge,h-.25,h+.18,bpy.data.materials['R262_PALE_COPING'])
 lightRecords.append(dict(sourcePixel=[px,py],polygon=pp))


from math import sin,cos,pi
for k,(px,py,r) in enumerate([(445,599,9),(445,631,10),(458,665,10),(466,689,9),(495,695,9),(503,660,9)]):
 center=xy(px,py);pp=[tuple(center+Vector((cos(j*pi/12),sin(j*pi/12)))*r*.125) for j in range(24)]
 z=ds[0]['plane'][0]*(center.x-ds[0]['origin'][0])+ds[0]['plane'][1]*(center.y-ds[0]['origin'][1])+ds[0]['plane'][2]
 cutter=prism('TEMP_ROUND_APERTURE',pp,z-1,z+1,ma);boolean(slab,cutter)
 prism(f'R295_ROUND_GLASS_{k}',pp,z-.06,z-.02,glass)
 for j in range(24):
  a=Vector(pp[j]);b=Vector(pp[(j+1)%24]);aa=center+(a-center)*.86;bb=center+(b-center)*.86
  prism(f'R295_ROUND_REVEAL_{k}_{j}',[tuple(a),tuple(b),tuple(bb),tuple(aa)],z-.25,z+.16,bpy.data.materials['R262_PALE_COPING'])
 lightRecords.append(dict(sourcePixel=[px,py],circleRadius=r*.125,polygon=pp))

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
  for ridx,region in enumerate(regions):
   sign=1 if sum(region[i][0]*region[(i+1)%len(region)][1]-region[(i+1)%len(region)][0]*region[i][1] for i in range(len(region)))>0 else -1;result=[]
   for chunk in chunks:
    if max(p[0] for p in chunk)<min(p[0] for p in region) or min(p[0] for p in chunk)>max(p[0] for p in region) or max(p[1] for p in chunk)<min(p[1] for p in region) or min(p[1] for p in chunk)>max(p[1] for p in region):result.append(chunk);continue
    remaining=chunk
    # Split at slab underside before removing old roof: existing lower facade retained.
    cutz=min(ds[ridx]['cornerRoofs'])-.25
    below=[];above=[]
    for j,P in enumerate(chunk):
     Q=chunk[(j+1)%len(chunk)];ip=P[2]>=cutz;iq=Q[2]>=cutz
     (above if ip else below).append(P)
     if ip!=iq:
      t=(cutz-P[2])/(Q[2]-P[2]);hit=tuple(a+(b-a)*t for a,b in zip(P,Q));above.append(hit);below.append(hit)
    if len(below)>2:result.append(below)
    remaining=above
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
  new=bpy.data.meshes.new(ob.name+'_ROOF_CUT');new.from_pydata(verts,[],faces);new.update()
  for ma in me.materials:new.materials.append(ma)
  for i,ma in enumerate(mis):new.polygons[i].material_index=ma
  for j,layer in enumerate(uvs):
   dst=new.uv_layers.new(name=layer.name)
   for l in new.loops:dst.data[l.index].uv=attrs[l.vertex_index][j*2:j*2+2]
  ob.data=new;records.append(dict(name=ob.name,cutTriangles=changed))
count=sum(r["cutTriangles"] for r in records)

path=R/'scenes/MUDAM_R295_DOGU_IKI_BUYUK_CATI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.camera.location=(250,77,180);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=150;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R295_east_roofs_authored.png');bpy.ops.render.render(write_still=True)
for ob in s.objects:ob.select_set(ob.name.startswith('R295_'))
glb=R/'exports/r152_clean/r295_roofs_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R295_TWO_ROOFS.json').write_text(json.dumps(dict(accepted=False,published=False,sourceFits=ds,rooflights=lightRecords,clipping=records,checks=checks,limits=['South roof traced from R277; 41 rectangular and 6 round rooflights independently traced from R291 close source; remainder outside slab unresolved; whole roof source p90 1.028m so not accepted','Coping section and slab thickness provisional','Existing lower facade retained until independent reconstruction','Whole first-six scope incomplete']),indent=2));print('R295_READY',flush=True)
