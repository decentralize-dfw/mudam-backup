"""Read-only evaluated scene audit. Open study surfaces are recorded, not silently accepted."""
from pathlib import Path
import bpy,bmesh,json,math,sys
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(Path(__file__).parent));from release_utils import verified_current_scene
r=verified_current_scene();output_name='R44_global_audit_before.json'
if '--' in sys.argv:
 args=sys.argv[sys.argv.index('--')+1:];assert len(args)==2;r=json.loads((B/'reports'/args[0]).read_text());output_name=args[1]
bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();rows=[];bad=[];open_surfaces=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me);bounds=sum(e.is_boundary for e in bm.edges);nonman=sum(not e.is_manifold for e in bm.edges);zero=[f.index for f in bm.faces if f.calc_area()<1e-10];loose=sum(not e.link_faces for e in bm.edges);inconsistent=sum(e.is_manifold and not e.is_contiguous for e in bm.edges);volume=bm.calc_volume(signed=True);finite=all(math.isfinite(x) for v in me.vertices for x in eo.matrix_world@v.co);no_material=sum(f.material_index>=len(me.materials) or me.materials[f.material_index] is None for f in me.polygons);row=dict(name=ob.name,kind=ob.get('element_type','unknown'),vertices=len(me.vertices),faces=len(me.polygons),boundary_edges=bounds,nonmanifold_edges=nonman,zero_area_faces=zero,loose_edges=loose,inconsistent_edges=inconsistent,volume_m3=volume,finite=finite,faces_without_material=no_material,source_ids=ob.get('source_ids',''),status=ob.get('status',''))
 rows.append(row)
 if zero or loose or inconsistent or not finite or no_material or (nonman==0 and volume<=0):bad.append(row)
 if nonman:open_surfaces.append(row)
 bm.free();eo.to_mesh_clear()
result=dict(file=r['file'],visible_mesh_count=len(rows),objects=rows,numerical_findings=bad,open_or_nonmanifold_objects=open_surfaces,failures=bad+open_surfaces,architectural_acceptance=False,notes=['Read-only whole-scene audit; source/measurement validity is independent.','Open reference/envelope surfaces are reported explicitly; this audit does not certify a watertight building or collision model.']);(B/'reports'/output_name).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(visible=len(rows),numerical_findings=len(bad),open_objects=len(open_surfaces),bad=[dict(name=x['name'],zero=len(x['zero_area_faces']),inconsistent=x['inconsistent_edges'],loose=x['loose_edges'],volume=x['volume_m3']) for x in bad]),indent=2))
