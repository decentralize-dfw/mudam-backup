import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'reports/R515_SOUTH_MOAT_FLOOR_DOMAIN.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R512_KALE_DIS_TASAN_TOPRAK_KESIM_ADAY_v001.blend'))
cx,cy=d['center'];a,b,c=d['coefficients'];names=[];checks=[]
for k,piece in enumerate(d['pieces']):
 xy=[];lookup={}
 def ix(p):
  key=tuple(p)
  if key not in lookup:lookup[key]=len(xy);xy.append(p)
  return lookup[key]
 top=[tuple(ix(p) for p in t) for t in piece['triangles']]
 outline=[ix(p) for p in piece['outline']]
 if outline[-1]==outline[0]:outline.pop()
 n=len(xy);vs=[(x,y,a+b*(x-cx)+c*(y-cy)+dz) for dz in (0,-.18) for x,y in xy]
 fs=top+[tuple(i+n for i in reversed(t)) for t in top]
 from collections import Counter
 edges=Counter(tuple(sorted((t[i],t[(i+1)%3]))) for t in top for i in range(3))
 fs += [(i,j,j+n,i+n) for (i,j),count in edges.items() if count==1]
 me=bpy.data.meshes.new('R515_MEASURED_LOWER_GROUND');me.from_pydata(vs,[],fs);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 ck=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));print('BAD_EDGES',[[tuple(v.co) for v in e.verts] for e in bm.edges if not e.is_manifold]);assert not any(ck.values()),ck
 bm.to_mesh(me);bm.free();checks.append(ck)
 o=bpy.data.objects.new('R515_SOUTH_MOAT_LOWER_GROUND_'+str(k),me);bpy.context.scene.collection.objects.link(o);names.append(o.name)
 src=bpy.data.objects.get('R430_FRONT_APPROACH_PAVING')
 if src:
  for mat in src.data.materials:me.materials.append(mat)
 for uvname in ('UVMap','R55_CONTEXT_METRIC_UV','R497_MINERAL_METRIC'):
  uv=me.uv_layers.new(name=uvname)
  for loop in me.loops:
   v=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x/3,v.y/3)
 o['source']='Independent planar lower moat floor; withheld LiDAR controls in R515 plane report. Not a copied scan surface.'
out=R/'scenes/MUDAM_R515_GUNEY_HENDEK_ALT_ZEMIN_ADAY_v001.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for x,y,z in [(-61.765616,-65.813892,-9.716026),(-59.726354,-67.794421,-9.681026)]:
 h,p,n,idx,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,35)),Vector((0,0,-1)),distance=80)
 rows.append(dict(x=x,y=y,hit=o.name if h else None,error=p.z-z if h else None));assert h and abs(p.z-z)<.08,rows[-1]
(R/'reports/R515_BUILD.json').write_text(json.dumps(dict(scene=str(out),objects=names,checks=checks,reopened=True,targetContacts=rows,accepted=False,published=False),indent=2))
print('R515_OK',rows)

