"""R07 flat wall, miter, and visible scene approach checks."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R07_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();C=json.loads((B/'config/foundation.json').read_text())['calibration'];fail=[];solids=[];approach=[];floor_edges=[]
def point(p,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
def ray(ob,p,d,length):
 inv=ob.matrix_world.inverted();hit,loc,_,_=ob.ray_cast(inv@p,inv.to_3x3()@d,distance=length);return (ob.matrix_world@loc-p).length if hit else None
for definition in r['wall_definitions']:
 name=definition['name'];ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();ob.to_mesh_clear();solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 a,b=map(point,definition['inner_edge_canonical']);normal=(point([650,375])-(a+b)/2);t=(b-a).normalized();normal=(normal-t*normal.dot(t)).normalized()
 for f in [.1,.3,.5,.7,.9]:
  p=a.lerp(b,f);top=definition['top_heights'][0]*(1-f)+definition['top_heights'][1]*f
  for z in [definition['bottom']+1,1.5,top-.2]:
   p.z=z;origin=p+normal*.35;hits=[]
   for other in visible:
    d=ray(other,origin,-normal,.7)
    if d is not None:hits.append([d,other.name])
   hits.sort();ok=bool(hits) and hits[0][1]==name and abs(hits[0][0]-.35)<1e-4;approach.append(dict(wall=name,fraction=f,z=z,hits=hits[:2],passed=ok))
   if not ok:fail.append(approach[-1])
  p.z=definition['bottom']+.1;base=bpy.data.objects['P05_ZONE_LM1_GALLERIES_FOYER'].evaluated_get(deps);d=ray(base,p+normal*.2,Vector((0,0,-1)),.2);floor_edges.append(dict(wall=name,fraction=f,offset_inside_m=.2,has_lower_floor=d is not None))
# Both miter surfaces must share the same four corner edge coordinates.
one=bpy.data.objects[r['closed_objects'][0]];two=bpy.data.objects[r['closed_objects'][1]];shared=[]
for v in one.data.vertices:
 if any((one.matrix_world@v.co-two.matrix_world@w.co).length<1e-5 for w in two.data.vertices):shared.append(list(v.co))
if len(shared)!=4:fail.append(dict(test='wall_miter',shared_vertices=len(shared)))
assert all(bpy.data.objects[n].hide_render for n in r['hidden_superseded_objects'])
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,wall_approach_rays=approach,miter_shared_vertices=shared,basement_floor_edge_observations=floor_edges,construction_acceptance=False);(B/'reports/R07_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(failures=fail,solids=solids,floor_edges=floor_edges),indent=2));assert not fail,fail
