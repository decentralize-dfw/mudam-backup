"""R109 join existing R33 wall ends at shared source centerline corners.

No new boundary, opening, wall height or wall thickness is inferred.
"""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
B=Path(__file__).resolve().parents[1]
P=json.loads((B/'config/ground_service_rooms.json').read_text())
C=json.loads((B/'config/foundation.json').read_text())['calibration']
base=json.loads((B/'reports/R108_build_report.json').read_text())
out=B/'scenes/MUDAM_R109_SERVIS_MERDIVEN_ALTI_KOSELERI_v001.blend'
assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B.parent/base['file']))
up=Vector((0,0,1));groups={};before={};joints=[]
def pt(p):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
def cross(a,b):return a.x*b.y-a.y*b.x
for name,ends in P['walls'].items():
 if not name.startswith(('SERVICE_W_',)):continue
 for i,p in enumerate(ends):groups.setdefault(tuple(p),[]).append((name,i,pt(ends[1-i])-pt(p)))
for coord,parts in groups.items():
 if len(parts)!=2:continue
 p=pt(coord);axes=[part[2].normalized() for part in parts];normals=[up.cross(a) for a in axes];den=cross(*axes)
 if abs(den)<1e-5:continue
 half=P['wall_thickness_m']/2;corners=[]
 for sign in [-1,1]:
  a=p+normals[0]*half*sign;b=p-normals[1]*half*sign
  m=a+axes[0]*cross(b-a,axes[1])/den
  assert (m-p).length<.4
  corners.append(dict(old=[list(a),list(b)],miter=list(m)))
  for part,old in zip(parts,[a,b]):
   ob=bpy.data.objects['R33_WALL_'+part[0]]
   indices=[v.index for v in ob.data.vertices if ((ob.matrix_world@v.co).xy-old.xy).length<3e-5]
   assert len(indices)>=2,(ob.name,indices)
   if ob.name not in before:before[ob.name]=[list(ob.matrix_world@v.co) for v in ob.data.vertices];ob.data=ob.data.copy()
   inv=ob.matrix_world.inverted()
   for i in indices:
    q=ob.matrix_world@ob.data.vertices[i].co;ob.data.vertices[i].co=inv@Vector((m.x,m.y,q.z))
   ob['R109_note']='Existing source centerline and wall planes preserved; two end faces mitered at shared source corner. Dimensions remain conditional.'
  joints.append(dict(source_corner=list(coord),center=list(p),parts=['R33_WALL_'+x[0] for x in parts],corners=corners)) if sign==1 else None
for name in before:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
changed=sorted(before)
r=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(base['file']).name,closed_objects=changed,changed_inherited_objects=changed,joints=joints,before_world_vertices=before,source_ids=['102','PDF2016'],construction_acceptance=False,limits=['Existing R33 source centerlines, wall planes, heights and thickness retained.','Only exact shared endpoints in ground service-stair walls are joined; no doorway endpoint extended.','Miter geometry reconciles continuous source walls; hidden construction and exact thickness are unknown.'])
bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R109 ground service wall corner miters'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R109_build_report.json').write_text(json.dumps(r,indent=2))
print('R109',len(changed),'walls',len(joints),'corners')
