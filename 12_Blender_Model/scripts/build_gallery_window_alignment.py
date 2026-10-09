"""R52 conditional glazing along PDF room steps, with photo-checked recesses."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';C=json.loads((B/'config/foundation.json').read_text())['calibration'];Q=json.loads((B/'reports/R27_build_report.json').read_text());base='MUDAM_R51_ANA_CATI_GOLGELIK_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R52_GALERI_CAM_HIZA_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));root=bpy.data.collections.new('R52_WINDOW_ALIGNMENT_TRIAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];up=Vector((0,0,1));a=Vector(Q['origin']);axis=Vector(Q['axis']);inside=Vector(Q['inside']);stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];metal=bpy.data.materials['R14_DARK_COATED_FRAME_CANDIDATE'];glass=bpy.data.materials['P10_GLASS_PREVIEW']
def point(x,y):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*x+ox;v=k*y+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,0))
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);me=bpy.data.meshes.new(name);me.from_pydata([tuple(p+up*z) for z in [z0,z1] for p in poly],[],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='EAST_GALLERY_FRONT',level_id='L00',source_ids='061,062,004,116,PDF2016,102',status='conditional_plan_step_glazing_alignment',assumption_note='PDF floor step constrains back plane; second window width transferred from first. Recess surfaces and exact positions conditional.').items():o[k]=v
 made.append(name);return o
rows=[]
for bay,x0,x1,y in [(2,334.27005932,356.21290312,559.74486845),(4,385.53728687,407.48013067,611.00422358)]:
 left=point(x0,y);right=point(x1,y);u=(right-left).normalized();n=(point(x0,y+1)-left).normalized();w=(right-left).length;fw=.07;depth=.12
 for suffix in ['FRAME_L','FRAME_R','FRAME_B','FRAME_T','GLASS']:
  ob=bpy.data.objects[f'R27_BAY_{bay}_{suffix}'];ob.hide_render=True;ob.hide_set(True);changed.append(ob.name)
 def box(lab,s0,s1,z0,z1,d=depth,mat=metal):return prism(f'R52_BAY_{bay}_{lab}',[left+u*s0-n*.02,left+u*s1-n*.02,left+u*s1+n*(d-.02),left+u*s0+n*(d-.02)],z0,z1,mat,'window_alignment_'+lab.lower()+'_candidate')
 box('FRAME_L',0,fw,.08,3.45);box('FRAME_R',w-fw,w,.08,3.45);box('FRAME_B',0,w,.08,.15);box('FRAME_T',0,w,3.38,3.45);o=box('GLASS',fw,w-fw,.15,3.38,.018,glass)
 op=next(q for q in Q['openings'] if q['index']==bay);frontL=a+axis*op['start']+inside*1.25;frontR=a+axis*op['end']+inside*1.25;poly=[frontL,frontR,right,left];prism(f'R52_BAY_{bay}_THRESHOLD',poly,-.12,.08,stone,'skew_reveal_threshold_candidate');prism(f'R52_BAY_{bay}_SOFFIT',poly,3.45,3.60,stone,'skew_reveal_head_candidate')
 center=sum(poly,Vector())/4
 for lab,p,q in [('LEFT',frontL,left),('RIGHT',frontR,right)]:
  side=up.cross((q-p).normalized())
  if side.dot(center-(p+q)/2)>0:side=-side
  prism(f'R52_BAY_{bay}_RETURN_{lab}',[p,q,q+side*.12,p+side*.12],.08,3.45,stone,'skew_side_return_candidate')
 # Full-height side-box trials created opaque projections unsupported by 062.
 # Trim only the inherited pier volume crossing the skew aperture, preserving
 # its outer profile and avoiding the extra full-height jamb boxes.
 if bay==4:
  void=prism('R52_BAY_4_RECESS_CUTTER',[frontL-inside*1.26,frontR-inside*1.26,right,left],.079,3.451,stone,'hidden_skew_recess_void_candidate');void.hide_render=True;void.hide_set(True);made.remove(void.name)
  for name in ['R27_BAY_4_SLOPING_PIER','R27_BAY_4_PIER_BASE','R27_BAY_4_PIER_SHOULDER']:
   pier=bpy.data.objects[name];mod=pier.modifiers.new('R52 skew recess coordination','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=void;changed.append(pier.name)
 white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE']
 if bay==2:
  prism('R52_BAY_2_INTERIOR_HEAD',[left-u*.12-n*.125,right+u*.12-n*.125,right+u*.12+n*.125,left-u*.12+n*.125],3.45,4.35,white,'gallery_window_head_fill_candidate')
 else:
  # The previous generic room boundary treated this entire step as opaque.
  cutter=prism('R52_BAY_4_WALL_CUTTER',[left-u*.015-n*.4,right+u*.015-n*.4,right+u*.015+n*.4,left-u*.015+n*.4],.08,3.45,white,'hidden_window_void_candidate');cutter.hide_render=True;cutter.hide_set(True);made.remove(cutter.name);wall=bpy.data.objects['R33_WALL_GALLERY_E_S'];mod=wall.modifiers.new('R52 plan-step glazing aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;changed.append(wall.name)
 rows.append(dict(bay=bay,glass=o.name,back_canonical=[[x0,y],[x1,y]],left=list(left),right=list(right),outward=list(n),front=[list(frontL),list(frontR)],width=w))
# Restore the three opaque segments of the same PDF room boundary, between
# the two candidate glazed steps; keep the original floor polygon untouched.
for i,(aa,bb) in enumerate([((309.00953748,534.65499635),(334.27005932,559.74486845)),((356.21290312,559.74486845),(356.21290312,581.68371548)),((356.21290312,581.68371548),(385.53728687,611.00422358))]):
 p,q=point(*aa),point(*bb);n=up.cross((q-p).normalized())
 if n.dot(point(400,500)-(p+q)/2)>0:n=-n
 prism(f'R52_GALLERY_FRONT_LINER_{i}',[p,q,q+n*.2,p+n*.2],0,4.35,white,'pdf_gallery_boundary_liner_candidate')
S=bpy.context.scene;S['stage']='R52 conditional gallery window and PDF boundary coordination';S['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R52_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=changed,closed_objects=made,windows=rows,construction_acceptance=False,visual_acceptance=False),indent=2),encoding='utf8')
