import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R398_KALE_CATI_VE_PAVYON_BAGLANTI_ADAY_v001.blend'));d=json.loads((R/'reports/R387_ROOF_INPUT.json').read_text());joints=json.loads((R/'reports/R400_DECK_JOINTS_INPUT.json').read_text());names=[]
def mat(name,color,rough,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
wood=mat('R400_WEATHERED_TIMBER_DECK',(.29,.265,.23),.87);dark=mat('R400_DARK_LOUVER_FRAMES',(.035,.044,.047),.5,.6);metal=mat('R400_ZINC_SLOPING_FASCIA',(.24,.27,.29),.58,.65);glass=mat('R400_CLERESTORY_GLAZING',(.085,.135,.145),.2);gp=glass.node_tree.nodes.get('Principled BSDF');gp.inputs['Transmission Weight'].default_value=.45;gp.inputs['IOR'].default_value=1.45
tex=wood.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures/R32_wood_candidate_normal.png'),check_existing=True);tex.image.colorspace_settings.name='Non-Color';nm=wood.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.18;wood.node_tree.links.new(tex.outputs['Color'],nm.inputs['Color']);wood.node_tree.links.new(nm.outputs['Normal'],wood.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
for name in ['R389_FORT_INNER_PARAPET','R389_FORT_INNER_COPING','R398_FORT_STANDING_SEAMS']:
 o=bpy.data.objects[name];o.hide_render=True;o.hide_viewport=True;o.hide_set(True);o['R400_rejected']='Rooftop photo and INPA document show timber deck and glazed/louvered perimeter, not the earlier stone parapet/standing-seam assumption.'
for name in ['R389_FORT_LOWER_METAL_ROOF','R389_FORT_RAISED_METAL_ROOF','R389_FORT_PERIMETER_LEDGE']:
 o=bpy.data.objects[name];o.data.materials.clear();o.data.materials.append(wood);o['R400_surface']='Timber roof terrace, confirmed in Zinneke rooftop view 2. Legacy object name retained for traceability.'
 for l in o.data.loops:
  v=o.data.vertices[l.vertex_index].co;o.data.uv_layers.active.data[l.index].uv=((v.x-v.y)/4.24264,(v.x+v.y)/1.64049)
def mesh(name,vs,fs,material):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(material);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob['level_id']='SITE';ob['source']='Independent architecture. INPA construction description plus Zinneke 2012 rooftop view 2, CC-BY-SA3, visual reference only; classified levels R386.';names.append(name);return ob
def box(vs,fs,a,b,width,height):
 a=Vector(a);b=Vector(b);t=(b-a).normalized();side=Vector((-t.y,t.x,0)).normalized()*width/2;z=Vector((0,0,height/2));i=len(vs);vs.extend([tuple(p) for p in [a-side-z,b-side-z,b+side-z,a+side-z,a-side+z,b-side+z,b+side+z,a+side+z]]);fs.extend([[i+j for j in f] for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
v=[];f=[]
for row in joints['seams']:
 c=row['plane'];a,b=row['a'],row['b'];box(v,f,(*a,c[0]*a[0]+c[1]*a[1]+c[2]+.001),(*b,c[0]*b[0]+c[1]*b[1]+c[2]+.001),.003,.002)
mesh('R400_TIMBER_DECK_JOINTS',v,f,dark)
line=d['crestOutline'];area=sum(line[i][0]*line[(i+1)%len(line)][1]-line[(i+1)%len(line)][0]*line[i][1] for i in range(len(line)));normals=[]
for i,pt in enumerate(line):
 tangent=(Vector(line[(i+1)%len(line)])-Vector(line[i-1])).normalized();normal=Vector((tangent.y,-tangent.x));normals.append(normal if area>0 else -normal)
# Swept multi-point metal fascia: high vegetated roof meets low glazed band.
profile=[(-.13,2.87),(-.10,2.94),(.24,3.49),(.24,3.55),(.20,3.55),(-.15,2.96)];v=[];f=[];k=len(profile);n=len(line)
for p,no in zip(line,normals):
 for offset,z in profile:q=Vector(p)+no*offset;v.append((q.x,q.y,z))
for i in range(n):
 for j in range(k):f.append((i*k+j,((i+1)%n)*k+j,((i+1)%n)*k+(j+1)%k,i*k+(j+1)%k))
mesh('R400_SLOPED_PERIMETER_FASCIA',v,f,metal)
gv=[];gf=[];fv=[];ff=[];lv=[];lf=[]
for i,(p,no) in enumerate(zip(line,normals)):
 a=Vector((*p,0))-Vector((*no,0))*.12;b=Vector((*line[(i+1)%n],0))-Vector((*normals[(i+1)%n],0))*.12;length=(b-a).length;div=max(1,round(length/1.2));t=(b-a).normalized();out=Vector((t.y,-t.x,0))*(1 if area>0 else -1)
 box(gv,gf,a+Vector((0,0,2.565)),b+Vector((0,0,2.565)),.012,.63)
 for z in [2.235,2.895]:box(fv,ff,a+Vector((0,0,z)),b+Vector((0,0,z)),.065,.045)
 for j in range(div+1):
  p=a+(b-a)*(j/div);q=p+t*.04;box(fv,ff,p+Vector((0,0,2.565)),q+Vector((0,0,2.565)),.065,.63)
 for j in range(7):
  z=2.27+j*.09;box(lv,lf,a-out*.055+Vector((0,0,z)),b-out*.055+Vector((0,0,z)),.065,.025)
mesh('R400_PERIMETER_CLERESTORY_GLASS',gv,gf,glass);mesh('R400_PERIMETER_WINDOW_FRAMES',fv,ff,dark);mesh('R400_PERIMETER_HORIZONTAL_LOUVERS',lv,lf,dark)
out=R/'scenes/MUDAM_R400_KALE_CAM_BANT_AHSAP_TERAS_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(c['nonManifold'] or c['zeroArea'] for c in checks),checks
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and not ob.hide_render and (ob.name.startswith(('R389_','R392_','R397_','R400_')) or ob.name in ['R154_FORT_MASONRY_BODY','R154_FORT_ROUNDED_EARTH_ROOF']):ob.select_set(True)
glb=R/'exports/r152_clean/r400_fort_pavilion_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False)
report=dict(scene=out.name,accepted=False,published=False,meshChecks=checks,sourceDocument='https://inpa.public.lu/fr/patrimoine/feodal_fortifie/forteresse_luxembourg/musee_forteresse/partie_authentique_reconstruite.html',sourcePhoto='references/fort_inpa/rooftop_view_2_Zinneke_CC_BY_SA_3.jpg',correction='Prior metal-deck/stone-parapet interpretation rejected; timber terrace, continuous glazing, horizontal louvers and sloping metal fascia independently modeled.',limits=['Board, frame and louver spacing are visual estimates, not survey dimensions.','Tower-end court and shoulder junction remain incomplete. Whole green-marked perimeter not accepted.']);(R/'reports/R400_FORT_ROOF.json').write_text(json.dumps(report,indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-42,-34,100));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-42,-34,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=65;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R400_fort_roof_candidate.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));errors=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':
  bad=sum(not all(math.isfinite(x) for x in v.co) for v in ob.data.vertices);zero=sum(p.area<1e-10 for p in ob.data.polygons)
  if bad or zero:errors.append(dict(name=ob.name,nonFinite=bad,zeroArea=zero))
report['glbErrors']=errors;(R/'reports/R400_FORT_ROOF.json').write_text(json.dumps(report,indent=2));assert not errors;print('R400_READY')
