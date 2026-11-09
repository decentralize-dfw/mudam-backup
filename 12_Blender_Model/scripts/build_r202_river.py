from pathlib import Path
import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R201_KUZEY_KAPALI_CATILAR_v001.blend'))
rows=json.loads((R/'config/r202_river_domains.json').read_text())['domains'];raw=json.loads((R/'.local_source_cache/r154/terrain.json').read_text());gv=[];gf=[]
for r in raw['meshes']:
 k=len(gv);gv.extend(r['vertices']);gf.extend([k+i for i in f] for f in r['faces'])
ground=BVHTree.FromPolygons(gv,gf,all_triangles=True);cuts=[]
for r in rows:
 for xy in r['cuts']:
  if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))<0:xy.reverse()
  cuts.append((xy,[min(p[0] for p in xy),max(p[0] for p in xy),min(p[1] for p in xy),max(p[1] for p in xy)]))
def split(poly,a,b):
 ins=[];out=[]
 def dist(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp,dq=dist(p),dist(q);(ins if dp>=0 else out).append(p)
  if dp*dq<0:
   t=dp/(dp-dq);v=[u+(w-u)*t for u,w in zip(p,q)];ins.append(v);out.append(v)
 return ins,out
changes=[]
for obj in list(bpy.context.scene.objects):
 if obj.type!='MESH' or not (obj.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS'] or obj.name.startswith(('R182_EXTENSION_GROUND','R182_EXTENSION_ROADS'))):continue
 old=obj.data;old.calc_loop_triangles();uv=old.uv_layers.active;verts=[];faces=[];tex=[];mats=[];cutcount=0
 for t in old.loop_triangles:
  poly=[]
  for vi,li in zip(t.vertices,t.loops):
   p=obj.matrix_world@old.vertices[vi].co;poly.append([*p,*(uv.data[li].uv if uv else (p.x/6,p.y/6))])
  bounds=[min(p[0] for p in poly),max(p[0] for p in poly),min(p[1] for p in poly),max(p[1] for p in poly)];parts=[poly]
  for xy,b in cuts:
   if bounds[1]<b[0] or bounds[0]>b[1] or bounds[3]<b[2] or bounds[2]>b[3]:continue
   result=[]
   for part in parts:
    remain=part
    for a,c in zip(xy,xy[1:]+xy[:1]):
     if len(remain)<3:break
     remain,out=split(remain,a,c)
     if len(out)>=3:result.append(out)
    if len(remain)>=3:cutcount+=1
   parts=result
  for p in parts:
   k=len(verts);verts.extend(v[:3] for v in p);tex.extend(v[3:] for v in p)
   for j in range(1,len(p)-1):faces.append((k,k+j,k+j+1));mats.append(t.material_index)
 me=bpy.data.meshes.new(obj.name+'_R192');me.from_pydata(verts,[],faces);me.update()
 for m in old.materials:me.materials.append(m)
 layer=me.uv_layers.new()
 for p,mi in zip(me.polygons,mats):
  p.material_index=mi;p.use_smooth=True
  for li in p.loop_indices:layer.data[li].uv=tex[me.loops[li].vertex_index]
 obj.data=me;changes.append(dict(name=obj.name,intersections=cutcount));print(obj.name,cutcount,flush=True)

water=bpy.data.materials.new('R202_ALZETTE_WATER');water.use_nodes=True;p=water.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.035,.085,.075,1);p.inputs['Roughness'].default_value=.25;p.inputs['Metallic'].default_value=.12
for i,row in enumerate(rows):
 me=bpy.data.meshes.new('R202_ALZETTE_%02d'%i);me.from_pydata(row['vertices'],[],row['faces']);me.update();me.materials.append(water);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
def inside(p,ring):
 h=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:h=not h
 return h
removed=[]
for o in list(bpy.data.objects):
 if not o.name.startswith('R157_TREE_'):continue
 p=o.matrix_world.translation
 if any(inside(p,r['outer']) and not any(inside(p,h) for h in r['holes']) for r in rows):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
(R/'reports/R202_RIVER_RELATION.json').write_text(json.dumps(dict(accepted=False,source='OSM banks and ACT2024 MNT independent water plane',terrain_changes=changes,removed_tree_roots=removed,limits=['Water plane fit has partial support; shoreline height comparison pending','Road crossings require independently modeled bridge decks; not all crossings accepted']),indent=2))
s=bpy.context.scene;t=Vector((-165,-365,-55));s.camera.location=t+Vector((-180,-200,140));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=340;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R202_ALT_MAHALLE_NEHIR_v001.blend'),compress=True);s.render.filepath=str(R/'renders/qa/R202_river_ground_v001.png');bpy.ops.render.render(write_still=True)
