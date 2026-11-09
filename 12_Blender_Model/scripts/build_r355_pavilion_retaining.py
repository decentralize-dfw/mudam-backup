import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R348_PAVYON_KADEMELERI_ADAY_v001.blend'))
o=bpy.data.objects['R321_MUSEUM_WEST_MOAT_RETAINING'];old=o.data;materials=list(old.materials)
# Keep the already constructed western run; replace the poorly sampled end
# with independently classified crest stations, including the missing return.
stations=[]
for i in range(12):
 vs=[o.matrix_world@v.co for v in old.vertices[i*4:i*4+4]];stations.append(dict(xy=list((vs[2]+vs[3]).to_2d()/2),z=vs[2].z,base=min(v.z for v in vs)))
for r in json.loads((R/'reports/R352_WALL_CREST_SAMPLES.json').read_text()):
 vals=r['classes']['6'];stations.append(dict(xy=r['xy'],z=vals[2],base=-8.3,source=r['pixel'],spread=vals[3]-vals[1]))
pts=[Vector((*r['xy'],r['z'])) for r in stations];normals=[]
for a,b in zip(pts,pts[1:]):
 d=(b-a).to_2d().normalized();normals.append(Vector((-d.y,d.x,0)))
vertices=[]
for i,p in enumerate(pts):
 n=normals[0] if i==0 else normals[-1] if i==len(pts)-1 else (normals[i-1]+normals[i]).normalized()
 if 0<i<len(pts)-1:n/=max(.35,n.dot(normals[i]))
 a=p-n*.4;b=p+n*.4;z=stations[i]['base'];vertices.extend([(a.x,a.y,z),(b.x,b.y,z),tuple(b),tuple(a)])
faces=[(3,2,1,0),(len(vertices)-4,len(vertices)-3,len(vertices)-2,len(vertices)-1)]
for i in range(len(pts)-1):
 for j in range(4):faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
me=bpy.data.meshes.new('R355_PAVILION_RETURN_CONTINUOUS');me.from_pydata(vertices,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o.data=me
for m in materials:me.materials.append(m)
names=set(l.name for l in old.uv_layers)|{'METRIC_UV_4x3m'}
for name in names:
 uv=me.uv_layers.new(name=name)
 for f in me.polygons:
  n=f.normal;u=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.8 else Vector((1,0,0));v=n.cross(u).normalized()
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/4,q.dot(v)/3)
o['source']='R352 classified ACT2024 crest stations, source/photo matched end return. Independent closed wall; width retained 0.8m pending transverse survey.'
# The inner stone terrace is a retaining mass down to the local lower ground,
# not a floating 15cm pavement. Its surface is independently level-fitted.
floor=bpy.data.objects['R348_MOAT_INNER_ARM_RUIN_FLOOR'];n=len(floor.data.vertices)//2
for v in floor.data.vertices[:n]:v.co.z=-6.2
floor.data.materials.clear();floor.data.materials.append(materials[0]);floor['source']='R347 independent planar masonry terrace; buried foundation base -6.2m is construction overlap, not a surveyed visible level.'
checks=[]
for ob in [o,floor,bpy.data.objects['R348_PAVILION_WEST_RUIN_FLOOR']]:
 bm=bmesh.new();bm.from_mesh(ob.data);checks.append(dict(name=ob.name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(c['nonManifold'] or c['zeroArea'] for c in checks)
out=R/'scenes/MUDAM_R355_PAVYON_SUR_DONUSU_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(out));bpy.ops.object.select_all(action='DESELECT')
for name in ['R321_MUSEUM_WEST_MOAT_RETAINING','R348_MOAT_INNER_ARM_RUIN_FLOOR','R348_PAVILION_WEST_RUIN_FLOOR']:bpy.data.objects[name].select_set(True)
glb=R/'exports/r152_clean/r355_pavilion_return_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));errors=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 if any(not all(math.isfinite(c) for c in v.co) for v in ob.data.vertices):errors.append(ob.name+' nonfinite')
 if any(f.area<1e-10 for f in ob.data.polygons):errors.append(ob.name+' zeroarea')
assert not errors
(R/'reports/R355_PAVILION_RETURN.json').write_text(json.dumps(dict(scene=str(out),accepted=False,published=False,stations=stations,checks=checks,glbErrors=errors,limits=['0.8m existing width retained; precise coping width unverified','Last crest station has a lower outlier; median retained as local candidate','Adjacent terrace edges and east lawn remain unresolved; no whole-ring acceptance']),indent=2));print('R355_REOPEN_EXPORT_PASS',checks)
