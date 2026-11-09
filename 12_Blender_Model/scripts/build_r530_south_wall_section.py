import bpy,bmesh,json,ast
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R525_BATI_TERAS_EGIMLI_KENAR_ADAY_v001.blend'))
a,b,c=json.loads((R/'reports/R529_SOUTH_FACE_PLANE.json').read_text())['plane']
stations=[49.04445,54,58,64,68,72.13087]
def crest(x):return -2.02+min(1,max(0,(x-54)/4))*.57
vs=[]
for x in stations:
 z=crest(x);front=a*x+b*z+c
 vs.extend([(x,a*x+b*-9+c,-9),(x,front+2,-9),(x,front+2,z),(x,front,z)])
checks=[];regions=[]
def replace(name,verts):
 ob=bpy.data.objects[name];mat=ob.data.materials[0];faces=[(3,2,1,0),tuple(range(len(verts)-4,len(verts)))]+[(4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j)for i in range(len(verts)//4-1)for j in range(4)]
 me=bpy.data.meshes.new(name+'_R530');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));ck=dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not ck['nonManifold'] and not ck['zeroArea'],ck;bm.to_mesh(me);bm.free();checks.append(ck);me.materials.append(mat);ob.data=me
 uv=me.uv_layers.new(name='R55_CONTEXT_METRIC_UV')
 for p in me.polygons:
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.z/3)if abs(p.normal.z)<.8 else(v.x/4,v.y/3)
 ob['R530_source']='Independent planar southern masonry face: 47 training controls, 9 heldout, RMS0.0778m/max0.1457m. Cap widths and obscured return remain visual candidates; no scan mesh reused.'
 for i in range(len(verts)//4-1):
  poly=[verts[4*i][:2],verts[4*(i+1)][:2],verts[4*(i+1)+1][:2],verts[4*i+1][:2]]
  for tr in tessellate_polygon([[Vector((*p,0))for p in poly]]):regions.append([poly[j]if isinstance(j,int)else(j.x,j.y)for j in tr])
replace('R494_SOUTH_PAVILION_OUTER_RETAINING_WALL',vs)
# Maintain the existing measured return crest; replace its shared junction exactly.
ret=bpy.data.objects['R495_SOUTH_OUTER_WALL_EAST_RETURN'];rv=[tuple(v.co)for v in ret.data.vertices];rv[:4]=vs[-4:]
replace(ret.name,rv)
records=[]
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(n for n in source.body if isinstance(n,ast.FunctionDef)and n.name=='clip');loop=next(n for n in source.body if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='ob');exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'))
code=ast.unparse(loop).replace('for region in regions:', 'for region in [r for r in regions if not (max(p[0] for p in points)<min(v[0] for v in r) or min(p[0] for p in points)>max(v[0] for v in r) or max(p[1] for p in points)<min(v[1] for v in r) or min(p[1] for p in points)>max(v[1] for v in r))]:')
exec(compile(code,'<terrain cut>','exec'))
me=bpy.data.objects['R152_CLASS2_TERRAIN'].data;groups={};keys={}
for f in me.polygons:
 for li in f.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;k=tuple(round(x,6)for x in v);keys[li]=k;groups.setdefault(k,Vector((0,0,0)));groups[k]+=f.normal*f.area
 f.use_smooth=True
me.normals_split_custom_set([groups[keys[i]].normalized()for i in range(len(me.loops))])
out=R/'scenes/MUDAM_R530_GUNEY_SUR_TAM_KESIT_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
left=bpy.data.objects['R494_SOUTH_PAVILION_OUTER_RETAINING_WALL'];right=bpy.data.objects['R495_SOUTH_OUTER_WALL_EAST_RETURN'];gap=max((left.data.vertices[len(left.data.vertices)-4+i].co-right.data.vertices[i].co).length for i in range(4));assert gap<1e-6
(R/'reports/R530_BUILD.json').write_text(json.dumps(dict(checks=checks,cuts=records,reopened=True,sharedJunctionGap=gap,accepted=False,published=False,remaining=['Road surface behind cap not yet rebuilt','Obscured return and western termination require photo comparison']),indent=2));print('R530_SAVED',checks,gap,flush=True)
