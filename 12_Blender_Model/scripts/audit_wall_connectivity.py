"""Wall-only connected components: diagnostic, not an architectural acceptance rule."""
from pathlib import Path
import bpy,json,itertools
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/DUVAR_ENVANTERI.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['scene']));deps=bpy.context.evaluated_depsgraph_get();data={};parent={};links=[]
for row in r['objects']:
 name=row['name'];ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();vs=[ob.matrix_world@v.co for v in me.vertices];data[name]=(BVHTree.FromPolygons(vs,[list(f.vertices) for f in me.polygons]),vs,([min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]));ob.to_mesh_clear();parent[name]=name
def root(n):
 while parent[n]!=n:n=parent[n]
 return n
for a,b in itertools.combinations(data,2):
 ta,va,ba=data[a];tb,vb,bb=data[b]
 if any(ba[1][i]<bb[0][i]-.002 or bb[1][i]<ba[0][i]-.002 for i in range(3)):continue
 contact=bool(ta.overlap(tb))
 if not contact:contact=any((h:=tb.find_nearest(v,.002))[0] is not None for v in va) or any((h:=ta.find_nearest(v,.002))[0] is not None for v in vb)
 if contact:parent[root(a)]=root(b);links.append([a,b])
groups={}
for name in data:groups.setdefault(root(name),[]).append(name)
result=dict(file=r['scene'],wall_count=len(data),surface_or_vertex_contacts=links,components=sorted(groups.values(),key=lambda g:-len(g)),limits='Independent pavilion, slab-separated levels, door/frame components, detached architectural walls and stair cores may correctly be separate. No completion claim follows from this graph.');(B/'reports/DUVAR_BAGLANTI_GRAFIGI.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('COMPONENTS',len(groups))
for group in result['components']:print(len(group),','.join(group[:30]))
