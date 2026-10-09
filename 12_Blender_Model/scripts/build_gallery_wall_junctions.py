"""R71: miter existing gallery wall backs, retaining every source-facing edge.

No new room boundary, portal, thickness or height is inferred. Only adjacent
offset faces belonging to the same source polygon acquire a shared endpoint.
"""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
C=json.loads((B/'config/foundation.json').read_text())['calibration']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001'
base='MUDAM_R70_GALERI_RAY_SPOT_v003.blend'
out=B/'scenes'/f'MUDAM_R71_GALERI_DUVAR_BIRLESIMLERI_{version}.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
up=Vector((0,0,1));changed=set();joints=[];skipped=[];before={}
def point(p,lower=False):
 x,y=p
 if lower:
  s,dx,dy=C['basement_registration']['source_to_canonical'];x=s*x+dx;y=s*y+dy
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
def cross(a,b):return a.x*b.y-a.y*b.x
def selected(side,edge,lower):
 if lower:
  if side=='E' and edge==1:return ['R29_E_FOYER_DIVIDER']
  return [f'R29_{side}_BOUNDARY_{edge:02d}']
 return [o.name for o in bpy.context.scene.objects if o.name.startswith(f'R23_{side}_{edge}_') and o.get('element_type')=='upper_gallery_finish_wall_candidate']
for lower,config,key in [(False,'upper_gallery_room.json','source_polygons_canonical'),(True,'lower_gallery_rooms.json','rooms')]:
 P=json.loads((B/'config'/config).read_text());th=P['wall_thickness_candidate_m'] if lower else P['wall_display_thickness_m']
 for side,coords in P[key].items():
  poly=[point(p,lower) for p in coords];center=sum(poly,Vector())/len(poly)
  for i,p in enumerate(poly):
   previous=(i-1)%len(poly);following=i;ax1=(p-poly[previous]).normalized();ax2=(poly[(i+1)%len(poly)]-p).normalized()
   n1=ax1.cross(up);n2=ax2.cross(up)
   if n1.dot(p-center)<0:n1=-n1
   if n2.dot(p-center)<0:n2=-n2
   a=p+n1*th;b=p+n2*th;den=cross(ax1,ax2)
   if abs(den)<1e-6:continue
   m=a+ax1*(cross(b-a,ax2)/den)
   assert (m-p).length<4*th,'Unexpected acute miter'
   matches=[]
   for edge,old in [(previous,a),(following,b)]:
    found=[]
    for name in selected(side,edge,lower):
     ob=bpy.data.objects.get(name)
     if ob is None:continue
     indices=[v.index for v in ob.data.vertices if ((ob.matrix_world@v.co)-Vector((old.x,old.y,(ob.matrix_world@v.co).z))).length<2e-5]
     if indices:found.append((ob,indices,old))
    matches.append(found)
   if not all(matches):
    skipped.append(dict(level='LM1' if lower else 'LP1',side=side,corner=i,reason='Intentional doorway/divider termination or inherited different wall; not auto-closed.'));continue
   bounds=[];parts=[]
   for found in matches:
    for ob,indices,old in found:
     if ob.name not in before:
      before[ob.name]=[list(ob.matrix_world@v.co) for v in ob.data.vertices];ob.data=ob.data.copy()
     inv=ob.matrix_world.inverted()
     for index in indices:
      v=ob.data.vertices[index];oldworld=ob.matrix_world@v.co;v.co=inv@Vector((m.x,m.y,oldworld.z))
     ob.data.update();bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
     ob['wall_junction_revision']='R71 shared back-face miter; source-facing edge and openings unchanged'
     changed.add(ob.name);parts.append(ob.name)
     zs=[(ob.matrix_world@v.co).z for v in ob.data.vertices];bounds.append([min(zs),max(zs)])
   joints.append(dict(level='LM1' if lower else 'LP1',side=side,corner=i,source_corner=coords[i],inner=list(p),old_back_a=list(a),old_back_b=list(b),shared_back=list(m),parts=sorted(set(parts)),z_overlap=[max(v[0] for v in bounds),min(v[1] for v in bounds)],thickness_candidate_m=th))
report=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=sorted(changed),changed_inherited_objects=sorted(changed),joints=joints,intentional_unmodified_terminations=skipped,before_world_vertices=before,construction_acceptance=False,limits=['Source-facing gallery footprints, portal jamb positions, heights and inherited thicknesses retained.','Only miter geometry is corrected; thicknesses and basement ceiling remain unmeasured candidates.','Other wall systems require separate audit; this is not whole-building wall completion.'])
bpy.context.scene['stage']='R71 gallery wall junction continuity';bpy.context.scene['current_file']=out.name
bpy.data.texts.new('R71_SOURCE_AND_LIMITS').write(json.dumps({k:v for k,v in report.items() if k!='before_world_vertices'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R71_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('R71',len(changed),'walls;',len(joints),'miter joints;',len(skipped),'intentional terminations retained')
