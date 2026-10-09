"""R101 missing source-drawn sides of the reading/east-room passage."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];prior=json.loads((B/'reports/R100_build_report.json').read_text());P=json.loads((B/'reports/R96_build_report.json').read_text());Q=json.loads((B/'config/reading_room.json').read_text());UP=P['upper_z'];TOP=UP+2.7
out=B/'scenes/MUDAM_R101_OKUMA_SERVIS_GECIDI_YAN_DUVARLAR_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B.parent/prior['file']));root=bpy.data.collections.new('R101_READING_EAST_LINK');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[]
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
# R96 omitted room edges9 and11. Edge10 is the doorway and must remain open.
# North side stops at the existing R96 north join, rather than duplicating it.
x0=Q['room_inner_polygon'][2][0];t=.3/C['meters_per_canonical_pixel']
specs=[dict(name='R101_PASSAGE_NORTH_SIDE',x0=x0,x1=619.65,y0=632.33-t,y1=632.33),dict(name='R101_PASSAGE_SOUTH_SIDE',x0=x0,x1=623.77,y0=647.58,y1=647.58+t)]
for s in specs:
 vs=[pt(x,y,z) for z in [UP,TOP] for x,y in [(s['x0'],s['y0']),(s['x1'],s['y0']),(s['x1'],s['y1']),(s['x0'],s['y1'])]];me=bpy.data.meshes.new(s['name']);me.from_pydata(vs,[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(s['name'],me);root.objects.link(ob);me.materials.append(bpy.data.materials['P05_NEUTRAL_ENVELOPE'])
 for key,val in dict(element_id=s['name'],element_type='source_upper_passage_side_wall',level_id='LP1',source_ids='PDF2016_page5,103',status='source_topology_candidate_dimensions',assumption_note='Missing side edges from the existing source room polygon. Reading-room fit and north solid join retained.300mm thickness and2.7m height unmeasured. Doorway remains open.').items():ob[key]=val
 made.append(ob.name)
r=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(prior['file']).name,closed_objects=made,changed_inherited_objects=[],upper_z=UP,top_z=TOP,side_specs=specs,construction_acceptance=False,limits=['Source2016 east reading passage side edges9/11 restored; entrance edge10 remains open.','Existing room registration,300mm wall thickness and2.7m clear height are conditional; not measured construction detail.','Only this source-supported connection accepted; other marked upper-floor boundaries remain under review.']);bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R101 reading east passage side boundaries';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R101_build_report.json').write_text(json.dumps(r,indent=2));print('R101',made)
