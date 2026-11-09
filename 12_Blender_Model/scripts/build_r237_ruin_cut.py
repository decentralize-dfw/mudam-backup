from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R236_KALE_AVLU_YOL_OTURUM_ADAY_v001.blend'))
xy=json.loads((R/'reports/R198_RUIN_MEASUREMENTS.json').read_text())['xy']
if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))<0:xy.reverse()
records=[]
def split(poly,a,b):
 ins=[];out=[]
 def dt(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=dt(p),dt(q);(ins if dp>=0 else out).append(p)
  if dp*dq<0:
   t=dp/(dp-dq);v=[u+(w-u)*t for u,w in zip(p,q)];ins.append(v);out.append(v)
 return ins,out
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or not (o.name.startswith('R193_SOUTHWEST_COURT') ):continue
 old=o.data;old.calc_loop_triangles();before=sum(p.area for p in old.polygons);uv=old.uv_layers.active;vs=[];fs=[];tex=[]
 for tri in old.loop_triangles:
  poly=[]
  for vi,li in zip(tri.vertices,tri.loops):v=old.vertices[vi].co;poly.append([*v,*(uv.data[li].uv if uv else (0,0))])
  parts=[];remain=poly
  for a,b in zip(xy,xy[1:]+xy[:1]):
   if len(remain)<3:break
   remain,out=split(remain,a,b)
   if len(out)>=3:parts.append(out)
  for p in parts:
   k=len(vs);vs.extend(v[:3] for v in p);tex.extend(v[3:] for v in p);fs.extend((k,k+j,k+j+1) for j in range(1,len(p)-1))
 me=bpy.data.meshes.new(o.name+'_RUIN_CUT');me.from_pydata(vs,[],fs);me.update()
 for m in old.materials:me.materials.append(m)
 u=me.uv_layers.new()
 for l in me.loops:u.data[l.index].uv=tex[l.vertex_index]
 o.data=me
 records.append(dict(name=o.name,beforeArea=before,afterArea=sum(p.area for p in me.polygons)))

removed=sum(x['beforeArea']-x['afterArea'] for x in records)
assert removed>1,removed
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('R193_SOUTHWEST_COURT'):
  bm=bmesh.new();bm.from_mesh(o.data);bad=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(o.data);bm.free()
p=R/'scenes/MUDAM_R237_KALE_KALINTI_AVLU_KESIM_ADAY_v001.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(p))
s=bpy.context.scene;t=Vector((-229.6,-192.1,-18));s.camera.location=t+Vector((30,-45,38));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=48;s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R237_ruin_court.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith(('R193_SOUTHWEST_COURT','R198_RUIN','R199_RUIN')))
g=R/'exports/r152_clean/r237_ruin_court_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(g),export_format='GLB',use_selection=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(g))
checks=[dict(name=o.name,finite=all(math.isfinite(x) for v in o.data.vertices for x in v.co),zero=sum(p.area<1e-10 for p in o.data.polygons)) for o in bpy.context.scene.objects if o.type=='MESH']
assert all(c['finite'] and not c['zero'] for c in checks)
(R/'reports/R237_RUIN_COURT_CUT.json').write_text(json.dumps(dict(accepted=False,published=False,removedArea=removed,changes=records,reopen=checks,reason='Restore source-traced archaeological ruin exclusion lost when R235 reconstructed full court triangles',limits=['Retaining and grade continuity require further source comparison','No overall fort acceptance']),indent=2))
print('R237_READY',removed)
