from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/act_context/local_glb';out=R/'.local_source_cache/r155';out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
rows=json.loads((D/'manifest.json').read_text())['tiles'];points=[];count=0
for r in rows:
 bounds=np.array(r['bounds_local']);lo=bounds.min(0);hi=bounds.max(0)
 if hi[0]<95 or lo[0]>160 or hi[1]<15 or lo[1]>82:continue
 bpy.ops.import_scene.gltf(filepath=str(D/r['file']));count+=1
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  p=np.array([o.matrix_world@v.co for v in o.data.vertices]);p=p[(p[:,0]>95)&(p[:,0]<160)&(p[:,1]>15)&(p[:,1]<82)];points.append(p)
np.savez_compressed(out/'melia_reference_points.npz',xyz=np.concatenate(points))

from mathutils import Vector
from mathutils.geometry import barycentric_transform
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text())
w=next(w for w in ways if str(w['id'])=='37847300');xy=np.asarray(w['xy'])[:-1]-[293425,5499960]
# Remove collinear OSM survey points, retain the actual four-sided footprint.
keep=[]
for i,p in enumerate(xy):
 a=p-xy[i-1];b=xy[(i+1)%len(xy)]-p
 if abs(np.cross(a,b))/(np.linalg.norm(a)*np.linalg.norm(b))>.003:keep.append(p)
xy=np.asarray(keep);area=sum(np.cross(a,b) for a,b in zip(xy,np.roll(xy,-1,axis=0)))
if area<0:xy=xy[::-1]
pts=np.concatenate(points);roof=float(np.median(pts[(pts[:,2]>32)&(pts[:,2]<36),2]));base=roof-32
images={}
for m in bpy.data.materials:
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image:
    im=n.image;images[m.name]=(np.asarray(im.pixels[:]).reshape(im.size[1],im.size[0],4),im.size[:]);break
dg=bpy.context.evaluated_depsgraph_get()
def color_at(q,outward):
 hit,p,n,idx,o,mat=bpy.context.scene.ray_cast(dg,Vector(q)+outward*3,-outward,distance=7)
 if not hit or idx<0:return None
 me=o.data;face=me.polygons[idx]
 if len(face.vertices)!=3 or not me.uv_layers.active:return None
 material=me.materials[face.material_index]
 if material.name not in images:return None
 local=o.matrix_world.inverted()@p;v=[me.vertices[i].co for i in face.vertices];uv=[Vector((*me.uv_layers.active.data[i].uv,0)) for i in face.loop_indices];co=barycentric_transform(local,*v,*uv)
 pixels,size=images[material.name];return pixels[int((co.y%1)*(size[1]-1)),int((co.x%1)*(size[0]-1)),:3].tolist()
sides=[]
for side,(a,b) in enumerate(zip(xy,np.roll(xy,-1,axis=0))):
 delta=b-a;length=float(np.linalg.norm(delta));u=delta/length;outward=Vector((u[1],-u[0],0));cols=round(length/1.25);rows=20;cells=[]
 for j in range(rows):
  for i in range(cols):
   samples=[]
   for du,dz in [(0,0),(-.2,0),(.2,0),(0,-.25),(0,.25)]:
    q=a+u*((i+.5)*length/cols+du);c=color_at((*q,base+(j+.5)*32/rows+dz),outward)
    if c is not None:samples.append(c)
   c=np.median(samples,axis=0).tolist() if samples else [.55,.55,.53]
   cells.append(dict(i=i,j=j,rgb=c,samples=len(samples)))
 sides.append(dict(a=a.tolist(),b=b.tolist(),columns=cols,rows=rows,cells=cells))
(out/'melia_facades.json').write_text(json.dumps(dict(footprint=xy.tolist(),roof=roof,base=base,sides=sides,source='OSM 37847300 footprint/32m height; ACT2020 facade color samples; 1.25m x 1.6m panel rhythm approximate',sampled_cells=sum(c['samples']>0 for s in sides for c in s['cells']))))
print('MELIA_FACADE_SAMPLED',roof,base,flush=True)
