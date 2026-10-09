"""Local skin continuity of east/west roof cells, including the frame margins."""
from pathlib import Path
import bpy,json,sys,math,re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
r={'file':args[0]} if args else verified_current_scene()
bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
rev=re.search(r'_R(\d+)_',r['file']).group(1)
domains=B/'reports/R89_side_roof_domains.json'
if not domains.exists():
    assert rev=='89'
    old={x['name']:x for x in json.loads((B/'reports/R12_build_report.json').read_text())['panels']}
    rows=[]
    for ob in bpy.context.scene.objects:
        if not ob.name.startswith(('P11_EAST_','P11_WEST_')) or ob.get('element_type')!='glass_panel':continue
        original=[Vector(x) for x in old[ob.name]['old_vertices'][:4]] if ob.name in old else [v.co.copy() for v in ob.data.vertices[:4]]
        original=[ob.matrix_world@p for p in original]
        center=sum(original,Vector())/4;short=min((a-b).length for a,b in zip(original,original[1:]+original[:1]))
        factor=1-.045/(short+.045)
        assert factor>.9, (ob.name,factor)
        raw=[center+(p-center)/factor for p in original]
        current=[ob.matrix_world@v.co for v in ob.data.vertices[:4]]
        origin=sum(current,Vector())/4;n=(current[1]-current[0]).cross(current[3]-current[0]).normalized()
        if n.z<0:n=-n
        flat=[p-n*(p-origin).dot(n) for p in raw]
        rows.append(dict(name=ob.name,polygon=[list(p) for p in flat],normal=list(n)))
    assert len(rows)==228,len(rows)
    domains.write_text(json.dumps(dict(file=r['file'],panels=rows,limits=['P11 documented centroid shrink inverted; R12 pre-flattening coordinates used for west.', 'Domain projected onto existing accepted glass plane; no roof shape change inferred.']),indent=2))
data=json.loads(domains.read_text());verts=[];faces=[]
deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or not ob.name.startswith('P11_'):continue
    if ob.get('element_type') not in ['glass_panel','surface_frame','opaque_stone_base_envelope']:continue
    eo=ob.evaluated_get(deps);mesh=eo.to_mesh();start=len(verts);verts.extend(eo.matrix_world@v.co for v in mesh.vertices)
    faces.extend(tuple(start+i for i in f.vertices) for f in mesh.polygons);eo.to_mesh_clear()
tree=BVHTree.FromPolygons(verts,faces);result=[]
for row in data['panels']:
    ps=[Vector(p) for p in row['polygon']];n=Vector(row['normal']);center=sum(ps,Vector())/4;missing=[];count=0
    for ei,(a,b) in enumerate(zip(ps,ps[1:]+ps[:1])):
        edge=b-a;side=n.cross(edge).normalized()
        if side.dot(center-(a+b)/2)<0:side=-side
        steps=max(1,math.ceil(edge.length/.05))
        for i in range(steps):
            for inset in [0,.01,.02,.03,.04,.06,.08]:
                p=a+edge*((i+.5)/steps)+side*inset
                signs=[(v-u).cross(p-u).dot(n) for u,v in zip(ps,ps[1:]+ps[:1])]
                if min(signs)<-1e-5 and max(signs)>1e-5:continue
                count+=1
                if tree.ray_cast(p+n*.2,-n,.4)[0] is None:missing.append(dict(position=list(p),edge=ei,inset=inset))
    result.append(dict(name=row['name'],samples=count,missing_count=len(missing),missing=missing))
out=dict(file=r['file'],panels=result,total_samples=sum(x['samples'] for x in result),missing_count=sum(x['missing_count'] for x in result),construction_acceptance=False)
(B/'reports'/f'R{rev}_side_roof_skin.json').write_text(json.dumps(out,indent=2))
print('SIDE ROOF',out['total_samples'],out['missing_count'], 'affected panels',sum(x['missing_count']>0 for x in result))
