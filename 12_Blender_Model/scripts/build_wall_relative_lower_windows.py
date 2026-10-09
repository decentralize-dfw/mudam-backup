"""R54 trial: top-open historic-wall notches with source-visible jambs/sills."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/lower_windows_wall_relative.json').read_text());site=json.loads((B/'config/site_moat.json').read_text());version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R54_TARIHI_DUVAR_ALT_CAM_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('R54_LOWER_WINDOWS_WALL_RELATIVE_CANDIDATE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
path=next(x for x in site['wall_paths'] if x['id']==P['historic_path']);a,b=[Vector((*q,0)) for q in path['points'][:2]];u=(b-a).normalized();up=Vector((0,0,1));n=u.cross(up);old_inside=Vector(json.loads((B/'reports/R27_build_report.json').read_text())['inside']);n=n if n.dot(old_inside)>0 else -n;stone=bpy.data.materials['R32_LIMESTONE_APPEARANCE_CANDIDATE'];metal=bpy.data.materials['R14_DARK_COATED_FRAME_CANDIDATE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];made=[];changed=[];guides=[];windows=[];fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def pt(t,d,z):return a+u*t+n*d+up*z
def mesh(name,points,mat,kind,visible=True):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(pt(*p)) for p in points],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='LOWER_FRONT_FACADE',level_id='LM1',source_ids=','.join(P['source_ids']),status='conditional_wall_relative_exterior_candidate',assumption_note='OSM wall-relative trial with photo116 ray study; all elevations/dimensions conditional. Nonpublic room identity unknown.').items():o[k]=v
 if mat==stone:
  uv=me.uv_layers.new(name='R32_METRIC_SURFACE_UV')
  for f in me.polygons:
   normal=f.normal;uu=up.cross(normal).normalized() if abs(normal.z)<.95 else u;vv=normal.cross(uu).normalized()
   for li in f.loop_indices:
    q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(uu)/3.2,q.dot(vv)/2.4)
 if visible:made.append(name)
 else:o.hide_render=True;o.hide_set(True);guides.append(name)
 return o
def box(name,t0,t1,d0,d1,z0,z1,mat,kind,visible=True):return mesh(name,[(t,d,z) for z in [z0,z1] for t,d in [(t0,d0),(t1,d0),(t1,d1),(t0,d1)]],mat,kind,visible)
def boolean(ob,cutter,label):
 mod=ob.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 if ob.name not in changed:changed.append(ob.name)
lower=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('R27_') and not o.hide_render and min((o.matrix_world@v.co).z for v in o.data.vertices)<-1]
wall=bpy.data.objects[P['historic_wall_object']]
for i,t in enumerate(P['centers_along_wall_m'],1):
 prefix=f'R54_WINDOW_{i:02d}';ow=P['outer_width_m']/2;iw=P['inner_width_m']/2;d0=P['outer_depth_from_wall_center_m'];d1=P['glass_depth_from_wall_center_m'];s0=P['outer_sill_z'];s1=P['inner_sill_z'];h=P['glass_head_z'];top=P['historic_top_z'];th=P['jamb_thickness_m'];fw=P['frame_width_m'];fd=P['frame_depth_m']
 # A top-open notch, not the rejected R40 closed reveal box.
 coords=[(t-ow-.005,d0-.015,s0-.015),(t+ow+.005,d0-.015,s0-.015),(t+iw+.005,d1+.02,s1-.015),(t-iw-.005,d1+.02,s1-.015)]
 notch=mesh(prefix+'_HISTORIC_CUTTER',coords+[(tt,dd,.1) for tt,dd,zz in coords],stone,'hidden_top_open_notch',False);boolean(wall,notch,prefix+' historic notch')
 void=box(prefix+'_FACADE_CUTTER',t-ow-.01,t+ow+.01,d0-4,d1+4,s0-.01,top+.02,stone,'hidden_lower_facade_opening',False)
 for ob in lower:
  ts=[(ob.matrix_world@v.co-a).dot(u) for v in ob.data.vertices]
  if max(ts)>t-ow-.01 and min(ts)<t+ow+.01:boolean(ob,void,prefix+' lower opening')
 # Exterior reveal sides rise only to the top of the historic wall.
 for label,sign in [('L',-1),('R',1)]:
  coords=[]
  for off in [0,sign*th]:coords += [(t+sign*ow+off,d0,s0),(t+sign*iw+off,d1,s1),(t+sign*iw+off,d1,top),(t+sign*ow+off,d0,top)]
  mesh(prefix+'_JAMB_'+label,coords,stone,'historic_notch_stone_jamb_candidate')
 topcoords=[(t-ow,d0,s0),(t+ow,d0,s0),(t+iw,d1,s1),(t-iw,d1,s1)];mesh(prefix+'_SILL',topcoords+[(tt,dd,zz-th) for tt,dd,zz in topcoords],stone,'sloping_stone_sill_candidate')
 box(prefix+'_BACK_HEAD',t-iw,t+iw,d1,d1+th,h,top,stone,'notch_back_wall_above_frame_candidate')
 for label,l,r,z0,z1 in [('L',t-iw,t-iw+fw,s1,h),('R',t+iw-fw,t+iw,s1,h),('B',t-iw,t+iw,s1,s1+fw),('T',t-iw,t+iw,h-fw,h)]:box(prefix+'_FRAME_'+label,l,r,d1-fd,d1,z0,z1,metal,'lower_fixed_frame_candidate')
 name=prefix+'_GLASS';box(name,t-iw+fw,t+iw-fw,d1-P['glass_thickness_m'],d1,s1+fw,h-fw,glass,'lower_fixed_glass_candidate');windows.append(dict(id=i,glass=name,t=t,inner_width=P['inner_width_m'],outer_width=P['outer_width_m'],head=h,sill=s1,outer_sill=s0,glass_center=list(pt(t,d1,(s1+h)/2)),front_center=list(pt(t,d0,(s1+h)/2))))
for name in changed:bpy.data.objects[name]['opening_revision']='R54 wall-relative lower window candidate; elevations and room identity unresolved'
bpy.context.scene['stage']='R54 trial lower windows aligned to historic wall';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=changed,hidden_guides=guides,windows=windows,origin=list(a),axis=list(u),inside=list(n),visual_acceptance=False,construction_acceptance=False);(B/'reports/R54_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R54',len(made),'new objects',len(changed),'changed')
