import bpy,bmesh,json,ast
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R530_GUNEY_SUR_TAM_KESIT_ADAY_v001.blend'))
d=json.loads((R/'reports/R531_FULL_ROAD_PLANE.json').read_text());a,b,c=d['plane'];wall=bpy.data.objects['R494_SOUTH_PAVILION_OUTER_RETAINING_WALL'];poly=[tuple(wall.data.vertices[i+1].co[:2])for i in range(0,len(wall.data.vertices),4)];poly.extend([(72.13087,.102*72.13087-55),(49.04445,.102*49.04445-55)])
tris=tessellate_polygon([[Vector((*p,0))for p in poly]]);regions=[[poly[i]if isinstance(i,int)else(i.x,i.y)for i in t]for t in tris];records=[]
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(n for n in source.body if isinstance(n,ast.FunctionDef)and n.name=='clip');loop=next(n for n in source.body if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='ob');exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));code=ast.unparse(loop).replace('for region in regions:', 'for region in [r for r in regions if not (max(p[0] for p in points)<min(v[0] for v in r) or min(p[0] for p in points)>max(v[0] for v in r) or max(p[1] for p in points)<min(v[1] for v in r) or min(p[1] for p in points)>max(v[1] for v in r))]:');exec(compile(code,'<terrain cut>','exec'))
a,b,c=d['plane'];n=len(poly);verts=[(x,y,a*x+b*y+c+dz)for dz in(0,-.25)for x,y in poly];faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];me=bpy.data.meshes.new('R531_SOUTH_PAVILION_PAVED_APPROACH');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not any(check.values());bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);ob['level_id']='SITE';ob['source']='Independent plane from classified ground:302 training/99 heldout cells, RMS0.03673m/max0.12212m. Paved extent from ACT view; no source mesh copied. Edge transitions pending visual acceptance.'
mat=bpy.data.materials['R457_LOADING_COURT_MINERAL'];me.materials.append(mat)
for name in ('UVMap','R497_MINERAL_METRIC','R55_CONTEXT_METRIC_UV','MicroUV'):
 uv=me.uv_layers.new(name=name)
 for loop in me.loops:
  v=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x/3,v.y/3)
me=bpy.data.objects['R152_CLASS2_TERRAIN'].data;groups={};keys={}
for f in me.polygons:
 for li in f.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;k=tuple(round(x,6)for x in v);keys[li]=k;groups.setdefault(k,Vector((0,0,0)));groups[k]+=f.normal*f.area
 f.use_smooth=True
me.normals_split_custom_set([groups[keys[i]].normalized()for i in range(len(me.loops))])
out=R/'scenes/MUDAM_R531_GUNEY_SUR_ARKASI_SERT_ZEMIN_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R531_BUILD.json').write_text(json.dumps(dict(check=check,cut=records,reopened=True,planeValidation=d['heldout'],accepted=False,published=False),indent=2));print('R531_SAVED',check,flush=True)

