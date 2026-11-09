import bpy,bmesh,json,ast,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R530_GUNEY_SUR_TAM_KESIT_ADAY_v001.blend'));d=json.loads((R/'reports/R532_WHOLE_PAVING_PLANES.json').read_text());regions=[];records=[]
for poly in d['pieces']:
 for t in tessellate_polygon([[Vector((*p,0))for p in poly]]):regions.append([poly[i]if isinstance(i,int)else(i.x,i.y)for i in t])
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(n for n in source.body if isinstance(n,ast.FunctionDef)and n.name=='clip');loop=next(n for n in source.body if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='ob');exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));code=ast.unparse(loop).replace('for region in regions:', 'for region in [r for r in regions if not (max(p[0] for p in points)<min(v[0] for v in r) or min(p[0] for p in points)>max(v[0] for v in r) or max(p[1] for p in points)<min(v[1] for v in r) or min(p[1] for p in points)>max(v[1] for v in r))]:');code=code.replace("ob.name not in ['R152_CLASS2_TERRAIN']", "not (ob.name == 'R152_CLASS2_TERRAIN' or ob.name.startswith('R152_PATH_'))");exec(compile(code,'<terrain cut>','exec'))
def height(x,y):return sum(a*b for a,b in zip(d['coefficients'],[1,x-60,y+45,max(x-58,0),max(x-72,0),max(y+42,0)]))
checks=[]
for k,poly in enumerate(d['pieces']):
 n=len(poly);vs=[(x,y,height(x,y)+dz)for dz in(0,-.25)for x,y in poly];fs=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];me=bpy.data.meshes.new(f'R532_SOUTH_PAVED_APPROACH_{k}');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));ck=dict(name=me.name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not ck['nonManifold']and not ck['zeroArea'],ck;bm.to_mesh(me);bm.free();checks.append(ck);o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);o['level_id']='SITE';o['source']='Independent continuous planar road grades from1001training/342heldout ground controls. ACT footprint trace only. Whole approach replaces R531 rectangle.';me.materials.append(bpy.data.materials['R457_LOADING_COURT_MINERAL'])
 for name in ('UVMap','R497_MINERAL_METRIC','R55_CONTEXT_METRIC_UV','MicroUV'):
  uv=me.uv_layers.new(name=name)
  for loop in me.loops:
   v=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x/3,v.y/3)
# Match adjacent ground only within a narrow border of the actual road outline.
o=bpy.data.objects['R152_CLASS2_TERRAIN'];me=o.data;poly=d['outline'];changes=[]
for v in me.vertices:
 x,y,z=v.co
 if not(34<x<85 and -59<y<-22):continue
 dist=100
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dx=q[0]-p[0];dy=q[1]-p[1];t=max(0,min(1,((x-p[0])*dx+(y-p[1])*dy)/(dx*dx+dy*dy)));dist=min(dist,math.hypot(x-p[0]-t*dx,y-p[1]-t*dy))
 target=height(x,y)
 if dist<.75 and abs(target-z)<.4:
  dz=(target-z)*(1-dist/.75);v.co.z+=dz;changes.append(abs(dz))
me.update();groups={};keys={}
for f in me.polygons:
 for li in f.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;key=tuple(round(x,6)for x in v);keys[li]=key;groups.setdefault(key,Vector((0,0,0)));groups[key]+=f.normal*f.area
 f.use_smooth=True
me.normals_split_custom_set([groups[keys[i]].normalized()for i in range(len(me.loops))])
out=R/'scenes/MUDAM_R532_GUNEY_TAM_YAYA_ALANI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R532_BUILD.json').write_text(json.dumps(dict(checks=checks,cuts=records,reopened=True,edgeBlendVertices=len(changes),edgeBlendMax=max(changes,default=0),sourceControlValidation=d['heldout'],accepted=False,published=False),indent=2));print('R532_SAVED',checks,flush=True)

