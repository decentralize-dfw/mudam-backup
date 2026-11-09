from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R271_ERASMUS_IKI_ENINE_BAGLANTI_ADAY_v001.blend'))
parts=json.loads((R/'config/r233_courtyard_roof_planes.json').read_text())['parts'];poly=parts[2]['polygon'];light=parts[0]
mat=bpy.data.materials.new('R273_ROOF_MEMBRANE');mat.diffuse_color=(.13,.15,.14,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Roughness'].default_value=.83
glass=bpy.data.materials['R221_BLUE_GREY_GLASS'];wall=bpy.data.materials['R227_UNRESOLVED_FACADE']
def prism(name,p,bot,top,material):
 n=len(p);vs=[(x,y,z[i] if isinstance(z,list) else z) for z in [bot,top] for i,(x,y) in enumerate(p)];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(material);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def boolean(o,c):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Architectural opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
# Independent architectural solids, measured rooflight planes; hidden base remains provisional.
measure=json.loads((R/'config/r273_right_court_planes.json').read_text());shift=(.7562829027*48.4,.6542447333*48.4);poly=[(155.65,453.216667),(163.233333,460.55),(172.733333,449.55),(165.233333,443.05)]
body=prism('R273_COURT_HALL',poly,.5,5.85,wall)
cx=sum(x for x,y in poly)/4;cy=sum(y for x,y in poly)/4
inner=[(cx+(x-cx)*.94,cy+(y-cy)*.94) for x,y in poly];boolean(body,prism('Interior cavity',inner,.85,5.55,wall));roof=prism('R273_COURT_ROOF',poly,5.85,5.9,mat)
for j,light in enumerate(measure[:2]):
 assert light['samples']>500 and light['support']>.95 and light['p90']<.15
 p=light['polygon'];z=light['cornerRoofs']
 for o in [body,roof]:boolean(o,prism('Lightwell',p,5.5,8,mat))
 prism(f'R273_GLAZING_{j}',p,[v-.07 for v in z],z,glass)
 center=Vector((sum(x for x,y in p)/4,sum(y for x,y in p)/4))
 for i in range(4):
  a=Vector(p[i]);b=Vector(p[(i+1)%4]);n=(center-(a+b)/2).normalized()*.09;pp=[tuple(a),tuple(b),tuple(b+n),tuple(a+n)];zz=[z[i]-.07,z[(i+1)%4]-.07,z[(i+1)%4]-.07,z[i]-.07];prism(f'R273_UPSTAND_{j}_{i}',pp,5.8,zz,wall)
 # Eight glazing modules, independent narrow frame solids along the measured incline.
 for k in range(9):
  t=k/8;a=Vector(p[0]).lerp(Vector(p[1]),t);b=Vector(p[3]).lerp(Vector(p[2]),t);d=(Vector(p[1])-Vector(p[0])).normalized()*.025;za=z[0]*(1-t)+z[1]*t;zb=z[3]*(1-t)+z[2]*t;prism(f'R273_FRAME_{j}_{k}',[tuple(a-d),tuple(a+d),tuple(b+d),tuple(b-d)],[za+.01,za+.01,zb+.01,zb+.01],[za+.06,za+.06,zb+.06,zb+.06],bpy.data.materials['R221_DARK_FRAMES'])
out=R/'scenes/MUDAM_R273_ERASMUS_SAG_AVLU_ADAY_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));s=bpy.context.scene;c=s.camera;c.location=(177.6,434.66,20);c.rotation_euler=(Vector((161.1,455.66,5.5))-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=27;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R273_courtyard.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R273_'))
glb=R/'exports/r152_clean/r247_court_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R273_COURTYARD_HALL.json').write_text(json.dumps(dict(accepted=False,published=False,checks=checks,source='R272 direct top traces and R273 independent scalar plane fits',limits=['Source comparison pending; both lights independently fitted','Hidden interior cavity and foundation depth provisional','Surround roof 5.85 inferred from rear strip; complete perimeter needs independent check']),indent=2));print('R273_READY',checks,flush=True)
