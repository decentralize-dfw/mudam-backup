from pathlib import Path
import bpy,bmesh,json
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');glb=R/'exports/r152_clean/r246_upper_facades_REVIEW.glb'
bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
print(checks)

