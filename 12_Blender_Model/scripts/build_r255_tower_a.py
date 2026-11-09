import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R254_OVAL_BUTUNLESIK_ADAY_v001.blend'))
def mat(n,c,r,m=0):
 a=bpy.data.materials.new(n);a.use_nodes=True;p=a.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=r;p.inputs['Metallic'].default_value=m;return a
metal=mat('R255_TOWER_SILVER',(.54,.61,.62),.32,.65);glass=mat('R255_TOWER_BLUE_GLASS',(.095,.24,.29),.23,.3);roof=mat('R255_TOWER_ROOF',(.22,.24,.24),.85);dark=mat('R255_SPANDREL',(.14,.23,.26),.5,.3)
V={};F={}
def box(name,a,b,z0,z1,depth,ma):
 a=Vector(a);b=Vector(b);n=Vector((-(b-a).y,(b-a).x)).normalized()*depth/2;p=[a-n,b-n,b+n,a+n];vs=[(q.x,q.y,z) for z in [z0,z1] for q in p];k=len(V.setdefault(name,[]));V[name]+=vs;F.setdefault(name,[]).extend(tuple(k+j for j in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);M[name]=ma
M={};ring=[Vector(p) for p in [(224,309.4),(245.8,314.2),(237,353.4),(215.8,349.8)]]
# Straight architectural corners fitted to source footprint, not copied scan triangles.
pixels=[1128,1090,1052,1014,976,938,900,862,824,786,748,710,672,634,596,558,520,482,444,406]
levels=[7+(1188.152945-y)/11.007373 for y in pixels];bottom=6.1;top=79.15
# Observed ~15 panes on short facade, ~21 on long face; rear cadence provisional.
for edge,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
 u=(b-a).normalized();normal=Vector((u.y,-u.x));length=(b-a).length;n=[15,21,15,21][edge]
 box('R255_A_BASE',a,b,bottom,levels[0]-.2,.30,dark)
 for z in levels:box('R255_A_FLOOR_BANDS',a,b,z-.13,z+.13,.30,metal)
 limits=levels+[top]
 for lo,hi in zip(limits,limits[1:]):
  if hi-lo<.4:continue
  for j in range(n):
   p=a.lerp(b,j/n)+u*.045-normal*.10;q=a.lerp(b,(j+1)/n)-u*.045-normal*.10
   box('R255_A_RECESSED_GLAZING',p,q,lo+.13,hi-.13,.065,glass)
 for j in range(n+1):
  p=a.lerp(b,j/n);box('R255_A_VERTICAL_MULLIONS',p-u*.045,p+u*.045,levels[0]-.13,top,.26,metal)
 box('R255_A_PARAPET',a,b,top-.15,top+.28,.30,metal)
# Closed flat roof/floor slabs.
def slab(name,z0,z1):
 k=0;V[name]=[(p.x,p.y,z) for z in [z0,z1] for p in ring];F[name]=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];M[name]=roof
slab('R255_A_ROOF',top-.22,top);slab('R255_A_FLOOR',bottom,bottom+.25)
for name,v in V.items():
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],F[name]);me.materials.append(M[name]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
o=bpy.data.objects['R165_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data);remove=[v for v in bm.verts if (o.matrix_world@v.co).y<370];removed=len(remove);bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(o.data);bm.free()
p=R/'scenes/MUDAM_R255_KUZEY_KULE_A_MIMARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.camera.location=(390,180,65);s.camera.rotation_euler=(Vector((240,370,48))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=145;s.render.resolution_x=1600;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R255_tower_a_authored.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R255_'))
glb=R/'exports/r152_clean/r255_tower_a_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert checks and all(not c['boundary'] and not c['zero'] for c in checks)
(R/'reports/R255_TOWER_A.json').write_text(json.dumps(dict(accepted=False,published=False,removedReferenceVertices=removed,levels=levels,source='R255_towers_source.png; planar source footprint and visible facade lines',checks=checks,limits=['Rear facade cadence needs independent source elevation','Roof equipment not yet reconstructed','Base terrain contact not verified','Materials visual approximation; no scan texture','No region completion claim']),indent=2));print('R255_READY',flush=True)
