from pathlib import Path
import bpy,json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R122_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));out=B/'scenes/MUDAM_R123_CATI_YINELENEN_PROFILLER_v001.blend';assert not out.exists()
pairs=[('P10_MAIN_ROOF_FACE_4_GRID_0039','P10_MAIN_ROOF_FACE_4_GRID_0025'),('P10_MAIN_ROOF_FACE_4_GRID_0042','P10_MAIN_ROOF_FACE_4_GRID_0036')];checks=[]
def sig(o):
 dep=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(dep);m=eo.to_mesh();vs=[tuple(round(c,4) for c in eo.matrix_world@v.co) for v in m.vertices];faces=sorted(tuple(sorted(vs[i] for i in f.vertices)) for f in m.polygons);mats=[x.name if x else None for x in m.materials];eo.to_mesh_clear();return faces,mats
for name,keep in pairs:
 o=bpy.data.objects[name];k=bpy.data.objects[keep];assert sig(o)==sig(k),(name,keep)
 pts=[o.matrix_world@v.co for v in o.data.vertices];checks.append(dict(removed=name,retained=keep,bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)],evaluated_faces_and_materials_identical_at_0_1mm_rounding=True));o.hide_render=True;o.hide_set(True);o['R123_note']='Coincident evaluated profile within 0.1 mm rounding retained at same position; duplicate hidden, original mesh preserved.'
q=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(r['file']).name,closed_objects=[],changed_inherited_objects=[p[0] for p in pairs],duplicate_pairs=checks,source_ids=['P10','R93'],construction_acceptance=False,visual_acceptance=False,limits=['No new geometry or architectural dimensions. Two exact duplicates removed from display; retained profiles unchanged.'])
bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R123_build_report.json').write_text(json.dumps(q,indent=2));print(checks)
