from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R96_build_report.json').read_text());old=json.loads((B/'reports/R95_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=r['upper_z'];results={};fail=[]
def pt(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
probes=[]
for x in [836,840,844]:
 for z in [UP+.5,UP+1.5,UP+2.5]:probes.append(dict(id='room_old_y_wall',p=pt(x,356,z),n=(pt(0,1)-pt(0,0)).normalized(),expected=False))
for y in [362,366,370]:
 for z in [UP+.5,UP+1.5,UP+2.5]:probes.append(dict(id='room_old_x_wall',p=pt(862.5,y,z),n=(pt(1,0)-pt(0,0)).normalized(),expected=False))
for x,y,axis in [(840,356,1),(862.5,378,0)]:probes.append(dict(id='ground_preserved',p=pt(x,y,2),n=(pt(1-axis,axis)-pt(0,0)).normalized(),expected=True))
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or not o.visible_get():continue
  eo=o.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
  for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(o.name)
  eo.to_mesh_clear()
 t=BVHTree.FromPolygons(vs,fs,epsilon=.00001);rows=[]
 for p in probes:
  hit=t.ray_cast(p['p']+p['n']*.3,-p['n'],.6);ok=(hit[0] is not None)==p['expected'];rows.append(dict(id=p['id'],point=list(p['p']),hit=None if hit[0] is None else owners[hit[2]],passed=ok))
 if phase=='after':
  for p in old['probes']:
   a=Vector(p['point']);n=Vector(p['normal']);hit=t.ray_cast(a+n*.7,-n,1.4);rows.append(dict(id='R95_'+p['issue'],passed=(hit[0] is not None)==(p['expected']=='closed')))
  for f in old['glazed_surfaces']:
   ps=[Vector(p) for p in f['vertices']];a=sum(ps,Vector())/len(ps);n=Vector(f['normal']);rows.append(dict(id='R95_glass',passed=t.ray_cast(a+n*.15,-n,.3)[0] is not None))
  # Source room floor and ceiling must cover occupied points; stair well must stay open.
  for x,y in [(635,615),(650,635),(675,642),(704,645),(694,660)]:
   for z,label in [(UP,'floor'),(UP+2.7,'ceiling')]:
    a=pt(x,y,z);hit=t.ray_cast(a+Vector((0,0,.25)),Vector((0,0,-1)),.5);rows.append(dict(id='documentation_'+label,point=list(a),passed=hit[0] is not None))
  a=pt(651,677,UP);rows.append(dict(id='service_stair_void',passed=t.ray_cast(a+Vector((0,0,.1)),Vector((0,0,-1)),.2)[0] is None))
  for name in r['closed_objects']+r['changed_inherited_objects']:
   ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);ok=all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.free();rows.append(dict(id=name,passed=ok))
  for name in ['P05_GALLERY_HALL_WEST2','R14_GALLERY_WALL_RETAINED']:
   z=max((bpy.data.objects[name].matrix_world@v.co).z for v in bpy.data.objects[name].data.vertices);rows.append(dict(id=name+'_top',passed=abs(z-(UP-.2))<1e-4))
  fail.extend(x for x in rows if not x['passed'])
 results[phase]=rows
q=dict(file=r['file'],results=results,before_intrusion_failures=sum(not x['passed'] for x in results['before']),failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R96_verification.json').write_text(json.dumps(q,indent=2));print('R96',q['before_intrusion_failures'],'old failures;',len(fail),'new failures',fail);assert not fail
