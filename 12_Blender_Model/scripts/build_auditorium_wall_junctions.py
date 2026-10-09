"""R75: six stage-recess wall joints, retaining the traced 104 front faces."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R74_STUDIO_DUVAR_BIRLESIMLERI_v003.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R75_ODITORYUM_DUVAR_BIRLESIMLERI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));changed=set();before={};joints=[]
def cross(a,b):return a.x*b.y-a.y*b.x
for i in range(6):
 names=[f'R19_STAGE_BACK_{i}',f'R19_STAGE_BACK_{i+1}'];obs=[bpy.data.objects[n] for n in names];vs=[[o.matrix_world@v.co for v in o.data.vertices] for o in obs];a=vs[0][2].copy();b=vs[1][3].copy();ax1=(vs[0][1]-vs[0][0]).normalized();ax2=(vs[1][1]-vs[1][0]).normalized();den=cross(ax1,ax2);assert abs(den)>1e-5;m=a+ax1*(cross(b-a,ax2)/den);p=vs[0][1].copy();assert (p-vs[1][0]).length<2e-5
 assert (m-p).length<1,'Unexpected miter span'
 for ob,indices in [(obs[0],[2,6]),(obs[1],[3,7])]:
  if ob.name not in before:before[ob.name]=[list(ob.matrix_world@v.co) for v in ob.data.vertices];ob.data=ob.data.copy()
  inv=ob.matrix_world.inverted()
  for index in indices:
   v=ob.data.vertices[index];w=ob.matrix_world@v.co;v.co=inv@Vector((m.x,m.y,w.z))
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();ob['wall_junction_revision']='R75 shared stage-recess back corners; source front fixed';changed.add(ob.name)
 z0=min(v.z for v in vs[0]);z1=max(v.z for v in vs[0])
 joints.append(dict(level='LM1',side='AUDITORIUM',corner=i,inner=[p.x,p.y,0],old_back_a=[a.x,a.y,0],old_back_b=[b.x,b.y,0],shared_back=[m.x,m.y,0],parts=names,z_overlap=[z0,z1]))
report=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=sorted(changed),changed_inherited_objects=sorted(changed),joints=joints,before_world_vertices=before,construction_acceptance=False,limits=['Source104 stage outline and all front faces/heights retained.','200mm wall depth remains inherited candidate; concealed build-up is unknown.','Convex gaps and concave overlaps reconciled at six shared corners.'])
bpy.context.scene['stage']='R75 auditorium stage wall junctions';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R75_SOURCE_AND_LIMITS').write(json.dumps({k:v for k,v in report.items() if k!='before_world_vertices'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R75_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R75',len(changed),'walls',len(joints),'joints')
