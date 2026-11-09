import bpy,bmesh,json,ast,math
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt,tessellate_polygon
R=Path(__file__).resolve().parents[1];d=json.loads((R/'reports/R523_WEST_REBUILD_DOMAINS.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R515_GUNEY_HENDEK_ALT_ZEMIN_ADAY_v001.blend'))
terr=bpy.data.objects['R322_WEST_MUSEUM_TERRACE'];terr.data.calc_loop_triangles();oldbv=BVHTree.FromPolygons([terr.matrix_world@v.co for v in terr.data.vertices],[list(t.vertices)for t in terr.data.loop_triangles],all_triangles=True)
regions=[t for p in d['floor']+d['added'] for t in p['triangles']];records=[]
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(n for n in source.body if isinstance(n,ast.FunctionDef)and n.name=='clip');loop=next(n for n in source.body if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='ob');exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'))
code=ast.unparse(loop).replace('for region in regions:', 'for region in [r for r in regions if not (max(p[0] for p in points)<min(v[0] for v in r) or min(p[0] for p in points)>max(v[0] for v in r) or max(p[1] for p in points)<min(v[1] for v in r) or min(p[1] for p in points)>max(v[1] for v in r))]:')
print('CLIP_START',len(regions),flush=True);exec(compile(code,'<clip terrain>','exec'));print('CLIP_DONE',flush=True)
checks=[]
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name+'_REBUILT');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));ck=dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not ck['nonManifold'] and not ck['zeroArea'],ck;bm.to_mesh(me);bm.free();checks.append(ck)
 o=bpy.data.objects.get(name)
 if o:o.data=me
 else:o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o)
 me.materials.append(mat)
 for un in ('UVMap','R55_CONTEXT_METRIC_UV','METRIC_UV_4x3m','R497_MINERAL_METRIC','MicroUV'):
  uv=me.uv_layers.new(name=un)
  for f in me.polygons:
   for li in f.loop_indices:
    p=me.vertices[me.loops[li].vertex_index].co
    uv.data[li].uv=(p.x/3,p.y/3) if abs(f.normal.z)>.5 else ((p.x if abs(f.normal.y)>.5 else p.y)/3,p.z/3)
 o['source']='R523 independent closed architectural reconstruction, source trace and heldout ground controls. No copied scan mesh.'
 return o
wall=[Vector(p)for p in d['wall']];vs=[]
for i,p in enumerate(wall):
 tangent=wall[min(i+1,len(wall)-1)]-wall[max(0,i-1)];tangent.z=0;tangent.normalize();n=Vector((-tangent.y,tangent.x,0))
 for side,z in [(-1,-9.5),(1,-9.5),(1,p.z),(-1,p.z)]:q=p+n*side*.4;vs.append((q.x,q.y,z))
fs=[(3,2,1,0),(len(vs)-4,len(vs)-3,len(vs)-2,len(vs)-1)]+[(4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j)for i in range(len(wall)-1)for j in range(4)]
mat=bpy.data.objects['R321_MUSEUM_WEST_MOAT_RETAINING'].data.materials[0];mesh('R321_MUSEUM_WEST_MOAT_RETAINING',vs,fs,mat)
poly=d['terraceOutline'];points=list(poly)
def inside(x,y):
 odd=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:odd=not odd
 return odd
for x in range(-52,18):
 for y in range(-50,16):
  if inside(x,y):points.append((x,y))
vv,ee,ff,*_=delaunay_2d_cdt([Vector(p)for p in points],[(i,(i+1)%len(poly))for i in range(len(poly))],[list(range(len(poly)))],1,1e-5)
def height(p):
 h=oldbv.ray_cast(Vector((p.x,p.y,30)),Vector((0,0,-1)),60)[0]
 near=(1e9,0)
 for a,b in zip(wall,wall[1:]):
  v=(b-a).to_2d();t=max(0,min(1,(p-a.to_2d()).dot(v)/v.length_squared));dist=(p-a.to_2d()-t*v).length
  if dist<near[0]:near=(dist,a.z+(b.z-a.z)*t-.12)
 z=h.z if h else near[1];w=max(0,1-near[0]/1.2);return z*(1-w)+near[1]*w
top=[(p.x,p.y,height(p))for p in vv];n=len(top);edges=Counter(tuple(sorted((f[i],f[(i+1)%len(f)])))for f in ff for i in range(len(f)));faces=[tuple(f)for f in ff]+[tuple(i+n for i in reversed(f))for f in ff]+[(a,b,b+n,a+n)for(a,b),ct in edges.items()if ct==1]
mineral=bpy.data.objects['R430_FRONT_APPROACH_PAVING'].data.materials[0];mesh('R322_WEST_MUSEUM_TERRACE',top+[(x,y,-10.5)for x,y,z in top],faces,mineral)
for k,p in enumerate(d['floor']):
 xy=[];idx={}
 def ix(q):
  t=tuple(q)
  if t not in idx:idx[t]=len(xy);xy.append(t)
  return idx[t]
 fs=[tuple(ix(q)for q in t)for t in p['triangles']];n=len(xy);a,b,c=d['floorPlane'];vs=[(x,y,a*x+b*y+c+dz)for dz in (0,-.2)for x,y in xy];edges=Counter(tuple(sorted((t[i],t[(i+1)%3])))for t in fs for i in range(3));faces=fs+[tuple(i+n for i in reversed(f))for f in fs]+[(a,b,b+n,a+n)for(a,b),ct in edges.items()if ct==1];o=mesh('R523_WEST_MOAT_LOWER_GROUND_'+str(k),vs,faces,bpy.data.objects['R152_CLASS2_TERRAIN'].data.materials[0])
 for layer in o.data.uv_layers:
  for l in o.data.loops:
   q=o.data.vertices[l.vertex_index].co;layer.data[l.index].uv=((q.x+500)/1150,(q.y+450)/1100) if layer.name=='UVMap' else (q.x/6,q.y/6)
# Separately authored planar sloping masonry, traced outline and independent checks.
for part in d['diagonal']:
 outline=part['outline'];a,b,c=-.31647746,.39124149,-5.32731015;n=len(outline);vs=[(x,y,a*x+b*y+c if top else -8.2)for top in (False,True)for x,y in outline];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
 mesh('R523_WEST_DIAGONAL_SLOPING_MASONRY',vs,fs,mat)
# Preserve the shared-position terrain shading after attribute-preserving clipping.
o=bpy.data.objects['R152_CLASS2_TERRAIN'];me=o.data;groups={};keys={}
for f in me.polygons:
 for li in f.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;key=tuple(round(a,6)for a in v);keys[li]=key;groups.setdefault(key,Vector((0,0,0)));groups[key]+=f.normal*f.area
 f.use_smooth=True
me.normals_split_custom_set([groups[keys[i]].normalized()for i in range(len(me.loops))])
# Use an exportable normal-map mineral shader rather than an unbaked procedural bump.
mineral=bpy.data.materials['R457_LOADING_COURT_MINERAL'].copy();mineral.name='R523_WEST_TERRACE_MINERAL';mineral.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.24,.215,.18,1)
bpy.data.objects['R322_WEST_MUSEUM_TERRACE'].data.materials[0]=mineral
out=R/'scenes/MUDAM_R523_BATI_SUR_TERAS_HENDEK_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));dg=bpy.context.evaluated_depsgraph_get();tests=[]
old=json.loads((R/'reports/R514_FULL_SCENE_CONTACT_RECHECK.json').read_text())['rows']
for q in old:
 if not(-24<q['x']<0 and -18<q['y']<3):continue
 h,p,n,idx,o,m=bpy.context.scene.ray_cast(dg,Vector((q['x'],q['y'],35)),Vector((0,0,-1)),distance=80)
 tests.append(dict(x=q['x'],y=q['y'],object=o.name if h else None,error=p.z-q['ground']if h else None))
(R/'reports/R523_BUILD.json').write_text(json.dumps(dict(checks=checks,reopened=True,cut=records,targetControls=tests,accepted=False,published=False),indent=2));print('R523_OK',checks,tests)
