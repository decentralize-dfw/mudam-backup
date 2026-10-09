"""Check saved upper-gallery glass-to-sky paths against current opaque geometry."""
from pathlib import Path
import bpy,json,sys,re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
r=verified_current_scene();bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
panels=json.loads((B/'reports/R24_build_report.json').read_text())['panels'];deps=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];owners=[];names=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or ob.get('level_id')=='SITE':continue
    if ob.name.startswith('R24_GLASS_'):continue
    eo=ob.evaluated_get(deps);me=eo.to_mesh();start=len(verts);verts.extend(eo.matrix_world@v.co for v in me.vertices);names.append(ob.name)
    for f in me.polygons:faces.append(tuple(start+i for i in f.vertices));owners.append(len(names)-1)
    eo.to_mesh_clear()
tree=BVHTree.FromPolygons(verts,faces);rows=[]
for p in panels:
    c=Vector(p['center']);a=c-Vector((0,.2,.1));d=(c+Vector((0,60,84))-a).normalized();hit=tree.ray_cast(a,d,104)
    rows.append(dict(panel=p['name'],opaque_hit=None if hit[0] is None else names[owners[hit[2]]],distance=None if hit[0] is None else hit[3],position=None if hit[0] is None else list(hit[0])))
rev=re.search(r'_R(\d+)_',r['file']).group(1)
out=dict(file=r['file'],rays=rows,blocked_count=sum(p['opaque_hit'] is not None for p in rows),construction_acceptance=False,limits=['Single inherited R24 sky direction per panel; not a daylight simulation or survey.'])
(B/'reports'/f'R{rev}_gallery_daylight_path.json').write_text(json.dumps(out,indent=2));print('DAYLIGHT',len(rows),out['blocked_count']);print([p for p in rows if p['opaque_hit']])
