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
base=18.5;body=prism('R283_NORTH_HALL',extent,2.1,base,wall)
for i,d in enumerate(bays):
 p=d['polygon'];z=d['cornerRoofs'];prism(f'R283_MINERAL_ROOF_BAY_{i:02}',p,base-.05,z,bpy.data.materials['R262_MINERAL_LOWER_ROOF'])
 # Continuous glass strip fills the remaining interval to the following bay, with shared endpoints.
 nextp=bays[i+1]['polygon'] if i+1<len(bays) else [gaps[-1]['polygon'][3],gaps[-1]['polygon'][2]]
 glasspoly=[p[3],p[2],nextp[1],nextp[0]];g=gaps[i];origin=g['origin'];c=g['plane'];gz=[c[0]*(x-origin[0])+c[1]*(y-origin[1])+c[2] for x,y in glasspoly]
 prism(f'R283_GLAZED_ROOF_STRIP_{i:02}',glasspoly,base-.05,gz,glass)
 # Mineral end curbs close the seams without making an unsupported extra canopy.
 for j in [0,2]:
  a=Vector(glasspoly[j]);b=Vector(glasspoly[(j+1)%4]);n=(b-a).normalized();q=Vector((-n.y,n.x))*.035;pp=[tuple(a-q),tuple(b-q),tuple(b+q),tuple(a+q)];zz=[gz[j]+.04,gz[(j+1)%4]+.04,gz[(j+1)%4]+.04,gz[j]+.04];prism(f'R283_STRIP_FRAME_{i:02}_{j}',pp,[v-.08 for v in zz],zz,bpy.data.materials['R221_DARK_FRAMES'])
def inside(p):
 cs=[(extent[(i+1)%4][0]-a[0])*(p.y-a[1])-(extent[(i+1)%4][1]-a[1])*(p.x-a[0]) for i,a in enumerate(extent)];return min(cs)>=0 or max(cs)<=0
ob=bpy.data.objects['R166_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(ob.data);rm=[v for v in bm.verts if inside(ob.matrix_world@v.co)];count=len(rm);bmesh.ops.delete(bm,geom=rm,context='VERTS');bm.to_mesh(ob.data);bm.free()
path=R/'scenes/MUDAM_R283_DOGU_UZUN_CATI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.camera.location=(340,235,180);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=100;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R283_north_roof_authored.png');bpy.ops.render.render(write_still=True)
for ob in s.objects:ob.select_set(ob.name.startswith('R283_'))
glb=R/'exports/r152_clean/r283_roof_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R283_NORTH_ROOF.json').write_text(json.dumps(dict(accepted=False,published=False,removedReferenceVertices=count,checks=checks,bays=bays,gaps=gaps,limits=['Seven bays have p90 over0.25m and need source refinement before acceptance','Hidden hall base provisional','Whole low podium and adjoining facades still inherited and require independent reconstruction']),indent=2));print('R283_READY',checks,flush=True)
