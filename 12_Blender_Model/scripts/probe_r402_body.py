import bpy,bmesh,json
from pathlib import Path
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');rows=[]
for rev,name in [('R401','MUDAM_R401_KALE_ACIK_TERAS_UCU_ADAY_v001.blend'),('R402','MUDAM_R402_KALE_ALCAK_KULE_AVLUSU_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/name));o=bpy.data.objects['R154_FORT_MASONRY_BODY'];bm=bmesh.new();bm.from_mesh(o.data);row=dict(rev=rev,before=sum(not e.is_manifold for e in bm.edges));bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);row['welded']=sum(not e.is_manifold for e in bm.edges);row['boundary']=sum(e.is_boundary for e in bm.edges);rows.append(row);bm.free()
(R/'reports/R402_body_topology_diagnostic.json').write_text(json.dumps(rows,indent=2));print(rows)
