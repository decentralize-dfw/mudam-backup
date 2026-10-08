"""Saved-scene R11 solid, roof corner, transparency and passage checks."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R11_build_report.json').read_text());P=json.loads((B/'config/east_end_glazing.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*x+ox;v=k*y+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 bm.free();ob.to_mesh_clear()
visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
def ray(p,q):
 d=(q-p).normalized();hits=[]
 for ob in visible:
  iv=ob.matrix_world.inverted();ok,loc,no,ix=ob.ray_cast(iv@p,iv.to_3x3()@d,distance=(q-p).length)
  if ok:hits.append(ob.name)
 return hits
passage=[]
for y in [269,279,289]:
 for z in [.2,1.5,2.1]:
  hits=ray(point(287,y,z),point(292,y,z));row=dict(y=y,z=z,hits=hits);passage.append(row)
  if hits:fail.append(row)
joins=[]
for z,y in [(r['roof_low_z'],161.5),(r['roof_high_z'],266.5)]:
 p=point(289.5,y,z);roof=bpy.data.objects['P06_EAST_GLAZED_ROOF'];wall=bpy.data.objects['R11_STONE_END'];row=dict(y=y,z=z,roof_error=min((roof.matrix_world@v.co-p).length for v in roof.data.vertices),wall_error=min((wall.matrix_world@v.co-p).length for v in wall.data.vertices));joins.append(row)
 if max(row['roof_error'],row['wall_error'])>1e-4:fail.append(row)
glass=[]
for name in r['panels']:
 ob=bpy.data.objects[name];value=ob.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value;glass.append(dict(name=name,transmission=value))
 if value<.9:fail.append(glass[-1])
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,link_passage=passage,shared_roof_wall_vertices=joins,glass_material=glass,roof_strip_closed=False,construction_acceptance=False);(B/'reports/R11_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
