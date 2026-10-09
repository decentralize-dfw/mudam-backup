"""R40: five source-visible lower windows. Exterior candidates, no room inference."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/basement_windows.json').read_text());F=json.loads((B/'reports/R27_build_report.json').read_text());version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R40_ALT_CEPHE_PENCERELERI_{version}.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P08_LOWER_FACADE_WINDOWS_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);a=Vector(F['origin']);axis=Vector(F['axis']);inside=Vector(F['inside']);up=Vector((0,0,1));made=[];changed=[];cutters=[];windows=[]
stone=bpy.data.materials['R32_LIMESTONE_APPEARANCE_CANDIDATE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R14_DARK_COATED_FRAME_CANDIDATE'];fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def pt(t,d,z):return a+axis*t+inside*d+up*z
def mesh(name,coords,mat,kind,track=True):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(pt(*v)) for v in coords],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='LOWER_FRONT_FACADE',level_id='LM1',source_ids=','.join(P['source_ids']),confidence_xy='D bay-aligned candidate',confidence_z='D unmeasured',confidence_detail='C topology / D dimensions',status='conditional_exterior_only',assumption_note='Five windows and splayed reveals per004/116; all size/depth values conditional; inner room identities unverified.').items():o[k]=v
 if mat==stone:uvmap(o)
 if track:made.append(name)
 return o
def uvmap(o):
 me=o.data;uv=me.uv_layers.get('R32_METRIC_SURFACE_UV') or me.uv_layers.new(name='R32_METRIC_SURFACE_UV')
 for f in me.polygons:
  n=f.normal;u=Vector((1,0,0)) if abs(n.z)>.5 else Vector((-n.y,n.x,0)).normalized();v=Vector((0,1,0)) if abs(n.z)>.5 else up
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/3.2,q.dot(v)/2.4)
def box(name,t0,t1,d0,d1,z0,z1,mat,kind,track=True):return mesh(name,[(t,d,z) for z in [z0,z1] for t,d in [(t0,d0),(t1,d0),(t1,d1),(t0,d1)]],mat,kind,track)
# Cut only pre-existing lower facade cells and one historic wall segment.
targets=[bpy.data.objects[n] for n in F['closed_objects'] if min(v.co.z for v in bpy.data.objects[n].data.vertices)<-1]+[bpy.data.objects['R35_WALL_51946353_00_0']]
for i,t in enumerate(P['centers_m'],1):
 ow=P['outer_width_m']/2;iw=P['inner_width_m']/2;d0=P['outer_depth_m'];d1=P['inner_depth_m'];s0=P['outer_sill_z'];s1=P['inner_sill_z'];h0=P['outer_head_z'];h1=P['inner_head_z'];th=P['stone_thickness_m'];prefix=f'R40_WINDOW_{i:02d}'
 cutter=box(prefix+'_CUTTER',t-ow,t+ow,-1,3.4,s0,h0+.015,stone,'opening_boolean_guide',False);cutters.append(cutter.name)
 for o in targets:
  tv=[(v.co-a).dot(axis) for v in o.data.vertices]
  if max(tv)<=t-ow or min(tv)>=t+ow:continue
  bpy.context.view_layer.objects.active=o;mod=o.modifiers.new(prefix+'_VOID','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
  if o.name not in changed:changed.append(o.name)
 cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE'
 # Two trapezoid jambs: shape narrows toward the glass; no invented hidden hardware.
 for label,sign in [('L',-1),('R',1)]:
  outer=t+sign*ow;inner=t+sign*iw;coords=[]
  for off in [0,sign*th]:coords += [(outer+off,d0,s0),(inner+off,d1,s1),(inner+off,d1,h1),(outer+off,d0,h0)]
  mesh(prefix+'_JAMB_'+label,coords,stone,'splayed_stone_jamb_candidate')
 for label,z0,z1,offset in [('SILL',s0,s1,-th),('HEAD',h0,h1,th)]:
  coords=[(t-ow,d0,z0),(t+ow,d0,z0),(t+iw,d1,z1),(t-iw,d1,z1)];mesh(prefix+'_'+label,coords+[(x,y,z+offset) for x,y,z in coords],stone,'splayed_stone_'+label.lower()+'_candidate')
 fw=P['frame_width_m'];fd=P['frame_depth_m']
 for label,l,r,z0,z1 in [('L',t-iw,t-iw+fw,s1,h1),('R',t+iw-fw,t+iw,s1,h1),('B',t-iw,t+iw,s1,s1+fw),('T',t-iw,t+iw,h1-fw,h1)]:box(prefix+'_FRAME_'+label,l,r,d1-fd,d1,z0,z1,metal,'fixed_frame_candidate')
 name=prefix+'_GLASS';box(name,t-iw+fw,t+iw-fw,d1-P['glass_thickness_m'],d1,s1+fw,h1-fw,glass,'fixed_glass_candidate');windows.append(dict(id=i,center_t=t,glass=name,center=list(pt(t,d1,(s1+h1)/2)),head=h1,sill=s1))
for name in changed:
 ob=bpy.data.objects[name];ob['opening_revision']='R40 exterior basement windows candidate'
 if any(m==stone for m in ob.data.materials):uvmap(ob)
bpy.context.scene['stage']='R40 lower facade window candidates';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R40_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R40_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made+changed,new_objects=made,changed_inherited_objects=changed,hidden_guides=cutters,windows=windows,origin=list(a),axis=list(axis),inside=list(inside),construction_acceptance=False),indent=2),encoding='utf8')
