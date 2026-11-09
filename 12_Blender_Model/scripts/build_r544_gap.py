import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from collections import Counter
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R540_KUZEY_KALINTI_SUR_HENDEK_ADAY_v001.blend'));d=json.loads((R/'reports/R544_GAP_DESIGN.json').read_text());xy=[];lookup={}
def ix(p):
 p=tuple(p)
 if p not in lookup:lookup[p]=len(xy);xy.append(p)
 return lookup[p]
fs=[tuple(ix(p)for p in t)for t in d['triangles']];n=len(xy);a,b,c,e=d['coefficients'];vs=[(x,y,a*x+b*y+c+e*max(y-3.5,0)+dz)for dz in (0,-.18)for x,y in xy];edges=Counter(tuple(sorted((f[i],f[(i+1)%3])))for f in fs for i in range(3));faces=fs+[tuple(i+n for i in reversed(f))for f in fs]+[(a,b,b+n,a+n)for(a,b),ct in edges.items()if ct==1]
me=bpy.data.meshes.new('R544_CLOSED_GROUND');me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not any(check.values()),check;bm.to_mesh(me);bm.free();o=bpy.data.objects.new('R544_WEST_MOAT_MISSING_SLOPED_GROUND',me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials['R157_CONTINUOUS_LANDCOVER'])
for un in ('UVMap','MicroUV'):
 uv=me.uv_layers.new(name=un)
 for l in me.loops:
  p=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((p.x+500)/1150,(p.y+450)/1100)if un=='UVMap'else(p.x/6,p.y/6)
o['source']='Independent continuous two-grade ground from ACT height controls. Existing coverage gap only; no copied scan geometry.'
out=R/'scenes/MUDAM_R544_BATI_HENDEK_ZEMIN_ACIKLIGI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));dg=bpy.context.evaluated_depsgraph_get();tests=[]
for x,y,z in [(-29,3,-6.44073486328125),(-28,3,-6.252479553222656),(-30,4,-6.387302398681641)]:
 h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,35)),Vector((0,0,-1)),distance=80);tests.append(dict(x=x,y=y,object=o.name if h else None,error=p.z-z if h else None));assert h and abs(p.z-z)<.12,tests[-1]
(R/'reports/R544_BUILD.json').write_text(json.dumps(dict(check=check,reopened=True,tests=tests,accepted=False),indent=2));print('R544_OK',tests)
