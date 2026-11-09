from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R284_DOGU_UZUN_CATI_ADAY_v001.blend'))
parts=json.loads((R/'config/r233_courtyard_roof_planes.json').read_text())['parts'];poly=parts[2]['polygon'];light=parts[0]
mat=bpy.data.materials.new('R247_ROOF_MEMBRANE');mat.diffuse_color=(.13,.15,.14,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Roughness'].default_value=.83
glass=bpy.data.materials['R221_BLUE_GREY_GLASS'];wall=bpy.data.materials['R227_UNRESOLVED_FACADE']
def prism(name,p,bot,top,material):
 n=len(p);vs=[(x,y,z[i] if isinstance(z,list) else z) for z in [bot,top] for i,(x,y) in enumerate(p)];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(material);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def boolean(o,c):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Architectural opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)


for ob in list(bpy.context.scene.objects):
 if ob.name.startswith('R284_'):bpy.data.objects.remove(ob,do_unlink=True)
d=json.loads((R/'config/r286_architectural_roof_modules.json').read_text());a=Vector((290+688/12,285-273/12));end=Vector((290+215/12,285-1020/12));axis=(end-a).normalized();width=Vector((212/12,-124/12));point=lambda x,t:tuple(a+axis*x+width*t);nodes=[(0,20.38,'start')]
for i,m in enumerate(d['modules']):
 nodes.extend([(m['start'],m['startZ'],f'bay{i}_start'),(m['crest'],m['crestZ'],f'bay{i}_crest'),(m['end'],m['endZ'],f'bay{i}_end')])
nodes.extend([(26.3,19.0,'middle_start'),(36.1,19.0,'middle_end'),(d['length'],20.2,'end')]);nodes.sort();clean=[]
for n in nodes:
 if clean and n[0]-clean[-1][0]<.10:
  if n[2].startswith('middle'):clean[-1]=n
  continue
 clean.append(n)
nodes=clean;mineral=bpy.data.materials['R284_MINERAL_GRAVEL'];extent=[point(0,0),point(0,1),point(d['length'],1),point(d['length'],0)];prism('R286_NORTH_HALL',extent,2.1,18.45,wall);pieces=[]
for i,(p,q) in enumerate(zip(nodes,nodes[1:])):
 x,z,tag=p;y,zz,nexttag=q;poly=[point(x,0),point(x,1),point(y,1),point(y,0)];heights=[z,z,zz,zz];is_glass=tag.endswith('_crest');prism(f'R286_ROOF_PLANE_{i:02}',poly,18.4,heights,glass if is_glass else mineral);pieces.append(dict(start=x,end=y,heights=[z,zz],material='glass' if is_glass else 'mineral'))
 if tag.endswith('_crest'):
  pp=[point(x-.035,0),point(x-.035,1),point(x+.035,1),point(x+.035,0)];prism(f'R286_CREST_FRAME_{i:02}',pp,z+.01,z+.08,bpy.data.materials['R221_DARK_FRAMES'])
path=R/'scenes/MUDAM_R286_DOGU_BUTUN_CATI_KESIT_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.camera.location=(340,235,180);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=100;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R286_north_roof_authored.png');bpy.ops.render.render(write_still=True)
for ob in s.objects:ob.select_set(ob.name.startswith('R286_'))
glb=R/'exports/r152_clean/r286_roof_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R286_WHOLE_ROOF.json').write_text(json.dumps(dict(accepted=False,published=False,architecturalModules=d,profileNodes=nodes,pieces=pieces,checks=checks,limits=['Independent held-out source evaluation pending','Source material boundary interpretation and end details require visual comparison','Low podium facade remains inherited']),indent=2));print('R286_READY',flush=True)
