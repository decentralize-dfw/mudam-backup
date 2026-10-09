"""R48: retain source stair paths, bridge two disconnected landing handrails."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R47_OKUMA_ISIKLIGI_v002.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R48_KUPESTE_BIRLESIMI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));root=bpy.data.collections.new('R48_LOWER_RAIL_TRANSITION_CANDIDATES');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];rows=[];sides=20;cut_length=.20
def rings(ob):
 p=[ob.matrix_world@v.co for v in ob.data.vertices];return [p[i:i+sides] for i in range(0,len(p),sides)]
def center(r):return sum(r,Vector())/len(r)
def make(name,rr,old,kind):
 verts=[list(v) for ring in rr for v in ring];n=len(rr);faces=[tuple(range(sides-1,-1,-1)),tuple((n-1)*sides+i for i in range(sides))]+[(j*sides+i,(j+1)*sides+i,(j+1)*sides+(i+1)%sides,j*sides+(i+1)%sides) for j in range(n-1) for i in range(sides)];me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob)
 for mat in old.data.materials:me.materials.append(mat)
 for f in me.polygons:f.use_smooth=f.index>=2
 for k,v in old.items():ob[k]=v
 ob['element_id']=name;ob['element_type']=kind;ob['source_ids']='049,050,051,052,102,104';ob['status']='conditional_continuous_landing_handrail';ob['assumption_note']='Observed smooth rail transition; inherited landing offset left 45 mm centreline mismatch. 0.20 m trim and Bezier blend are candidates, not fabrication geometry.';ob['revision']='R48';made.append(name);return ob
def hide(ob):ob.hide_render=True;ob.hide_set(True);ob['superseded_by']='R48 continuous landing transition';changed.append(ob.name)
for side,gi,end in [('INNER',2,'end'),('OUTER',3,'start')]:
 rail=bpy.data.objects['R05_ROUND_RAIL_'+side];ground=bpy.data.objects[f'R05_GROUND_EDGE_TOP_RAIL_{gi}'];rr=rings(rail);gg=rings(ground);oldA=center(rr[-1]);oldB=center(gg[-1] if end=='end' else gg[0]);acc=0.;idx=len(rr)-1
 while acc<cut_length:acc+=(center(rr[idx])-center(rr[idx-1])).length;idx-=1
 retained=rr[:idx+1];a=center(retained[-1]);start=retained[-1];u=(start[0]-a).normalized();v=(start[5]-a).normalized();ta=u.cross(v).normalized()
 if ta.dot(center(rr[idx+1])-a)<0:ta=-ta
 # Walk away from the landing junction and cut a straight ground rail at 0.20 m.
 away=gg if end=='start' else list(reversed(gg));dist=0.;j=0
 while dist+(center(away[j+1])-center(away[j])).length<cut_length:dist+=(center(away[j+1])-center(away[j])).length;j+=1
 span=(center(away[j+1])-center(away[j])).length;t=(cut_length-dist)/span;cut=[x.lerp(y,t) for x,y in zip(away[j],away[j+1])];trimmed=[cut]+away[j+1:];b=center(cut);tb=(center(away[j+1])-center(away[j])).normalized();radii=[(p-a).length for p in start];radius=sum(radii)/sides;length=(b-a).length;handle=length*.42;p1=a+ta*handle;p2=b-tb*handle
 count=40;points=[];tangents=[];us=[];last=u
 for k in range(count+1):
  t=k/count;p=a*(1-t)**3+p1*3*(1-t)**2*t+p2*3*(1-t)*t*t+b*t**3;tangent=((p1-a)*3*(1-t)**2+(p2-p1)*6*(1-t)*t+(b-p2)*3*t*t).normalized();last=(last-tangent*last.dot(tangent)).normalized();points.append(p);tangents.append(tangent);us.append(last.copy())
 # Match the two saved cap rings exactly, choosing the nearest cyclic phase.
 eu=us[-1];ev=tangents[-1].cross(eu).normalized();i0=max(range(sides),key=lambda i:(cut[i]-b).dot(eu));inc=1 if (cut[(i0+1)%sides]-cut[i0]).dot(ev)>0 else -1;endring=[cut[(i0+inc*i)%sides] for i in range(sides)];want=(endring[0]-b).normalized();twist=math.atan2(want.dot(ev),want.dot(eu));blend=[]
 for k,(p,tan,axis) in enumerate(zip(points,tangents,us)):
  axis2=tan.cross(axis).normalized();theta=twist*k/count;ru=axis*math.cos(theta)+axis2*math.sin(theta);rv=tan.cross(ru).normalized();blend.append([p+radius*(ru*math.cos(i*math.tau/sides)+rv*math.sin(i*math.tau/sides)) for i in range(sides)])
 blend[0]=start;blend[-1]=endring
 rname=f'R48_HELICAL_RAIL_{side}';gname=f'R48_LANDING_RAIL_{side}';ename=f'R48_TRANSITION_{side}';make(rname,retained,rail,'retained_helical_handrail_shortened_only_at_landing');make(gname,trimmed,ground,'retained_horizontal_handrail_shortened_at_landing');make(ename,blend,rail,'round_handrail_landing_blend_candidate');hide(rail);hide(ground)
 rows.append(dict(side=side,old_rail=rail.name,old_ground=ground.name,old_ground_end=end,before_centerline_gap_m=(oldA-oldB).length,rail=rname,ground=gname,transition=ename,retained_rail_rings=len(retained),ground_rings=len(trimmed),transition_rings=len(blend),rail_trim_m=acc,ground_trim_m=cut_length,radius_m=radius,start=list(a),end=list(b),start_tangent=list(ta),end_tangent=list(tb),centerline=[list(p) for p in points],start_ring=[list(p) for p in start],end_ring=[list(p) for p in endring],old_rail_ring_index=idx))
# v001 exposed flat-cap shading seams and glass corners above the new blend.
# Produce two single continuous skins, including the inherited ground joins.
def align(ring,previous):
 a=center(previous);b=center(ring);best=None
 for inc in [1,-1]:
  for shift in range(sides):
   candidate=[ring[(shift+inc*i)%sides] for i in range(sides)];cost=sum(((p-b)-(q-a)).length_squared for p,q in zip(candidate,previous))
   if best is None or cost<best[0]:best=(cost,candidate)
 return best[1]
def append_path(dst,extra,merge=False):
 if merge:
  p=(center(dst[-1])+center(extra[0]))/2;tan=(center(extra[1])-center(dst[-2])).normalized();u=(dst[-1][0]-center(dst[-1])).normalized();u=(u-tan*u.dot(tan)).normalized();v=tan.cross(u).normalized();rad=sum((x-center(dst[-1])).length for x in dst[-1])/sides;dst[-1]=[p+rad*(u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides)) for i in range(sides)];extra=extra[1:]
 for ring in extra:dst.append(align(ring,dst[-1]))
continuous=[]
for row in rows:
 path=rings(bpy.data.objects[row['rail']]);transition=rings(bpy.data.objects[row['transition']]);groundpath=rings(bpy.data.objects[row['ground']]);append_path(path,transition[1:]);append_path(path,groundpath[1:])
 if row['side']=='INNER':
  for gi in [1,0]:
   old=bpy.data.objects[f'R05_GROUND_EDGE_TOP_RAIL_{gi}'];append_path(path,list(reversed(rings(old))),merge=True);hide(old)
 name='R48_CONTINUOUS_RAIL_'+row['side'];make(name,path,bpy.data.objects[row['old_rail']],'continuous_round_handrail_with_landing_blend_candidate');row['continuous_rail']=name;row['continuous_ring_count']=len(path);row['continuous_centers']=[list(center(ring)) for ring in path];continuous.append((name,path))
 for key in ['rail','ground','transition']:
  name=row[key];bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True);made.remove(name)
glass_changes=[]
for ob in list(bpy.context.scene.objects):
 if not (ob.name.startswith('R05_GLASS_') or ob.name.startswith('R05_GROUND_EDGE_GLASS_')):continue
 original=[ob.matrix_world@v.co for v in ob.data.vertices];updates=[]
 for i,p in enumerate(original):
  # Only the upper end of the two landing transitions needs reshaping.
  if p.z<.6 or min((Vector((p.x,p.y,0))-Vector((q[0],q[1],0))).length for row in rows for q in [row['start'],row['end']])>.45:continue
  best=None
  for name,path in continuous:
   cc=[center(ring) for ring in path]
   for a,b in zip(cc,cc[1:]):
    d=b-a;dxy=Vector((d.x,d.y,0));t=max(0,min(1,Vector((p.x-a.x,p.y-a.y,0)).dot(dxy)/max(dxy.length_squared,1e-14)));q=a+d*t;error=math.hypot(p.x-q.x,p.y-q.y)
    if best is None or error<best[0]:best=(error,q.z)
  if best and best[0]<.085 and p.z>best[1]-.012:updates.append((i,p.z,best[1]-.012))
 if updates:
  ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
  for i,oldz,newz in updates:q=original[i].copy();q.z=newz;ob.data.vertices[i].co=inv@q
  ob.data.update();ob['landing_top_revision']='R48';ob['landing_top_note']='Local glass upper edge trimmed below candidate continuous rail; glass plane and base kept.';changed.append(ob.name);glass_changes.append(dict(name=ob.name,vertices=[dict(index=i,before=oldz,after=newz) for i,oldz,newz in updates]));made.append(ob.name)
bpy.context.scene['stage']='R48 lower stair landing rail transitions';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=changed,joins=rows,glass_changes=glass_changes,source_ids=['049','050','051','052','102','104'],construction_acceptance=False,limits='Rail axis continuity coordinated; blend length and concealed mounting unmeasured. Local glass upper corners trimmed; glass planes, base channels, treads and circulation unchanged.');(B/'reports/R48_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
manifest=json.loads((B/'references/source_manifest.json').read_text());sources=[s for s in manifest if s['id'] in report['source_ids']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R48_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=report['limits']),indent=2,ensure_ascii=False),encoding='utf8');print('R48 saved',out)
