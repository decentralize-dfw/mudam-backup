from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
source=BVHTree.FromPolygons(vs,fs,all_triangles=True)
# Registered top image displayed at1600: 260m extent centered(-210,-175).
polys=[('MOAT_NORTH',[(876,600),(1037,581),(1078,598),(1098,618),(1080,630),(1030,605),(887,623)]),('MOAT_EAST',[(1098,618),(1110,630),(1110,800),(1080,795),(1080,640)]),('UPPER_NORTH_PLATFORM',[(792,468),(944,400),(1047,466),(1136,460),(1080,492),(935,505),(830,497)])]
data=[]
for name,pixels in polys:
 xy=np.array([[-340+x*260/1600,-45-y*260/1600] for x,y in pixels]);center=xy.mean(0);samples=[]
 for p in list(xy*.85+center*.15)+[center]:
  hit,n,*_=source.ray_cast(Vector((*p,150)),Vector((0,0,-1)),350)
  if hit and abs(n.z)>.6:samples.append([*p,hit.z])
 if len(samples)<3:continue
 a=np.array(samples);origin=a[:,:2].mean(0);coef=np.linalg.lstsq(np.c_[a[:,:2]-origin,np.ones(len(a))],a[:,2],rcond=None)[0];err=abs(np.c_[a[:,:2]-origin,np.ones(len(a))]@coef-a[:,2]);data.append(dict(name=name,pixels=pixels,xy=xy.tolist(),origin=origin.tolist(),plane=coef.tolist(),sourceSamples=samples,residualMax=float(err.max()),accepted=bool(err.max()<.65)))
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_SUR_ADAY_v001.blend'))
mat=bpy.data.materials.new('R172_DRY_GRASS_TERRACES');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.24,.255,.14,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=1
for row in data:
 if not row['accepted']:continue
 xy=np.array(row['xy']);origin=np.array(row['origin']);plane=np.array(row['plane']);zs=np.c_[xy-origin,np.ones(len(xy))]@plane+.025;verts=[Vector((x,y,z)) for (x,y),z in zip(xy,zs)];faces=[]
 for tri in tessellate_polygon([verts]):faces.append([v if isinstance(v,int) else min(range(len(verts)),key=lambda j:(verts[j]-v).length_squared) for v in tri])
 me=bpy.data.meshes.new('R172_'+row['name']);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);me.materials.append(mat);o['source']='Manually traced ACT reference boundary, independent planar terrace fitted to sparse surveyed reference points';o['acceptance']='Local candidate, not whole fort acceptance'
 # Match existing terrain within this authored terrace footprint; preserve outside ground.
 for terrain in bpy.context.scene.objects:
  if terrain.name not in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN']:continue
  for v in terrain.data.vertices:
   p=terrain.matrix_world@v.co;inside=False
   for a,b in zip(xy,np.roll(xy,-1,axis=0)):
    if ((a[1]>p.y)!=(b[1]>p.y)) and p.x<(b[0]-a[0])*(p.y-a[1])/(b[1]-a[1]+1e-15)+a[0]:inside=not inside
   if inside:p.z=float(np.dot([p.x-origin[0],p.y-origin[1],1],plane));v.co=terrain.matrix_world.inverted()@p
  terrain.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_TERAS_ADAY_v003.blend'),compress=True)
(R/'reports/R172_TERRACES_v003.json').write_text(json.dumps(dict(accepted=False,terraces=data,limits=['Only source-visible polygons traced','Rejected non-planar or vegetation-obscured terrace fits excluded','Terrain-edge and wall junctions still require verification']),indent=2));print('TERRACES',[(r['name'],r['accepted'],r['residualMax']) for r in data])
s=bpy.context.scene;target=Vector((-210,-175,-35));s.camera.location=target+Vector((70,-150,180));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=280;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R172_fort_terraces_v003.png');bpy.ops.render.render(write_still=True)


