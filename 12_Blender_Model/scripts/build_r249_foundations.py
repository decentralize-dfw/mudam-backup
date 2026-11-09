import bpy,bmesh,json,re,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R247_ERASMUS_AVLU_SALON_ADAY_v001.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R182_EXTENSION_GROUND','R154_FAR_ROADS','R182_EXTENSION_ROADS'] or o.name.startswith('R210_GROUND_CONTINUITY_')):continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);records=[];changed=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not re.fullmatch(r'R(?:171|174|182_DISTRICT)_\d+',o.name):continue
 world=[o.matrix_world@v.co for v in o.data.vertices];base=min(v.z for v in world);idx=[i for i,v in enumerate(world) if abs(v.z-base)<.001];samples=[];misses=0
 for e in o.data.edges:
  i,j=e.vertices
  if i not in idx or j not in idx:continue
  a,b=world[i],world[j];n=max(2,math.ceil((b-a).length/.5))
  for k in range(n+1):
   p=a.lerp(b,k/n);h,*_=g.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),500)
   if h:samples.append(h.z)
   else:misses+=1
 low=min(samples) if samples else None;extension=max(0,base-low+.12) if low is not None else 0
 if extension>.001 and misses==0:
  inv=o.matrix_world.inverted()
  for i in idx:
   p=world[i].copy();p.z=low-.12;o.data.vertices[i].co=inv@p
  changed.append(o.name)
 records.append(dict(name=o.name,samples=len(samples),misses=misses,originalBase=base,minGround=low,extension=extension if misses==0 else 0))
(R/'reports/R249_DISTRICT_FOUNDATIONS.json').write_text(json.dumps(dict(accepted=False,changed=changed,records=records,method='Half-metre perimeter sampling against authored terrain; only lower foundation vertices extended, roof and XY untouched. Missing ground samples prevent mutation.'),indent=2));print('CHANGED',len(changed),[(r['name'],r['extension']) for r in records if r['extension']>.001],flush=True)
if changed:
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R249_ALT_MAHALLE_TEMEL_ADAY_v001.blend'),compress=True)
 for o in bpy.context.scene.objects:o.select_set(o.name in changed)
 bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r249_foundations_REVIEW.glb'),export_format='GLB',use_selection=True)
