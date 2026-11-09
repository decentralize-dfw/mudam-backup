from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R246_ERASMUS_UST_CEPHE_ADAY_v001.blend'))
parts=json.loads((R/'config/r233_courtyard_roof_planes.json').read_text())['parts'];poly=parts[2]['polygon'];light=parts[0]
mat=bpy.data.materials.new('R247_ROOF_MEMBRANE');mat.diffuse_color=(.13,.15,.14,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Roughness'].default_value=.83
glass=bpy.data.materials['R221_BLUE_GREY_GLASS'];wall=bpy.data.materials['R227_UNRESOLVED_FACADE']
def prism(name,p,bot,top,material):
 n=len(p);vs=[(x,y,z[i] if isinstance(z,list) else z) for z in [bot,top] for i,(x,y) in enumerate(p)];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(material);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def boolean(o,c):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Architectural opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
# Source traces establish external extent; concealed lower extent is a provisional closed foundation.
body=prism('R247_COURT_HALL',poly,.5,7.18,wall)
cx=sum(x for x,y in poly)/4;cy=sum(y for x,y in poly)/4
inner=[(cx+(x-cx)*.94,cy+(y-cy)*.94) for x,y in poly]
boolean(body,prism('Interior cavity',inner,.85,6.05,wall))
roof=prism('R247_COURT_ROOF',poly,7.18,7.23,mat)
for o in [body,roof]:boolean(o,prism('Lightwell',light['polygon'],6.18,8.0,mat))
z=light['cornerRoofs'];prism('R247_SOURCE_SLOPED_GLAZING',light['polygon'],[v-.07 for v in z],z,glass)
# Solid upstands close the recess down to glazing without covering its sloping surface.
for i in range(4):
 a=Vector(light['polygon'][i]);b=Vector(light['polygon'][(i+1)%4]);d=b-a;n=Vector((-d.y,d.x)).normalized()*.09
 p=[tuple(a),tuple(b),tuple(b+n),tuple(a+n)];zz=[z[i]-.07,z[(i+1)%4]-.07,z[(i+1)%4]-.07,z[i]-.07]
 prism('R247_LIGHTWELL_UPSTAND_'+str(i),p,zz,7.24,wall)
out=R/'scenes/MUDAM_R247_ERASMUS_AVLU_SALON_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));s=bpy.context.scene;c=s.camera;c.location=(141,403,20);c.rotation_euler=(Vector((124.5,424,5.5))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=27;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R247_courtyard.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R247_'))
glb=R/'exports/r152_clean/r247_court_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R247_COURTYARD_HALL.json').write_text(json.dumps(dict(accepted=False,published=False,checks=checks,source='R214 top trace; R233 supported first light plane; R247 edge measurements',limits=['Second light and crosslink support unresolved','Hidden interior cavity and foundation depth provisional','Roof 7.18 supported by central transverse edge measurements; whole roof not surveyed']),indent=2));print('R247_READY',checks,flush=True)
