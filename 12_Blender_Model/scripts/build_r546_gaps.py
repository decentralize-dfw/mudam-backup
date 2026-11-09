import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from collections import Counter
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R545_TERAS_KALE_TOPRAK_MALZEME_ADAY_v001.blend'));d=json.loads((R/'reports/R546_GAP_PLANES.json').read_text());checks=[]
for k,part in enumerate(d):
 xy=[];lookup={}
 def ix(p):
  p=tuple(round(v,6)for v in p)
  if p not in lookup:lookup[p]=len(xy);xy.append(p)
  return lookup[p]
 fs=[tuple(ix(p)for p in t)for t in part['triangles']];n=len(xy);c=part['plane']
 def z(x,y):return c[0]*x+c[1]*y+c[2]+(c[3]*max(x+31.6,0)+c[4]*max(y-3.2,0)if len(c)==5 else 0)
 vs=[(x,y,z(x,y)+dz)for dz in (0,-.18)for x,y in xy];edges=Counter(tuple(sorted((f[i],f[(i+1)%3])))for f in fs for i in range(3));faces=fs+[tuple(i+n for i in reversed(f))for f in fs]+[(a,b,b+n,a+n)for(a,b),ct in edges.items()if ct==1];me=bpy.data.meshes.new('R546_WEST_MOAT_EDGE_'+str(k));me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));ck=dict(name=me.name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert ck['nonManifold']==ck['zeroArea']==0,ck;checks.append(ck);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials['R157_CONTINUOUS_LANDCOVER'])
 for un in ('UVMap','MicroUV'):
  uv=me.uv_layers.new(name=un)
  for l in me.loops:
   p=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((p.x+500)/1150,(p.y+450)/1100)if un=='UVMap'else(p.x/6,p.y/6)
 o['source']='R546 independently fitted ground grades over remaining projected gap footprint. No source scan mesh copied. Wall-crest hits excluded from ground fit.'
out=R/'scenes/MUDAM_R546_BATI_HENDEK_KENAR_BUTUNLUGU_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));dg=bpy.context.evaluated_depsgraph_get();rays=[]
for k,part in enumerate(d):
 for t in part['triangles']:
  x=sum(p[0]for p in t)/3;y=sum(p[1]for p in t)/3;h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,30)),Vector((0,0,-1)),distance=60);assert h,(x,y);rays.append(dict(x=x,y=y,z=p.z,object=o.name))
(R/'reports/R546_BUILD.json').write_text(json.dumps(dict(checks=checks,reopened=True,coverageChecks=rays,accepted=False),indent=2));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=650;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-25,3,50));s.camera=bpy.context.object;s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=27;s.render.filepath=str(R/'renders/qa/R546_west_ground_candidate.png');bpy.ops.render.render(write_still=True)
