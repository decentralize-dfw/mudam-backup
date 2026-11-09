from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_CATIPENCERE_v089.blend'))
report=json.loads((R/'reports/R169_REAR_DORMERS_v089.json').read_text())
center=Vector((-81.746925354,-294.516082764,-69));right=Vector((-.97769629955,-.2100233883,0));normal=Vector((-.2100236565,.97769629955,0))
def pt(x,y,d):
 p=center+right*((x-1024)*36/2048)+normal*d;p.z=-69+(395.636-y)*36/2048;return p
base=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('ARCH_REAR_DORMER_')]
changes=[]
for rec in report['records']:
 if 'roofReturnDepth' not in rec:continue
 l,t,r,b=rec['sourceRectangle'];l-=5;r+=5;t-=6;b+=6;off=rec['measuredFrontOffset'];depth=rec['roofReturnDepth'];i=rec['index']
 verts=[pt(x,y,d) for d in [off+2,off-depth+.015] for x,y in [(l,t),(r,t),(r,b),(l,b)]]
 me=bpy.data.meshes.new('CUT');me.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();c=bpy.data.objects.new('CUT',me);bpy.context.collection.objects.link(c)
 lo=[min(v[k] for v in verts) for k in range(3)];hi=[max(v[k] for v in verts) for k in range(3)]
 for obj in base:
  points=[obj.matrix_world@v.co for v in obj.data.vertices]
  if not points or any(max(p[k] for p in points)<lo[k] or min(p[k] for p in points)>hi[k] for k in range(3)):continue
  before=len(obj.data.polygons);bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Actual dormer opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);changes.append([i,obj.name,before,len(obj.data.polygons)])
 bpy.data.objects.remove(c,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_CATIPENCERE_v090.blend'))
report['apertureChanges']=changes;report['accepted']=False;(R/'reports/R169_REAR_DORMERS_v090.json').write_text(json.dumps(report,indent=2))
s=bpy.context.scene;s.cycles.samples=16;target=Vector((-80,-301,-66));s.camera.location=target+Vector((-20,31,22));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/qa/R169_rear_dormers_v090.png');bpy.ops.render.render(write_still=True)
print('APERTURES',changes)
