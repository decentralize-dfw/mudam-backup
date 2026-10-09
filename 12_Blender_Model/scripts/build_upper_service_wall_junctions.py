"""R102 reconcile existing source wall backs at upper service-room corners."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'reports/R96_build_report.json').read_text());base=json.loads((B/'reports/R101_build_report.json').read_text());out=B/'scenes/MUDAM_R102_UST_SERVIS_DUVAR_KOSELERI_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B.parent/base['file']));up=Vector((0,0,1));before={};changed=set();joints=[]
def pt(p):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
def cross(a,b):return a.x*b.y-a.y*b.x
for side,coords,prefix in [('DOCUMENTATION_EAST',P['documentation_east_room'],'R96_DOCUMENTATION_EAST_WALL_'),('SERVICE_STAIR',P['service_stair_boundary'],'R96_SERVICE_STAIR_BOUNDARY_')]:
 poly=list(map(pt,coords))
 for i in range(1,7):
  p=poly[i];ax1=(p-poly[i-1]).normalized();ax2=(poly[i+1]-p).normalized();a=p+up.cross(ax1)*.3;b=p+up.cross(ax2)*.3;den=cross(ax1,ax2);assert abs(den)>1e-5;m=a+ax1*cross(b-a,ax2)/den;assert (m-p).length<1.2;parts=[];bounds=[]
  for edge,old in [(i-1,a),(i,b)]:
   ob=bpy.data.objects[prefix+str(edge)];indices=[v.index for v in ob.data.vertices if Vector(((ob.matrix_world@v.co).x-old.x,(ob.matrix_world@v.co).y-old.y,0)).length<3e-5];assert indices,(ob.name,i)
   if ob.name not in before:before[ob.name]=[list(ob.matrix_world@v.co) for v in ob.data.vertices];ob.data=ob.data.copy()
   inv=ob.matrix_world.inverted()
   for index in indices:
    v=ob.data.vertices[index];q=ob.matrix_world@v.co;v.co=inv@Vector((m.x,m.y,q.z))
   bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob['R102_note']='Existing source-facing polygon retained; adjacent outer wall backs mitered at shared endpoint. Thickness and height unchanged and conditional.';changed.add(ob.name);parts.append(ob.name);zs=[(ob.matrix_world@v.co).z for v in ob.data.vertices];bounds.append([min(zs),max(zs)])
  joints.append(dict(level='LP1' if side=='DOCUMENTATION_EAST' else 'L00_LP1',side=side,corner=i,source_corner=coords[i],inner=list(p),old_back_a=list(a),old_back_b=list(b),shared_back=list(m),parts=parts,z_overlap=[max(x[0] for x in bounds),min(x[1] for x in bounds)]))
r=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(base['file']).name,closed_objects=sorted(changed),changed_inherited_objects=sorted(changed),joints=joints,before_world_vertices=before,construction_acceptance=False,limits=['Existing source2016 room/stair inner traces remain fixed; only outer thickness corners reconciled.','No door, floor, ceiling, stair tread or source height changed. No construction-dimensional acceptance.']);bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R102 upper service wall corner continuity';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R102_build_report.json').write_text(json.dumps(r,indent=2));print('R102',len(changed),'walls',len(joints),'corners')
