"""R11 source-supported end glazing; preserve the link opening and flag roof gap."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/east_end_glazing.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];E=json.loads((B/'config/entry_package.json').read_text())['lower_roof'];H=E['band_bottom_z'];LO=E['low_eave_z']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R11_DOGU_UC_CAM_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;root=bpy.data.collections.new('P12_EAST_END_GLAZING_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*x+ox;v=k*y+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
x=P['end_plane_x'];ex=(point(x+1,0)-point(x,0)).normalized();ey=(point(x,1)-point(x,0)).normalized();up=Vector((0,0,1));normal=-ex;made=[];panels=[];frames=[];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];keys=set()
def solid(name,ps,n,depth,mat,kind):
 count=len(ps);vs=[tuple(p) for p in ps]+[tuple(p-n*depth) for p in ps];fs=[tuple(range(count-1,-1,-1)),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,source_ids=','.join(P['source_ids']),zone_id='EAST_GARDEN_END',level_id='MULTI',status='conditional_source_window_envelope',confidence_xy='C source boundary; D slot split',confidence_z='D inherited high edge',confidence_detail='D uncounted module candidate',parameter_ids='east_end_glazing.json',assumption_note='Tall window visible in 034/041. Head and module sizes unmeasured. Roof-strip gap deliberately unresolved.').items():ob[k]=v
 made.append(name);return ob
def frame(a,b):
 key=tuple(sorted(tuple(round(v,5) for v in p) for p in [a,b]))
 if key in keys:return
 keys.add(key);axis=(b-a).normalized();side=normal.cross(axis)*P['frame_width_m']/2;name=f'R11_END_FRAME_{len(frames):03}';solid(name,[a-side,b-side,b+side,a+side],normal,P['frame_depth_m'],metal,'rectangular_window_frame_candidate');frames.append(name)
def pane(y0,y1,z0,z1):
 if z1-z0<.03:return
 ps=[point(x,y0,z0),point(x,y1,z0),point(x,y1,z1),point(x,y0,z1)];margin=P['frame_width_m']/2;inside=[ps[0]+ey*margin+up*margin,ps[1]-ey*margin+up*margin,ps[2]-ey*margin-up*margin,ps[3]+ey*margin-up*margin];name=f'R11_END_GLASS_{len(panels):03}';solid(name,inside,normal,P['glass_thickness_m'],glass,'flat_window_glass_candidate');panels.append(name)
 for a,b in zip(ps,ps[1:]+ps[:1]):frame(a,b)
# Correct the shared end-wall edge to the already revised P11 roof corners.
old=bpy.data.objects['P05_EAST_END'];old.hide_render=True;old.hide_set(True)
y0,y1=P['stone_end_y'];solid('R11_STONE_END',[point(x,y0,0),point(x,y1,0),point(x,y1,H),point(x,y0,LO)],normal,P['stone_display_thickness_m'],stone,'source_triangular_end_wall_envelope')
link=bpy.data.objects['P05_LINK_ROOF'];link_z=max((link.matrix_world@v.co).z for v in link.data.vertices);ys=[P['glazed_slot_y'][0]+(P['glazed_slot_y'][1]-P['glazed_slot_y'][0])*j/P['slot_columns_candidate'] for j in range(P['slot_columns_candidate']+1)];ys=sorted(set(ys+[P['link_passage_y'][1]]));zs=sorted(set([H*j/P['slot_rows_candidate'] for j in range(P['slot_rows_candidate']+1)]+[link_z]))
for a,b in zip(ys,ys[1:]):
 for za,zb in zip(zs,zs[1:]):
  if (a+b)/2<P['link_passage_y'][1] and za<link_z-1e-6:continue
  pane(a,b,za,zb)
# Ground link-floor seam spans a half-pixel discrepancy between source boundaries.
floor=bpy.data.materials['P05_FLOOR_REFERENCE'];solid('R11_LINK_THRESHOLD',[point(288.8,264,0),point(289.55,264,0),point(289.55,294,0),point(288.8,294,0)],up,.2,floor,'floor_seam_connection_candidate')
S['stage']='R11 east end glazing and corrected triangular end wall';S['current_file']=out.name;bpy.data.texts.new('R11_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,panels=panels,frames=frames,changed_inherited_objects=[old.name],hidden_superseded=[old.name],roof_high_z=H,roof_low_z=LO,link_z=link_z,glass_head_verified=False,roof_strip_closed=False,construction_acceptance=False);(B/'reports/R11_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
