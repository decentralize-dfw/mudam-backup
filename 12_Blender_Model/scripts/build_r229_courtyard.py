from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R228_ERASMUS_CAM_BAGLANTI_ADAY_v001.blend'))
def solid(name,pts,z0,z1):
 vs=[(p[0],p[1],z)for z in [z0,z1]for p in pts];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();x=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(x);return x

def subtract(cutter):
 bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('R229_OPENING','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
glass=bpy.data.materials.new('R229_BLUE_GREY_GLASS');glass.diffuse_color=(.12,.24,.26,1);metal=bpy.data.materials.new('R229_DARK_FRAMES');metal.diffuse_color=(.15,.17,.16,1)
def box(name,x0,x1,y0,y1,z0,z1,mat=None):
 pts=[a+u*x+n*y for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];x=solid(name,pts,z0,z1)
 if mat:x.data.materials.append(mat)
 return x

records=[]
for idx in [0,1]:
 d=json.loads((R/f'config/r229_court{idx}_openings.json').read_text());o=bpy.data.objects[f'R226_ERASMUS_REAR_{idx}'];a=Vector(d['origin']);u=Vector(d['u']);n=Vector(d['normal']);poly=json.loads((R/'config/r226_rear_planes.json').read_text())['parts'][idx]['polygon'];c=sum((Vector(p)for p in poly),Vector((0,0)))/4
 inner=[c+(Vector(p)-c)*.90 for p in poly];subtract(solid('CUT',inner,5.3,10.95))
 for i,w in enumerate(d['openings']):
  x0,x1,z0,z1=[w[k]for k in ['u0','u1','z0','z1']];assert .15<x0<x1<d['wallLength']-.15 and 5.3<z0<z1<10.95
  subtract(box('CUT',x0,x1,-1,.3,z0,z1));prefix=f'R229_COURT_{idx}_{i}';box(prefix+'_GLASS',x0+.045,x1-.045,-.21,-.19,z0+.045,z1-.045,glass)
  for label,xx0,xx1,zz0,zz1 in [('L',x0,x0+.045,z0,z1),('R',x1-.045,x1,z0,z1),('B',x0,x1,z0,z0+.045),('T',x0,x1,z1-.045,z1)]:box(prefix+label,xx0,xx1,-.24,-.14,zz0,zz1,metal)
 records.append(dict(object=o.name,sourceObservedOpenings=4))
path=R/'scenes/MUDAM_R229_ERASMUS_AVLU_CEPHE_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for ob in bpy.context.scene.objects:ob.select_set(ob.name.startswith('R229_')or ob.name in ['R226_ERASMUS_REAR_0','R226_ERASMUS_REAR_1'])
glb=R/'exports/r152_clean/r229_courtyard_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(not x['boundary'] and not x['zero']for x in checks)
(R/'reports/R229_COURTYARD.json').write_text(json.dumps(dict(accepted=False,published=False,records=records,reopen=checks,limits=['Source-visible bounds approximate, no hidden apertures invented','Frame width .045 and cavity depth provisional','Remaining courtyard floors, windows, connecting structures and roof details incomplete']),indent=2));print('R229_READY',len(checks))
