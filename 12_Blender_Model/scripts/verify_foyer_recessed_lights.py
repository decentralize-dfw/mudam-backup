"""Reopen R69 and check recesses, support and closed fixture parts."""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R69_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();trees={};solids=[];fail=[];rays=[]
for name in r['closed_objects']+r['changed_inherited_objects']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);q=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces),volume=bm.calc_volume(signed=True));bm.free();trees[name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);ob.to_mesh_clear();solids.append(q)
 if q['nonmanifold'] or q['zero_faces'] or q['volume']<=0:fail.append(q)
def ray(label,c,offset,expected,z):
 start=Vector((c[0]+offset[0],c[1]+offset[1],c[2]-.30));hits=[]
 for name,tree in trees.items():
  p,n,i,d=tree.ray_cast(start,Vector((0,0,1)),.6)
  if p is not None:hits.append((d,name,p.z))
 hit=min(hits) if hits else None;ok=hit is not None and hit[1]==expected and abs(hit[2]-z)<2e-5;row=dict(label=label,hit=hit,expected=expected,expected_z=z,passed=ok);rays.append(row)
 if not ok:fail.append(row)
for f in r['fixtures']:
 c=f['center'];ray(f['id']+'_center',c,(0,0),f['lens'],c[2]+.064)
 for i in range(8):
  a=i*math.tau/8;ray(f['id']+f'_rim_{i}',c,(.078*math.cos(a),.078*math.sin(a)),f['rim'],c[2]-.004);ray(f['id']+f'_soffit_{i}',c,(.11*math.cos(a),.11*math.sin(a)),'R06_FOYER_CEILING_AND_CURVED_FASCIA',c[2])
result=dict(file=r['file'],solids=solids,rays=rays,failures=fail,construction_acceptance=False,limits='Recess and mesh checks do not validate candidate fixture placement or actual fixture dimensions.');(B/'reports/R69_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R69 solids',len(solids),'rays',len(rays),'failures',len(fail));assert not fail,fail
