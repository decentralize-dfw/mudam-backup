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


ds=json.loads((R/'config/r291_south_roof.json').read_text());regions=[];records=[]
for i,d in enumerate(ds):
 assert d['samples']>2000 # Equipment/openings contaminate whole-roof residual; not source acceptance
 p=d['polygon'];z=d['cornerRoofs'];ma=bpy.data.materials.new('R291_BLACK_MEMBRANE' if i==0 else 'R291_PALE_ROOF');ma.use_nodes=True;bs=ma.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.31,.30,.26,1);bs.inputs['Roughness'].default_value=.85
 slab=prism(f'R291_ROOF_SLAB_{i}',p,[h-.25 for h in z],z,ma);regions.append(p)
 # Source-visible perimeter coping; cross-section provisional, measured perimeter retained.
 center=sum((Vector(q) for q in p),Vector((0,0)))/len(p)
 for j in range(len(p)):
  if j in d['unresolvedCropEdges']:continue
  a=Vector(p[j]);b=Vector(p[(j+1)%len(p)]);u=(b-a).normalized();n=Vector((-u.y,u.x))
  if n.dot(center-(a+b)/2)<0:n=-n
  pp=[tuple(a),tuple(b),tuple(b+n*.16),tuple(a+n*.16)];zz=[z[j],z[(j+1)%len(p)],z[(j+1)%len(p)],z[j]];prism(f'R291_COPING_{i}_{j}',pp,zz,[h+.16 for h in zz],bpy.data.materials['R262_PALE_COPING'])

# Independently traced visible rooflights; opening and reveal dimensions remain image-derived candidates.
lights=[(379,1360,24,13,[-.85,.53]),(424,1332,23,13,[-.85,.53]),(456,1310,22,13,[-.85,.53]),(488,1288,22,13,[-.85,.53]),
(366,1269,13,22,[.53,-.85]),(377,1245,13,22,[.53,-.85]),(390,1220,13,22,[.53,-.85]),(402,1197,13,22,[.53,-.85]),
(428,1131,14,22,[.53,-.85]),(447,1103,14,22,[.53,-.85]),(468,1082,14,22,[.53,-.85]),(492,1045,14,22,[.53,-.85]),(505,1027,14,22,[.53,-.85]),
(529,998,14,22,[.53,-.85]),(543,974,14,22,[.53,-.85]),(554,954,14,22,[.53,-.85]),(566,932,14,22,[.53,-.85]),(580,914,14,22,[.53,-.85]),
(578,938,14,22,[.53,-.85]),(600,952,14,22,[.53,-.85]),(564,964,14,22,[.53,-.85]),(588,976,14,22,[.53,-.85]),(558,1004,14,22,[.53,-.85]),
(632,985,14,22,[.53,-.85]),(641,971,14,22,[.53,-.85]),(674,974,14,22,[.53,-.85]),(682,961,14,22,[.53,-.85]),
(708,1008,14,22,[.53,-.85]),(718,1028,14,22,[.53,-.85]),(728,1052,14,22,[.53,-.85]),(747,1054,14,22,[.53,-.85]),
(729,1076,14,22,[.53,-.85]),(753,1074,14,22,[.53,-.85]),(771,1086,14,22,[.53,-.85]),(745,1102,14,22,[.53,-.85]),(730,1110,14,22,[.53,-.85]),(706,1130,14,22,[.53,-.85])]
lightRecords=[]
def xy(px,py):return Vector((150+px*.1875,300-py*.1875))
for k,(px,py,w,l,axis) in enumerate(lights):
 center=xy(px,py);u=Vector((axis[0],-axis[1])).normalized();v=Vector((-u.y,u.x));u*=l*.1875/2;v*=w*.1875/2
 pp=[tuple(center-u-v),tuple(center+u-v),tuple(center+u+v),tuple(center-u+v)]
 zz=[ds[0]['plane'][0]*(x-ds[0]['origin'][0])+ds[0]['plane'][1]*(y-ds[0]['origin'][1])+ds[0]['plane'][2] for x,y in pp]
 cutter=prism('TEMP_APERTURE',pp,[h-1 for h in zz],[h+1 for h in zz],ma);boolean(slab,cutter)
 prism(f'R291_ROOFLIGHT_GLASS_{k:02}',pp,[h-.06 for h in zz],[h-.02 for h in zz],glass)
 for j in range(4):
  aa=Vector(pp[j]);bb=Vector(pp[(j+1)%4]);normal=(center-(aa+bb)/2).normalized()*.12
  edge=[tuple(aa),tuple(bb),tuple(bb+normal),tuple(aa+normal)];h=(zz[j]+zz[(j+1)%4])/2
  prism(f'R291_ROOFLIGHT_REVEAL_{k:02}_{j}',edge,h-.25,h+.18,bpy.data.materials['R262_PALE_COPING'])
 lightRecords.append(dict(sourcePixel=[px,py],polygon=pp))

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

path=R/'scenes/MUDAM_R291_DOGU_IKI_BUYUK_CATI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.camera.location=(250,77,180);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=150;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R291_east_roofs_authored.png');bpy.ops.render.render(write_still=True)
for ob in s.objects:ob.select_set(ob.name.startswith('R291_'))
glb=R/'exports/r152_clean/r291_roofs_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R291_TWO_ROOFS.json').write_text(json.dumps(dict(accepted=False,published=False,sourceFits=ds,rooflights=lightRecords,clipping=records,checks=checks,limits=['South roof traced from R277; 37 rectangular rooflights modeled; round lights and remaining perimeter openings unresolved; whole roof source p90 1.028m so not accepted','Coping section and slab thickness provisional','Existing lower facade retained until independent reconstruction','Whole first-six scope incomplete']),indent=2));print('R291_READY',flush=True)
