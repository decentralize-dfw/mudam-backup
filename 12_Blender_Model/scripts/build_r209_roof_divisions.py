from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R208_DOGRU_ARAZI_YUZEYLERI_v001.blend'))
rows=json.loads((R/'config/r209_roof_divisions.json').read_text());plane=json.loads((R/'config/r206_novotel_roof_planes.json').read_text())[1]
def floor(x,y):
 a,b,c=plane['plane'];ox,oy=plane['origin'];return a*(x-ox)+b*(y-oy)+c
made=[]
for row in rows:
 if row['support']<8 or row['top'] is None:continue
 a,b=Vector(row['a']),Vector(row['b']);u=(b-a).normalized();n=Vector((-u.y,u.x))*row['width']/2
 ring=[a+n,b+n,b-n,a-n];v=[(p.x,p.y,floor(p.x,p.y)) for p in ring]+[(p.x,p.y,max(row['top'],floor(p.x,p.y)+.15)) for p in ring]
 f=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
 me=bpy.data.meshes.new('R209_ROOF_DIVISION_%02d'%row['index']);me.from_pydata(v,[],f);me.materials.append(bpy.data.materials['R176_PALE_MINERAL']);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);o['source']='R190 roof orthographic reference independent trace';o['width_status']=row['width_status'];made.append(o.name)
s=bpy.context.scene;t=Vector((345,435,0));s.camera.location=t+Vector((0,0,200));s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=180;s.render.resolution_x=1600;s.render.resolution_y=1600;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R209_NOVOTEL_CATILAR_v001.blend'),compress=True)
(R/'reports/R209_ROOF_DIVISIONS.json').write_text(json.dumps(dict(accepted=False,objects=made,source='R190_roofs_source_top.png',method='Independent rectangular architectural members, scalar source height measurements; no source geometry or facade photo transfer',limitations=['Width approximate','Height samples include partial source support','Full roof equipment and facade acceptance pending']),indent=2))
s.render.filepath=str(R/'renders/qa/R209_roof_comparison_v001.png');bpy.ops.render.render(write_still=True)
