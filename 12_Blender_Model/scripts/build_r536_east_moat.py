import bpy,bmesh,json,ast
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R534_DOGU_KALINTI_DIS_DUVAR_ADAY_v001.blend'));d=json.loads((R/'reports/R536_EAST_MOAT_DESIGN.json').read_text());regions=d['triangles'];records=[]
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(n for n in source.body if isinstance(n,ast.FunctionDef)and n.name=='clip');loop=next(n for n in source.body if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='ob');exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));code=ast.unparse(loop).replace("ob.name not in ['R152_CLASS2_TERRAIN']","not (ob.name == 'R152_CLASS2_TERRAIN' or ob.name.startswith('R152_PATH_'))").replace('for region in regions:', 'for region in [r for r in regions if not (max(p[0] for p in points)<min(v[0] for v in r) or min(p[0] for p in points)>max(v[0] for v in r) or max(p[1] for p in points)<min(v[1] for v in r) or min(p[1] for p in points)>max(v[1] for v in r))]:');exec(compile(code,'<terrain cut>','exec'))
poly=d['outline'];a,b,c=d['plane'];n=len(poly);vs=[(x,y,a*x+b*y+c+dz)for dz in(0,-.18)for x,y in poly];fs=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];me=bpy.data.meshes.new('R536_EAST_RUIN_OUTER_MOAT_FLOOR');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));ck=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not any(ck.values());bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);ob['level_id']='SITE';ob['source']='Independent outer moat floor, classified LiDAR controls and source-traced architectural limits.41heldout RMS0.0477m/max0.1702m. Replaces intruding generic terrain; no scan faces.';me.materials.append(bpy.data.materials['R328_RUIN_MINERAL_FLOOR']);uv=me.uv_layers.new(name='UVMap')
for l in me.loops:
 v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x/2,v.y/2)
me=bpy.data.objects['R152_CLASS2_TERRAIN'].data;groups={};keys={}
for f in me.polygons:
 for li in f.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;key=tuple(round(x,6)for x in v);keys[li]=key;groups.setdefault(key,Vector((0,0,0)));groups[key]+=f.normal*f.area
 f.use_smooth=True
me.normals_split_custom_set([groups[keys[i]].normalized()for i in range(len(me.loops))])
out=R/'scenes/MUDAM_R536_DOGU_KALINTI_HENDEK_TABANI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R536_BUILD.json').write_text(json.dumps(dict(check=ck,reopened=True,cuts=records,sourceControls=d['heldout'],accepted=False,published=False),indent=2));print('R536_SAVED',ck,flush=True)
