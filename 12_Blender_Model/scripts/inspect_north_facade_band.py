from pathlib import Path
import bpy,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'));from release_utils import verified_current_scene
r=verified_current_scene();bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));S=bpy.context.scene;S.render.resolution_x=1600;S.render.resolution_y=1100;S.render.resolution_percentage=100;cam=bpy.data.objects['P07_PHOTO_087_CONDITIONAL'];vs=[];fs=[];owners=[];names=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in S.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices);idx=len(names);names.append(ob.name)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(idx)
 eo.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,fs);f=cam.data.view_frame(scene=S);rows=[]
for x in [300,450,1100,1250,1400]:
 for y in range(635,766,10):
  u=x/1600;v=y/1100;d=f[3].lerp(f[0],u).lerp(f[2].lerp(f[1],u),v);d=cam.matrix_world.to_quaternion()@d.normalized();hit=tree.ray_cast(cam.location,d,500);rows.append(dict(pixel=[x,y],name=None if hit[0] is None else names[owners[hit[2]]],point=None if hit[0] is None else list(hit[0])))
(B/'reports/KUZEY_CEPHE_BANT_DIAGNOSTIC.json').write_text(json.dumps(dict(file=r['file'],samples=rows),indent=2));print(json.dumps(rows,indent=2))
