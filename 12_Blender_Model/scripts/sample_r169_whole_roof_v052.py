from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_rear_dormer_cap_trials.json').read_text())[0];q=np.array([[-68.10883331298828+(x-700)/175,-293.02964782714844+(700-y)/175] for x,y in d['pixels']]);bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True)

# Full roof domain from source top view, rear edge extended to visible eave.
pixels=[(340,190),(850,70),(1014,778),(450,903)]
q=np.array([[-67+(x-700)/70,-299+(550-y)/70] for x,y in pixels])
t=q[1]-q[0];t=t/np.linalg.norm(t);out=np.array([-t[1],t[0]]);q[:2]+=out*.9
def xy(u,v):return (1-v)*((1-u)*q[0]+u*q[1])+v*((1-u)*q[3]+u*q[2])
def hit(x,y):
 h,*_=tree.ray_cast(Vector((float(x),float(y),50)),Vector((0,0,-1)),200);assert h is not None;return list(h)
nx=49;ny=81
verts=[hit(*xy(u,v)) for v in np.linspace(0,1,ny) for u in np.linspace(0,1,nx)]
r=dict(vertices=verts,nx=nx,ny=ny,ring=q.tolist(),pixels=pixels)
(D/'row_whole_roof_samples_v052.json').write_text(json.dumps(r))
print('HEIGHTS',min(p[2] for p in verts),max(p[2] for p in verts))
print('BOUNDARY',[(k,[round(verts[i][2],3) for i in inds]) for k,inds in [('rear',range(0,nx,4)),('front',range((ny-1)*nx,ny*nx,4))]])
