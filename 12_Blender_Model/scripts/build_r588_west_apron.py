import bpy,bmesh,json,hashlib,numpy as np
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R585_DOGU_HENDEK_CIFT_ZEMIN_TEMIZ_ADAY_v001.blend'))
d=json.loads((R/'reports/R588_WEST_JUNCTION_DESIGN.json').read_text())
def sig(o):
 a=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',a);b=np.empty(len(o.data.loops),dtype=np.int32);o.data.loops.foreach_get('vertex_index',b);return hashlib.sha256(a.tobytes()+b.tobytes()+str((o.matrix_world,o.hide_render)).encode()).hexdigest()
def clean(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
def check(o):
 bm=bmesh.new();bm.from_mesh(o.data);c=dict(name=o.name,vertices=len(bm.verts),faces=len(bm.faces),nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();return c
before={o.name:sig(o)for o in bpy.context.scene.objects if o.type=='MESH'}
terr=bpy.data.objects['R322_WEST_MUSEUM_TERRACE'];terr.data.calc_loop_triangles();bv=BVHTree.FromPolygons([terr.matrix_world@v.co for v in terr.data.vertices],[list(t.vertices)for t in terr.data.loop_triangles],all_triangles=True)
wall=bpy.data.objects['R321_MUSEUM_WEST_MOAT_RETAINING'];wall.data.calc_loop_triangles();wbv=BVHTree.FromPolygons([wall.matrix_world@v.co for v in wall.data.vertices],[list(t.vertices)for t in wall.data.loop_triangles],all_triangles=True)
materials=[]
for obname,label in [('R321_MUSEUM_WEST_MOAT_RETAINING','STONE'),('R322_WEST_MUSEUM_TERRACE','EARTH')]:
 mat=bpy.data.objects[obname].data.materials[0].copy();mat.name='R588_WEST_'+label+'_NO_STALE_AO'
 for nd in list(mat.node_tree.nodes):
  if nd.type=='GROUP' and nd.node_tree and 'glTF Material Output' in nd.node_tree.name:mat.node_tree.nodes.remove(nd)
 materials.append(mat)
g=d['grades'];ec=np.linalg.solve(np.array([[-43.25,16,1],[-43,17,1],[-44,14,1]]),np.array([-3.459694,-3.543182,-3.33195]))
def clamp(t):return max(0,min(1,t))
def plane(c,x,y):return c[0]*x+c[1]*y+c[2]
def intersection(a,b,y):return ((b[1]-a[1])*y+b[2]-a[2])/(a[0]-b[0])
def height(x,y):
 so,sb,si=[g[k]for k in ['southOuter','southBand','southInner']]
 south=plane(so,x,y)if x<intersection(so,sb,y)else min(plane(sb,x,y),plane(si,x,y))
 no,nb,nw,ne=[g[k]for k in ['northOuter','northBand','northWest','northEast']]
 ob=intersection(no,nb,min(y,13.5))
 band=plane(nb,x,y)if y<=13.5 else plane(no,ob,y)+(nb[0]+(.55-nb[0])*clamp((y-13.5)/.5))*(x-ob)
 outer=plane(no,x,y);upper=min(plane(nw,x,y),plane(ne,x,y))
 north=outer if x<intersection(no,nb,min(y,13.5)) else min(band,upper)
 t=clamp((y-9.5)/2.5);z=south*(1-t)+north*t
 front=min(plane(g['front'],x,y),plane(g['frontWest'],x,y));t=clamp((5-y)/1.5);z=z*(1-t)+front*t
 t=clamp((x+44.5)/1.25)*clamp((y-14.5)/1.5);z=z*(1-t)+plane(ec,x,y)*t
 if x>-35.2:
  hits=[v.z for tree in [bv,wbv] if (v:=tree.ray_cast(Vector((d['cutX']+.001,y,30)),Vector((0,0,-1)),60)[0])]
  if hits:t=clamp((x+35.2)/(d['cutX']+35.2));z=z*(1-t)+max(hits)*t
 return z
xy=[];lookup={};top=[];topm=[]
def ix(p):
 p=tuple(round(v,6)for v in p)
 if p not in lookup:lookup[p]=len(xy);xy.append(p)
 return lookup[p]
for part in d['parts']:
 for t in part['triangles']:top.append(tuple(ix(p)for p in t));topm.append(0 if part['name']=='outer'else 1)
n=len(xy);vs=[(x,y,height(x,y))for x,y in xy];edges=Counter(tuple(sorted((f[i],f[(i+1)%3])))for f in top for i in range(3));assert max(edges.values())<=2
boundary_edges=[(a,b)for(a,b),ct in edges.items()if ct==1];adj={}
for a,b in boundary_edges:adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
assert all(len(v)==2 for v in adj.values())
loop=[boundary_edges[0][0]];last=None;cur=loop[0]
while True:
 nxt=next(v for v in adj[cur]if v!=last)
 if nxt==loop[0]:break
 loop.append(nxt);last,cur=cur,nxt
assert len(loop)==len(boundary_edges)
outline=d['outerEdge'];betas=d.get('wallBatter',[.335,.335,.335,.335,.22,.159,.06,.04,0,0]);bottom=[];wall_offsets=[]
for idx in loop:
 x,y,z=vs[idx];rows=[];distances=[];crest_deltas=[]
 for k,(a,b)in enumerate(zip(outline,outline[1:])):
  a=np.array(a);b=np.array(b);p=np.array([x,y]);v=b-a;t=float(np.dot(p-a,v)/np.dot(v,v));nearest=a+max(0,min(1,t))*v
  if np.linalg.norm(p-nearest)<1e-4:
   unit=v/np.linalg.norm(v);rows.append([unit[1],-unit[0]]);refz=height(float((a[0]+b[0])/2),float((a[1]+b[1])/2));distances.append(betas[k]*(refz+10.5));crest_deltas.append(betas[k]*(refz-z))
 delta=np.zeros(2)
 if rows and min(np.linalg.norm(np.array([x,y])-np.array(end))for end in [outline[0],outline[-1]])>1e-4:
  crest_delta=np.linalg.lstsq(np.array(rows),np.array(crest_deltas),rcond=None)[0]
  if np.linalg.norm(crest_delta)>.3:crest_delta*=.3/np.linalg.norm(crest_delta)
  vs[idx]=(x+float(crest_delta[0]),y+float(crest_delta[1]),z)
  delta=np.linalg.lstsq(np.array(rows),np.array(distances),rcond=None)[0]
  limit=2*max(distances,default=0)
  if np.linalg.norm(delta)>limit and limit>0:
   nr=np.mean(np.array(rows),axis=0);delta=nr/np.linalg.norm(nr)*np.mean(distances)
 bottom.append(Vector((x+float(delta[0]),y+float(delta[1]),-10.5)));wall_offsets.append(dict(top=[x,y,z],base=list(bottom[-1]),displacement=float(np.linalg.norm(delta))))
bmap={tuple(round(v,7)for v in p):n+i for i,p in enumerate(bottom)};btris=tessellate_polygon([bottom]);vs+=list(bottom)
faces=top+[tuple(n+p if isinstance(p,int) else bmap[tuple(round(v,7)for v in p)] for p in reversed(tri))for tri in btris]+[(loop[i],loop[(i+1)%len(loop)],n+(i+1)%len(loop),n+i)for i in range(len(loop))]
(R/'reports/R588_WALL_BASE_DESIGN.json').write_text(json.dumps(dict(outline=d['outerEdge'],batter=betas,basePlan=[list(p)for p in bottom],offsets=wall_offsets,foundation='Technical closure at inherited -10.5m, not a measured foundation; exposed western batter measured, occluded continuations inferred.'),indent=2))
me=bpy.data.meshes.new('R588_WEST_APRON_AND_RETAINING_BODY');me.from_pydata(vs,[],faces);me.update()
for mat in materials:me.materials.append(mat)
for f,mi in zip(me.polygons,topm):f.material_index=mi
o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);clean(o)
o['source']=d['scope'];o['level_id']='SITE';o['grade_uncertainty']='Source-fit exposed grade only; occluded wall toes and substrate are not survey measurements.'
for un,scale in [('UVMap',(2.5,2.5)),('R554_STONE_METRIC_2_5M',(2.5,2.5)),('R556_STONE_ATLAS_20x10',(20,10)),('R545_GROUND_ATLAS',(160,180)),('R545_MICRO_2M',(2,2))]:
 uv=me.uv_layers.new(name=un)
 for f in me.polygons:
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co
   if un=='R545_GROUND_ATLAS':uv.data[li].uv=((v.x+80)/160,(v.y+85)/180)
   else:
    u,w=(v.x,v.y)if abs(f.normal.z)>.5 else((v.x if abs(f.normal.y)>.5 else v.y),v.z);uv.data[li].uv=(u/scale[0],w/scale[1])
checks=[check(o)];assert checks[-1]['nonManifold']==checks[-1]['zeroArea']==0,checks[-1]
for name in ['R557_WEST_APPROACH_0','R557_WEST_APPROACH_1']:bpy.data.objects[name].hide_render=True;bpy.data.objects[name].hide_set(True)
bpy.ops.mesh.primitive_cube_add(size=1,location=((d['cutX']-200)/2,0,0));cutter=bpy.context.object;cutter.dimensions=(d['cutX']+200,400,100);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
changednames=['R322_WEST_MUSEUM_TERRACE','R321_MUSEUM_WEST_MOAT_RETAINING','R152_HISTORIC_WALL_759680904','R490_NW_MINERAL_PASSAGE']
for name in changednames:
 o=bpy.data.objects[name];mod=o.modifiers.new('R588_COMPLETE_WEST_REPLACEMENT','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=bpy.data.objects['R588_WEST_APRON_AND_RETAINING_BODY']if name=='R490_NW_MINERAL_PASSAGE'else cutter;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);clean(o);checks.append(check(o))
bpy.data.objects.remove(cutter,do_unlink=True)
assert all(c['nonManifold']==c['zeroArea']==0 for c in checks),checks
out=R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v008.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
after={o.name:sig(o)for o in bpy.context.scene.objects if o.type=='MESH'};changed=[k for k in before if before[k]!=after.get(k)];assert set(changed)<=set(changednames+['R557_WEST_APPROACH_0','R557_WEST_APPROACH_1']),changed
checks=[check(bpy.data.objects[c['name']])for c in checks];assert all(c['nonManifold']==c['zeroArea']==0 for c in checks),checks
probes=[];dg=bpy.context.evaluated_depsgraph_get()
for x,y in [(-50,12),(-49,13),(-47,14),(-49,15),(-45.7,8),(-43.8,6.48),(-38.86,4.96),(-47,12),(-44,14),(-43.25,16),(-43,17)]:
 h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,15)),Vector((0,0,-1)),distance=35);probes.append(dict(x=x,y=y,z=p.z if h else None,obj=o.name if h else None))
(R/'reports/R588_BUILD.json').write_text(json.dumps(dict(sourceScene=str(out),reopened=True,checks=checks,changed=changed,unchanged=len(before)-len(changed),added=[k for k in after if k not in before],probes=probes,accepted=False,published=False),indent=2));print('R588_CHECK',checks,probes,flush=True)
s=bpy.context.scene
for o in s.objects:
 if o.name.startswith('R158_TREE_'):o.hide_render=True
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-62,-19,39));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-35,5,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=56;s.render.filepath=str(R/'renders/qa/R588_west_v008.png');bpy.ops.render.render(write_still=True)
s.camera.location=(-40,8,65);s.camera.rotation_euler=(0,0,0);s.camera.data.ortho_scale=38;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(R/'renders/qa/R588_west_top_v008.png');bpy.ops.render.render(write_still=True)
