import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R261_KULE_SERVIS_BOSLUKLARI_ADAY_v002.blend'))
def mat(n,c):
 m=bpy.data.materials.new(n);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=.92;return m
sedum=mat('R262_SEDUM_ROOF',(.2,.22,.1));nodes=sedum.node_tree.nodes;links=sedum.node_tree.links;b=nodes['Principled BSDF'];tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures/r262/sedum_base.png'));links.new(tex.outputs['Color'],b.inputs['Base Color']);nt=nodes.new('ShaderNodeTexImage');nt.image=bpy.data.images.load(str(R/'textures/r262/sedum_normal.png'));nt.image.colorspace_settings.name='Non-Color';nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.35;links.new(nt.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],b.inputs['Normal']);stone=mat('R262_PALE_COPING',(.48,.43,.36));pink=mat('R262_MINERAL_LOWER_ROOF',(.32,.255,.245))
def hull(points):
 pts=sorted(set(points));cross=lambda a,b,c:(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);lo=[];hi=[]
 for p in pts:
  while len(lo)>1 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in pts[::-1]:
  while len(hi)>1 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return [Vector(v) for v in lo[:-1]+hi[:-1]]
def prism(n,poly,z0,z1,ma):
 N=len(poly);v=[(p.x,p.y,z) for z in [z0,z1] for p in poly];f=[tuple(reversed(range(N))),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.materials.append(ma);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new();xs=[p.x for p in poly];ys=[p.y for p in poly]
 for loop in me.loops:
  p=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((p.x-min(xs))/max(.01,max(xs)-min(xs)),(p.y-min(ys))/max(.01,max(ys)-min(ys)))
 o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o)
records=[];lower=[]
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 if o.name.startswith(('R216_ERASMUS_WING','R217_ERASMUS_WING')):
  pts=[o.matrix_world@v.co for v in o.data.vertices];top=max(p.z for p in pts);poly=hull([(round(p.x,5),round(p.y,5)) for p in pts if abs(p.z-top)<.02]);inner=[]
  for i,p in enumerate(poly):
   a=(p-poly[i-1]).normalized();b=(poly[(i+1)%len(poly)]-p).normalized();na=Vector((-a.y,a.x));nb=Vector((-b.y,b.x));nn=(na+nb).normalized();inner.append(p+nn*.32/max(.2,nn.dot(nb)))
  prism('R262_SEDUM_'+o.name,inner,top,top+.08,sedum)
  for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):prism('R262_COPING_'+o.name+'_'+str(i),[a,b,inner[(i+1)%len(poly)],inner[i]],top,top+.27,stone)
  records.append(dict(name=o.name,top=top,ring=[list(p) for p in poly]))
 elif o.name.startswith(('R222_ERASMUS_FRONT','R225_ERASMUS_FRONT','R218_ERASMUS_FRONT','R219_ERASMUS_FRONT')):
  o.data.materials.append(pink);idx=len(o.data.materials)-1;n=0
  for p in o.data.polygons:
   if p.normal.z>.9:p.material_index=idx;n+=1
  lower.append(dict(name=o.name,faces=n))
assert len(records)==7
for im in bpy.data.images:
 if im.name.startswith('sedum_'):im.pack()
path=R/'scenes/MUDAM_R262_ERASMUS_CATI_SISTEMLERI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.camera.location=(171,366,46);s.camera.rotation_euler=(Vector((126,414,6))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=65;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=16;s.render.filepath=str(R/'renders/qa/R262_erasmus_roofs.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R262_'))
glb=R/'exports/r152_clean/r262_erasmus_roofs_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R262_ERASMUS_ROOFS.json').write_text(json.dumps(dict(accepted=False,published=False,greenRoofs=records,lowerRoofs=lower,checks=checks,source='R214_erasmus_source_top.png; authored planar wings',limits=['Sedum material generated procedurally; patch locations not claimed measured','Coping thickness320mm and height270mm approximate','Remaining facades/courtyard links still incomplete']),indent=2));print('R262_CHECKS',len(records),len(checks),sum(c['boundary'] for c in checks),sum(c['zero'] for c in checks),flush=True)
