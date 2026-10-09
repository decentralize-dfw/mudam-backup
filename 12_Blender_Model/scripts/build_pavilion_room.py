"""R17 pavilion floor, circular stair reserve, white interior and opposite window."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/pavilion_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R17_PAVYON_MEKAN_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P17_PAVILION_INTERIOR_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];panels=[];up=Vector((0,0,1));stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];floor=bpy.data.materials['P05_FLOOR_REFERENCE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R16_EXTERIOR_DARK_COATING_CANDIDATE'];white=stone.copy();white.name='R17_PAVILION_WHITE_FINISH_CANDIDATE';white.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.76,.76,.73,1)
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='PAV',level_id='MULTI',source_ids=','.join(P['source_ids']),confidence_xy='C source outline; D window identity and wall thickness',confidence_z='D section ratio and photo candidate',confidence_detail='D unmeasured',status='conditional_pavilion_room',parameter_ids='pavilion_room.json',assumption_note='Circular floor reserve follows plan symbol; not stair construction boundary. Window/finish geometry conditional.').items():ob[k]=v
 made.append(name);return ob
def prism(name,poly,z0,z1,mat,kind):
 N=len(poly);return mesh(name,[p+up*z for z in [z0,z1] for p in poly],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],mat,kind)
foot=[point(*p) for p in P['footprint']];center=sum(foot,Vector())/len(foot);H=Z['Z_PAV_WALL_TOP'];LOW=Z['Z_PAV_LM1_FINISH'];th=P['wall_display_thickness_m'];changed=[]
for name in ['P04_PAV_WALL_ENVELOPE','P05_PAV_LINK_LINTEL']:
 ob=bpy.data.objects[name];ob.hide_render=True;ob.hide_set(True);changed.append(name)
def wall(name,a,b,z0,z1,mat=stone):
 ax=(b-a).normalized();normal=ax.cross(up)
 if normal.dot(center-(a+b)/2)<0:normal=-normal
 ob=prism(name,[a,b,b+normal*th,a+normal*th],z0,z1,mat,'pavilion_wall_envelope')
 if mat==stone:
  ob.data.materials.append(white)
  for f in ob.data.polygons:
   if f.normal.dot(normal)>.8:f.material_index=1
 return ob
for i,(a,b) in enumerate(zip(foot,foot[1:]+foot[:1])):
 if i==3:
  wall('R17_PORTAL_HEAD',a,b,Z['Z_LINK_CEILING'],H);wall('R17_PORTAL_BELOW',a,b,LOW,-.2)
 elif i==7:
  axis=(b-a).normalized();l=a+axis*P['west_window_jamb_m'];r=b-axis*P['west_window_jamb_m'];bot=P['west_window_sill_z'];head=P['west_window_head_z'];wall('R17_WINDOW_LEFT',a,l,LOW,H);wall('R17_WINDOW_RIGHT',r,b,LOW,H);wall('R17_WINDOW_SILL',l,r,LOW,bot);wall('R17_WINDOW_HEAD',l,r,head,H);fw=P['frame_width_m']
  for lab,p,q,z0,z1 in [('LEFT',l,l+axis*fw,bot,head),('RIGHT',r-axis*fw,r,bot,head),('SILL',l,r,bot,bot+fw),('HEAD',l,r,head-fw,head)]:wall('R17_WINDOW_FRAME_'+lab,p,q,z0,z1,metal)
  normal=axis.cross(up)
  if normal.dot(center-(a+b)/2)<0:normal=-normal
  p=l+axis*fw+normal*.1;q=r-axis*fw+normal*.1;ob=prism('R17_WINDOW_GLASS',[p,q,q+normal*P['glass_thickness_m'],p+normal*P['glass_thickness_m']],bot+fw,head-fw,glass,'flat_pavilion_window_candidate');panels.append(ob.name)
 else:wall(f'R17_WALL_{i}',a,b,LOW,H)
slab=prism('R17_GROUND_FLOOR',foot,-P['floor_display_thickness_m'],0,floor,'pavilion_floor_with_stair_reserve');c=point(*P['stair_center_canonical']);radius=P['stair_radius_canonical']*C['meters_per_canonical_pixel'];circle=[c+Vector((math.cos(i*math.tau/96)*radius,math.sin(i*math.tau/96)*radius,0)) for i in range(96)];cut=prism('R17_STAIR_RESERVE_OPERAND',circle,-.8,.3,floor,'source_stair_reserve_not_riser_geometry');cut.hide_render=True;cut.hide_set(True);mod=slab.modifiers.new('R17 circular plan stair reserve','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
bpy.context.scene['stage']='R17 pavilion room candidate; separate stair unresolved';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R17_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,panels=panels,changed_inherited_objects=changed,hidden_superseded=changed,stair_center=list(c),stair_radius=radius,lower_floor_z=LOW,upper_floor_z=0,construction_acceptance=False);(B/'reports/R17_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
