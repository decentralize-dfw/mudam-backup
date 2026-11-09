import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R532_GUNEY_TAM_YAYA_ALANI_ADAY_v001.blend'));d=json.loads((R/'reports/R534_RUIN_WALL_DESIGN.json').read_text());old=bpy.data.objects['R152_RUIN_PARTITION_10'];oldBounds=[tuple(old.matrix_world@Vector(p))for p in old.bound_box];mat=old.data.materials[0];line=[Vector(p)for p in d['stations']];vs=[]
for i,p in enumerate(line):
 tangent=line[min(i+1,len(line)-1)]-line[max(0,i-1)];tangent.z=0;tangent.normalize();n=Vector((-tangent.y,tangent.x,0))
 for side,z in [(-1,-4.8),(1,-4.8),(1,p.z),(-1,p.z)]:
  q=p+n*side*.325;vs.append((q.x,q.y,z))
fs=[(3,2,1,0),tuple(range(len(vs)-4,len(vs)))]+[(4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j)for i in range(len(line)-1)for j in range(4)];me=bpy.data.meshes.new('R534_EAST_RUIN_OUTER_WALL');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));ck=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not any(ck.values());bm.to_mesh(me);bm.free();old.data=me;me.materials.append(mat);old['source']='R534 independent complete outer ruin wall, source-traced plan and heldout cap grades. Supersedes old R152 long wall crossing pedestrian route. Hidden base-4.8m and traced0.65mwidth remain modeling bounds.'
for name in ('UVMap','R55_CONTEXT_METRIC_UV','METRIC_UV_4x3m'):
 uv=me.uv_layers.new(name=name)
 for f in me.polygons:
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.y/3)if abs(f.normal.z)>.7 else((v.x if abs(f.normal.y)>.5 else v.y)/4,v.z/3)
out=R/'scenes/MUDAM_R534_DOGU_KALINTI_DIS_DUVAR_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));dg=bpy.context.evaluated_depsgraph_get();hit,p,n,idx,o,m=bpy.context.scene.ray_cast(dg,Vector((59,-46,20)),Vector((0,0,-1)),distance=50);assert hit and o.name.startswith('R532_'),o.name if hit else 'no ground';(R/'reports/R534_BUILD.json').write_text(json.dumps(dict(check=ck,reopened=True,oldBounds=oldBounds,clearedRoadPoint=dict(x=59,y=-46,object=o.name,z=p.z),capChecks=d['fits'],accepted=False,published=False),indent=2));print('R534_SAVED',ck,o.name,p.z,flush=True)
