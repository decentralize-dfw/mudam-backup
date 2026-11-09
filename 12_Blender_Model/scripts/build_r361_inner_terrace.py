import bpy,bmesh,json,ast,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R358_PAVYON_TERAS_TEMIZLIK_ADAY_v001.blend'))
row=json.loads((R/'reports/R360_PAVILION_PLANES.json').read_text())['moat_inner_arm'];assert row['valid'];xy=row['outline'];regions=[];records=[]
for face in tessellate_polygon([[Vector((x,y,0)) for x,y in xy]]):regions.append([xy[i] if isinstance(i,int) else (i.x,i.y) for i in face])
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='clip');loop=next(n for n in source.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='ob');code=ast.unparse(loop).replace("ob.name not in ['R152_CLASS2_TERRAIN']","not (ob.name in ['R152_CLASS2_TERRAIN','R322_WEST_MUSEUM_TERRACE'] or ob.name.startswith('R152_PATH_'))");exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));exec(compile(code,'<bounded surfaces>','exec'))
o=bpy.data.objects['R348_MOAT_INNER_ARM_RUIN_FLOOR'];mat=o.data.materials[0];a,b,c=row['plane'];n=len(xy);vs=[(x,y,-6.2) for x,y in xy]+[(x,y,a*x+b*y+c) for x,y in xy];fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
def finish(me):
 me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(mat)
 names={'METRIC_UV_4x3m'}|{getattr(v,'uv_map','') for v in mat.node_tree.nodes};names.discard('')
 for name in names:
  uv=me.uv_layers.new(name=name)
  for f in me.polygons:
   n=f.normal;u=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.8 else Vector((1,0,0));v=n.cross(u).normalized()
   for li in f.loop_indices:
    q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/4,q.dot(v)/3)
me=bpy.data.meshes.new('R361_MEASURED_INNER_TERRACE');me.from_pydata(vs,[],fs);finish(me);o.data=me
# The source-visible inner retaining edge is an independent masonry solid.
# Only stations supported by classified returns below the glass bridge are used.
points=[(4,-43,-2.50102575),(9.1875,-39.375,-1.78102577),(13.875,-35.9375,-1.10102575)]
vs=[];pts=[Vector(p) for p in points];norms=[]
for p,q in zip(pts,pts[1:]):
 d=(q-p).to_2d().normalized();norms.append(Vector((-d.y,d.x,0)))
for i,p in enumerate(pts):
 n=norms[0] if i==0 else norms[-1] if i==len(pts)-1 else (norms[i-1]+norms[i]).normalized();a=p-n*.4;b=p+n*.4;vs.extend([(a.x,a.y,-6.2),(b.x,b.y,-6.2),tuple(b),tuple(a)])
fs=[(3,2,1,0),(len(vs)-4,len(vs)-3,len(vs)-2,len(vs)-1)]
for i in range(len(pts)-1):
 for j in range(4):fs.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
me=bpy.data.meshes.new('R361_PAVILION_INNER_RETAINING');me.from_pydata(vs,[],fs);finish(me);wall=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(wall);wall['level_id']='SITE';wall['source']='Independent masonry, visible plan trace R345, classified crest elevations R359; bridge-occluded continuation not invented; width 0.8m provisional.'
checks=[]
for ob in [o,wall]:
 bm=bmesh.new();bm.from_mesh(ob.data);checks.append(dict(name=ob.name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(c['nonManifold'] or c['zeroArea'] for c in checks)
out=R/'scenes/MUDAM_R361_PAVYON_IC_SUR_TERAS_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));bpy.ops.object.select_all(action='DESELECT')
for name in ['R348_MOAT_INNER_ARM_RUIN_FLOOR','R361_PAVILION_INNER_RETAINING']:bpy.data.objects[name].select_set(True)
glb=R/'exports/r152_clean/r361_inner_terrace_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));errors=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and (any(f.area<1e-10 for f in ob.data.polygons) or any(not all(math.isfinite(c) for c in v.co) for v in ob.data.vertices)):errors.append(ob.name)
assert not errors
(R/'reports/R361_INNER_TERRACE.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,clipped=records,meshChecks=checks,glbErrors=errors,levelFit=row,remaining=['Bridge-obscured inner wall continuation','Pavilion east lawn and continuous junctions','Full source visual acceptance']),indent=2))
