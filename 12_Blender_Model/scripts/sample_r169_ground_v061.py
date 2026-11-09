from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R170_KAYNAK_ADA_BORDUR_ADAY_v002.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not any(s in o.name.upper() for s in ['TERRAIN','GROUND','TOPO']):continue
 print('GROUND',o.name);o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
t=BVHTree.FromPolygons(vs,fs,all_triangles=True);d=json.loads((R/'.local_source_cache/r169/row_whole_roof_samples_v061.json').read_text());nx=d['nx'];ny=d['ny'];v=d['vertices'];edge=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(ny*nx-2,(ny-1)*nx-1,-1))+[j*nx for j in range(ny-2,0,-1)];hits=[]
for i in edge:
 x,y,z=v[i];h,*_=t.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),250);hits.append(dict(index=i,z=h.z if h else None))
(R/'.local_source_cache/r169/ground_edge_v061.json').write_text(json.dumps(hits));print('RANGE',min(h['z'] for h in hits if h['z']),max(h['z'] for h in hits if h['z']))

