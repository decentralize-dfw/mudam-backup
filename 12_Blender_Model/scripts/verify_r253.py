import bpy,bmesh,json
from pathlib import Path
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'exports/r152_clean/r253_oval_facades_REVIEW.glb'));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
p=R/'reports/R253_OVAL_FACADES.json';d=json.loads(p.read_text());d['checks']=checks;d['weldToleranceMeters']=.0001;p.write_text(json.dumps(d,indent=2));assert all(not c['boundary'] and not c['zero'] for c in checks);print(checks,flush=True)
