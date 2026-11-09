import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from collections import Counter
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R561_SUR_ZEMIN_TEMAS_AO_BAKE_ADAY_v001.blend'));D=json.loads((R/'reports/R569_WALL_DESIGN.json').read_text());c=D['coefficients'];a,b,k=D['facePlane'];xy=[];lookup={}
def z(x,y):return c[0]+c[1]*(x-49.5)+c[2]*(y+58)+c[3]*max(x-54,0)+c[4]*max(x-56,0)
def front(x):return(a*x+b*z(x,0)+k)/(1-b*c[2])
def ix(p):
 p=tuple(round(v,6)for v in p)
 if p not in lookup:lookup[p]=len(xy);xy.append(p)
 return lookup[p]
fs=[tuple(ix(p)for p in t)for t in D['triangles']];n=len(xy);vs=[(x,y,z(x,y))for x,y in xy]
for x,y in xy:
 bx,by=x,y
 if abs(y-front(x))<1e-4:by=a*x+b*-9+k
 elif abs(x-49.5)<1e-5 and y>=-57.5001:bx=x+.2*(-9-z(x,y))
 vs.append((bx,by,-9))
edges=Counter(tuple(sorted((f[i],f[(i+1)%3])))for f in fs for i in range(3));faces=fs+[tuple(i+n for i in reversed(f))for f in fs]+[(u,v,v+n,u+n)for(u,v),ct in edges.items()if ct==1]
checks=[]
mat=bpy.data.materials['R554_WEATHERED_COURSED_STONE_CC0_R561_AO'].copy();mat.name='R554_WEATHERED_COURSED_STONE_CC0'
for nd in list(mat.node_tree.nodes):
 if nd.type=='GROUP' and nd.node_tree and nd.node_tree.name.startswith('glTF Material Output R561'):mat.node_tree.nodes.remove(nd)

def replace(o,verts,faces):
 me=bpy.data.meshes.new(o.name+'_R569');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));q=dict(name=o.name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces),signedVolume=bm.calc_volume(signed=True));assert not q['nonManifold']and not q['zeroArea']and q['signedVolume']>0,q;bm.to_mesh(me);bm.free();o.data=me;me.materials.append(bpy.data.materials['R554_WEATHERED_COURSED_STONE_CC0']);me.uv_layers.new(name='R554_STONE_METRIC_2_5M');me.uv_layers.new(name='R556_STONE_ATLAS_20x10')
 for f in me.polygons:
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;u,w=(v.x,v.y)if abs(f.normal.z)>.6 else(v.y,v.z)if abs(f.normal.x)>.7 else(v.x,v.z);me.uv_layers['R554_STONE_METRIC_2_5M'].data[li].uv=(u/2.5,w/2.5);me.uv_layers['R556_STONE_ATLAS_20x10'].data[li].uv=(u/20,w/10)
 checks.append(q);o['R569_source']='Independent continuous L-shaped masonry body and closed cap planes; R569_WALL_DESIGN.Measured source cells, withheld RMS0.0584m/max0.1053m. Return batter/thickness provisional, no scan mesh reused.'
o=bpy.data.objects['R494_SOUTH_PAVILION_OUTER_RETAINING_WALL'];replace(o,vs,faces)
ret=bpy.data.objects['R495_SOUTH_OUTER_WALL_EAST_RETURN'];rv=[tuple(v.co)for v in ret.data.vertices];x=72.13087;yf=front(x);rv[:4]=[(x,a*x+b*-9+k,-9),(x,yf+2,-9),(x,yf+2,z(x,yf+2)),(x,yf,z(x,yf))];rf=[tuple(p.vertices)for p in ret.data.polygons];replace(ret,rv,rf)
# Restore the actual lower paved strip exposed by narrowing the over-wide old cap.
xy=[];lookup={};fs=[tuple(ix(p)for p in t)for t in D['floorTriangles']];n=len(xy);cf=json.loads((R/'reports/R532_WHOLE_PAVING_PLANES.json').read_text())['coefficients']
def floorz(x,y):return sum(a*b for a,b in zip(cf,[1,x-60,y+45,max(x-58,0),max(x-72,0),max(y+42,0)]))
vs=[(x,y,floorz(x,y)+dz)for dz in (0,-.18)for x,y in xy];ed=Counter(tuple(sorted((f[i],f[(i+1)%3])))for f in fs for i in range(3));faces=fs+[tuple(i+n for i in reversed(f))for f in fs]+[(u,v,v+n,u+n)for(u,v),ct in ed.items()if ct==1]
me=bpy.data.meshes.new('R569_SOUTH_CAP_INNER_PAVED_FLOOR');ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);replace(ob,vs,faces);ob.data.materials.clear();ob.data.materials.append(bpy.data.materials['R457_LOADING_COURT_MINERAL']);uv=ob.data.uv_layers.new(name='R497_MINERAL_METRIC')
for l in ob.data.loops:
 p=ob.data.vertices[l.vertex_index].co;uv.data[l.index].uv=(p.x/3,p.y/3)
ob['source']='Independent extension of R532 measured paving planes into6.0525m2 exposed by cap-width correction. No scan surface copied.'
out=R/'scenes/MUDAM_R569_GUNEY_SUR_TAM_DONUS_KAPALI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));left=bpy.data.objects['R494_SOUTH_PAVILION_OUTER_RETAINING_WALL'];right=bpy.data.objects['R495_SOUTH_OUTER_WALL_EAST_RETURN'];gap=max(min((v.co-right.data.vertices[i].co).length for v in left.data.vertices)for i in range(4));assert gap<1e-4,gap
(R/'reports/R569_BUILD.json').write_text(json.dumps(dict(checks=checks,reopened=True,sharedEastJunctionGap=gap,accepted=False,published=False,aoNeedsRebakeForChangedWalls=True,restoredPavedArea=D['floorArea'],source='R569_WALL_DESIGN.json'),indent=2));print('R569_SAVED',checks,gap,flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=700;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(31,-76,18));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((55,-56,-2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=40;s.render.filepath=str(R/'renders/qa/R569_south_return_candidate.png');bpy.ops.render.render(write_still=True)
