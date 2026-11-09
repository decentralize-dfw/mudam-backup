import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R257_KULE_CATI_CEPHE_BIRLESIM_ADAY_v001.blend'));metal=bpy.data.materials['R255_TOWER_SILVER'];pieces=[]
def beam(n,a,b,width=.12):
 u=(b-a).normalized();v=u.cross(Vector((0,0,1)));v.normalize();w=u.cross(v).normalized();vs=[tuple(p+v*x+w*y) for p in [a,b] for x,y in [(-width/2,-width/2),(width/2,-width/2),(width/2,width/2),(-width/2,width/2)]];me=bpy.data.meshes.new(n);me.from_pydata(vs,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(metal);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);pieces.append(o)
# Roof framing must stand above the 120mm glazed roof plate.
for o in bpy.context.scene.objects:
 if o.name.startswith('R257_ROOF_FRAME'):
  for v in o.data.vertices:v.co.z+=.15
p=json.loads((R/'config/r256_tower_roof_planes.json').read_text());r=[Vector(v) for v in [(246,382),(269,400),(241,435),(223,421)]];a,b,c,d=r;m=d.lerp(a,.5);n=b.lerp(c,.5)
for k,(poly,co) in enumerate([([a,b,n,m],p[3]['plane']),([m,n,c,d],p[0]['plane'])]):
 q=[Vector((v.x,v.y,co[0]*v.x+co[1]*v.y+co[2])) for v in poly]
 for j,(x,y) in enumerate(zip(q,q[1:]+q[:1])):
  beam(f'R258_CROWN_EDGE_{k}_{j}',x+Vector((0,0,.17)),y+Vector((0,0,.17)),.25)
  for z in [91.8,95.45]:
   if max(x.z,y.z)<z:continue
   aa=x.copy();bb=y.copy()
   if min(x.z,y.z)<z:
    hit=x.lerp(y,(z-x.z)/(y.z-x.z))
    if x.z<z:aa=hit
    else:bb=hit
   aa.z=bb.z=z;beam(f'R258_CROWN_TRANSOM_{k}_{j}_{z}',aa,bb,.24)
# Source silhouette: front-left edge x934 at crown, x978 at lower facade;
# front-right edge ~1256 stays aligned. Independently model the facade taper.
u=(Vector((269,400))-Vector((246,382))).normalized();span=(Vector((269,400))-Vector((246,382))).length
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith(('R256_','R257_','R258_')):continue
 for v in o.data.vertices:
  across=(Vector((v.co.x,v.co.y))-Vector((246,382))).dot(u);weight=max(0,min(1,1-across/span));height=max(0,min(1,(88.35-v.co.z)/(88.35-7)));delta=u*(4.0*weight*height);v.co.x+=delta.x;v.co.y+=delta.y
# Restore a physically plausible brighter blue-gray PBR base; no source images.
for ma in bpy.data.materials:
 if ma.name.startswith('R255_TOWER_BLUE_GLASS'):
  bs=ma.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.19,.34,.39,1);bs.inputs['Metallic'].default_value=.18
path=R/'scenes/MUDAM_R258_KULE_KAYNAK_SILUET_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.cycles.samples=16;s.render.filepath=str(R/'renders/qa/R258_towers_source_matched.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith(('R255_','R256_','R257_','R258_')))
glb=R/'exports/r152_clean/r258_towers_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R258_TOWER_SILHOUETTE.json').write_text(json.dumps(dict(accepted=False,published=False,checks=checks,sourceObservations={'leftUpperPixel':934,'leftLowerPixel':978,'rightPixel':1256,'lowerInsetM':4},limits=['Roof service recess and mechanical details unresolved','Rear facade requires source view','Taper checked in one source elevation only','Terrain/hardscape repair still required; not region completion']),indent=2));assert checks and all(not c['boundary'] and not c['zero'] for c in checks);print('R258_READY',len(checks),flush=True)
