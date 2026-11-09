import bpy,bmesh,json,ast
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R536_DOGU_KALINTI_HENDEK_TABANI_ADAY_v001.blend'));d=json.loads((R/'reports/R540_NORTH_REBUILD_DESIGN.json').read_text());checks=[]
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name+'_R540');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));ck=dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not ck['nonManifold']and not ck['zeroArea'],ck;bm.to_mesh(me);bm.free();checks.append(ck);ob=bpy.data.objects.get(name)
 if ob:ob.data=me
 else:ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob)
 me.materials.append(mat);ob['level_id']='SITE';ob['source']='R540 independent north outer works reconstructed from classified LiDAR floor/upper ground break and ACT plan. No source mesh copied. Round corner and hidden base are explicit architectural interpolation.'
 for name in ('UVMap','R55_CONTEXT_METRIC_UV','METRIC_UV_4x3m'):
  uv=me.uv_layers.new(name=name)
  for f in me.polygons:
   for li in f.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/3,v.y/3)if abs(f.normal.z)>.7 else((v.x if abs(f.normal.y)>.5 else v.y)/3,v.z/3)
 return ob
vs=[]
for inner,outer,z in zip(d['inner'],d['outer'],d['cap']):vs.extend([(*inner,-4),(*outer,-4),(*outer,z),(*inner,z)])
fs=[(3,2,1,0),tuple(range(len(vs)-4,len(vs)))]+[(4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j)for i in range(len(d['inner'])-1)for j in range(4)]
mesh('R152_RUIN_PARTITION_00',vs,fs,bpy.data.objects['R152_RUIN_PARTITION_00'].data.materials[0]);poly=d['floorOutline'];a,b,c=d['floorPlane'];n=len(poly);vs=[(x,y,a*x+b*y+c+dz)for dz in(0,-.18)for x,y in poly];fs=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];mesh('R540_NORTH_RUIN_OUTER_MOAT_FLOOR',vs,fs,bpy.data.materials['R328_RUIN_MINERAL_FLOOR'])
poly=d['outer']+[d['floorOutline'][-3],d['floorOutline'][-2],d['floorOutline'][-1]];regions=[[poly[i]if isinstance(i,int)else(i.x,i.y)for i in t]for t in tessellate_polygon([[Vector((*p,0))for p in poly]])];records=[]
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(n for n in source.body if isinstance(n,ast.FunctionDef)and n.name=='clip');loop=next(n for n in source.body if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='ob');exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));code=ast.unparse(loop).replace("ob.name not in ['R152_CLASS2_TERRAIN']","not (ob.name == 'R152_CLASS2_TERRAIN' or ob.name.startswith('R152_PATH_'))").replace('for region in regions:', 'for region in [r for r in regions if not (max(p[0] for p in points)<min(v[0] for v in r) or min(p[0] for p in points)>max(v[0] for v in r) or max(p[1] for p in points)<min(v[1] for v in r) or min(p[1] for p in points)>max(v[1] for v in r))]:');exec(compile(code,'<terrain cut>','exec'))
me=bpy.data.objects['R152_CLASS2_TERRAIN'].data;groups={};keys={}
for f in me.polygons:
 for li in f.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;key=tuple(round(x,6)for x in v);keys[li]=key;groups.setdefault(key,Vector((0,0,0)));groups[key]+=f.normal*f.area
 f.use_smooth=True
me.normals_split_custom_set([groups[keys[i]].normalized()for i in range(len(me.loops))])
out=R/'scenes/MUDAM_R540_KUZEY_KALINTI_SUR_HENDEK_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R540_BUILD.json').write_text(json.dumps(dict(checks=checks,cuts=records,reopened=True,capChecks=[f['heldout']for f in d['capFits']],floorChecks=d['floorHeldout'],accepted=False,published=False),indent=2));print('R540_SAVED',checks,flush=True)
