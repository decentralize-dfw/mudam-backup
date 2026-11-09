from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R220_ERASMUS_ARKA_BAGLANTI_ADAY_v001.blend'));d=json.loads((R/'config/r221_front_openings_projected.json').read_text());o=bpy.data.objects['R216_ERASMUS_WING_0'];a=Vector(d['origin']);u=Vector(d['u']);n=Vector(d['normal']);poly=json.loads((R/'config/r215_erasmus_roof_traces.json').read_text())['parts'][0]['polygon'];c=sum((Vector(p)for p in poly),Vector((0,0)))/4

def solid(name,pts,z0,z1):
 vs=[(p[0],p[1],z)for z in [z0,z1]for p in pts];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();x=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(x);return x

def subtract(cutter):
 bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('R221_OPENING','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
inner=[c+(Vector(p)-c)*.94 for p in poly];subtract(solid('R221_INTERIOR_CUTTER',inner,5.5,11.19))
glass=bpy.data.materials.new('R221_BLUE_GREY_GLASS');glass.diffuse_color=(.12,.24,.26,1);metal=bpy.data.materials.new('R221_DARK_FRAMES');metal.diffuse_color=(.15,.17,.16,1)
def box(name,x0,x1,y0,y1,z0,z1,mat=None):
 pts=[a+u*x+n*y for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];x=solid(name,pts,z0,z1)
 if mat:x.data.materials.append(mat)
 return x
made=[];rejected=[]
for i,w in enumerate(d['openings']):
 if w['u0']<.15 or w['u1']>d['wallLength']-.15:rejected.append(dict(id=i,reason='Projected aperture crosses current footprint edge; footprint correction needed, not clipped'));continue
 x0,x1,z0,z1=[w[k]for k in ['u0','u1','z0','z1']];subtract(box('R221_WINDOW_CUTTER',x0,x1,-1,.3,z0,z1));box('R221_GLASS_'+str(i),x0+.04,x1-.04,-.21,-.19,z0+.04,z1-.04,glass)
 for label,xx0,xx1,zz0,zz1 in [('L',x0,x0+.045,z0,z1),('R',x1-.045,x1,z0,z1),('B',x0,x1,z0,z0+.045),('T',x0,x1,z1-.045,z1),('M',(x0+x1)/2-.0225,(x0+x1)/2+.0225,z0,z1)]:box('R221_FRAME_'+str(i)+label,xx0,xx1,-.24,-.14,zz0,zz1,metal)
 made.append(i)
bm=bmesh.new();bm.from_mesh(o.data);assert not any(e.is_boundary for e in bm.edges);bm.free()
path=R/'scenes/MUDAM_R221_ERASMUS_GERCEK_ACIKLIK_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for x in bpy.context.scene.objects:x.select_set(x.name=='R216_ERASMUS_WING_0' or x.name.startswith('R221_'))
glb=R/'exports/r152_clean/r221_facade_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for x in bpy.context.scene.objects:
 if x.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(x.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001);checks.append(dict(name=x.name,boundary=sum(e.is_boundary for e in bm.edges)));bm.free()
(R/'reports/R221_OPENINGS.json').write_text(json.dumps(dict(accepted=False,published=False,observedOpeningsBuilt=made,rejected=rejected,reopen=checks,limits=['Four actual observed upper apertures only; first reveals footprint mismatch','Inner wall thickness and frame .045m dimensions provisional','Remaining facades and connecting architecture incomplete']),indent=2));print('R221',made,rejected,flush=True)
