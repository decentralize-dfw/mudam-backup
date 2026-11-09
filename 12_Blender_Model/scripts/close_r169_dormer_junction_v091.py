from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_v088.blend'))
vs=[];faces=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();offset=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend([offset+j for j in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,faces,all_triangles=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_CATIPENCERE_v090.blend'))
center=Vector((-81.746925354,-294.516082764,-69));right=Vector((-.97769629955,-.2100233883,0));normal=Vector((-.2100236565,.97769629955,0))
def pt(x,y,d):
 p=center+right*((x-1024)*36/2048)+normal*d;p.z=-69+(395.636-y)*36/2048;return p
report=json.loads((R/'reports/R169_REAR_DORMERS_v090.json').read_text());miss=[]
for rec in report['records']:
 if 'roofReturnDepth' not in rec:continue
 l,t,r,b=rec['sourceRectangle'];l-=5;r+=5;t-=6;b+=6;off=rec['measuredFrontOffset'];vv=[];ff=[]
 for a,c,e,f in [(l,t,r,t),(r,t,r,b),(r,b,l,b),(l,b,l,t)]:
  prev=None
  for step in range(81):
   u=step/80;x=a+(e-a)*u;y=c+(f-c)*u;p=pt(x,y,off);hit,no,idx,dist=tree.ray_cast(p+normal*2,-normal,5)
   if hit is None:miss.append([rec['index'],x,y]);prev=None;continue
   # Collar joins the exact original authored envelope intersection to dormer face.
   k=len(vv);vv.extend([p,hit])
   if prev is not None:ff.append((prev,prev+1,k+1,k))
   prev=k
 me=bpy.data.meshes.new('Dormer junction');me.from_pydata(vv,[],ff);me.update();ob=bpy.data.objects.new(f"ARCH_REAR_DORMER_{rec['index']}_ROOF_JUNCTION",me);bpy.context.collection.objects.link(ob);me.materials.append(bpy.data.materials['Authored slate - neutral unlit source color not copied'])
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_CATIPENCERE_v091.blend'));print('MISSING_JUNCTION',len(miss))
