"""R13: square lantern evidenced by 089, on the registered octagonal pavilion."""
from pathlib import Path
import bpy,bmesh,json,sys,math,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/pavilion_glazing.json').read_text());F=json.loads((B/'config/foundation.json').read_text());C=F['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']}
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R13_PAVYON_CAM_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;root=bpy.data.collections.new('P11_PAVILION_GLAZING_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];panels=[];frames=[];frame_keys=set();glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];up=Vector((0,0,1))
def point(p,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
outer=np.array(F['polygons']['PAV'],dtype=float);center=outer.mean(axis=0);lines=[]
for i in range(4):
 a,b=outer[2*i:2*i+2];d=b-a;n=np.array([d[1],-d[0]]);n/=np.linalg.norm(n);lines.append((n,n@a))
def intersection(i,j,factor):
 a,b=lines[i],lines[j];return np.linalg.solve(np.array([a[0],b[0]]),np.array([a[0]@center+factor*(a[1]-a[0]@center),b[0]@center+factor*(b[1]-b[0]@center)]))
full=np.array([intersection((i-1)%4,i,1) for i in range(4)]);target=(outer[:,0].max()-outer[:,0].min())*P['tower_width_ratio_101'];factor=target/max(np.ptp(full,axis=0));inner=np.array([intersection((i-1)%4,i,factor) for i in range(4)]);center_world=point(center)
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='PAV',level_id='ROOF',source_ids=','.join(P['source_ids']),confidence_xy='C source footprint; D inner offset',confidence_z='D section-derived inherited heights',confidence_detail='C visible tower grid; D profiles and hidden faces',parameter_ids='pavilion_glazing.json',status='conditional_pavilion_detail',assumption_note='089 supports four tower faces and visible 3x3 grid. Hidden symmetry, roof modules and all hardware sizes remain provisional.',export_group='R13_CANDIDATE').items():ob[k]=v
 made.append(name);return ob
def solid(name,ps,n,depth,mat,kind):
 count=len(ps);return mesh(name,[tuple(p) for p in ps]+[tuple(p-n*depth) for p in ps],[tuple(range(count-1,-1,-1)),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)],mat,kind)
def frame(a,b,n):
 key=tuple(sorted(tuple(round(v,5) for v in p) for p in [a,b]))
 if key in frame_keys or (b-a).length<.01:return
 frame_keys.add(key);axis=(b-a).normalized();side=n.cross(axis)*P['frame_width_m']/2;lift=n*.025;name=f'R13_FRAME_{len(frames):03}';solid(name,[a-side+lift,b-side+lift,b+side+lift,a+side+lift],n,P['frame_depth_m'],metal,'rectangular_frame_candidate');frames.append(name)
def pane(name,ps):
 clean=[]
 for p in ps:
  if not clean or (p-clean[-1]).length>1e-5:clean.append(p)
 if (clean[-1]-clean[0]).length<1e-5:clean.pop()
 ps=clean;n=(ps[1]-ps[0]).cross(ps[2]-ps[0]).normalized();cent=sum(ps,Vector())/len(ps)
 if n.dot(cent-center_world)<0:n=-n
 short=min((b-a).length for a,b in zip(ps,ps[1:]+ps[:1]));shrink=max(.85,1-.05/short);inside=[cent+(p-cent)*shrink for p in ps];solid(name,inside,n,P['glass_thickness_m'],glass,'planar_glass_panel');panels.append(dict(name=name,source_polygon=[list(p) for p in ps],normal=list(n)))
 for a,b in zip(ps,ps[1:]+ps[:1]):frame(a,b,n)
def grid(name,ps,nx,ny):
 def at(u,v):return ps[0]*(1-u)*(1-v)+ps[1]*u*(1-v)+ps[2]*u*v+ps[3]*(1-u)*v
 for i in range(nx):
  for j in range(ny):pane(f'R13_{name}_{i:02}_{j:02}',[at(i/nx,j/ny),at((i+1)/nx,j/ny),at((i+1)/nx,(j+1)/ny),at(i/nx,(j+1)/ny)])
def tube(name,a,b,diam):
 axis=(b-a).normalized();ref=up if abs(axis.z)<.9 else Vector((1,0,0));u=axis.cross(ref).normalized()*diam/2;v=axis.cross(u).normalized()*diam/2;N=16;ring=[u*math.cos(i*math.tau/N)+v*math.sin(i*math.tau/N) for i in range(N)];ob=mesh(name,[tuple(p+q) for p in [a,b] for q in ring],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],metal,'round_member_candidate')
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
wall=Z['Z_PAV_WALL_TOP'];shoulder=Z['Z_PAV_SHOULDER'];top=Z['Z_PAV_LANTERN_TOP'];apex=point(center,Z['Z_PAV_APEX']);facets=[]
for i in range(4):
 a,b=map(lambda p:point(p,wall),outer[2*i:2*i+2]);c=point(inner[(i+1)%4],shoulder);d=point(inner[i],shoulder);ps=[a,b,c,d];facets.append([list(p) for p in ps]);grid('SLOPE_'+str(i),ps,P['roof_face_columns_candidate'],P['roof_rows_candidate'])
 a=point(outer[2*i+1],wall);b=point(outer[(2*i+2)%8],wall);c=point(inner[(i+1)%4],shoulder);facets.append([list(p) for p in [a,b,c]]);grid('HIP_'+str(i),[a,b,c,c],2,P['roof_rows_candidate'])
 a=point(inner[i],shoulder);b=point(inner[(i+1)%4],shoulder);c=point(inner[(i+1)%4],top);d=point(inner[i],top);grid('LANTERN_'+str(i),[a,b,c,d],P['tower_columns'],P['tower_rows']);grid('CAP_'+str(i),[d,c,apex,apex],P['tower_columns'],1)
 inward=(center_world-point((inner[i]+inner[(i+1)%4])/2)).normalized()*.15
 tube('R13_TOWER_X_'+str(i)+'_0',a+inward,d.lerp(c,1)+inward,.012);tube('R13_TOWER_X_'+str(i)+'_1',b+inward,d+inward,.012)
stemtop=apex+up*P['finial_stem_height_m'];tube('R13_FINIAL_STEM',apex,stemtop,P['finial_stem_diameter_m'])
bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=16,v_segments=8,radius=P['finial_ball_diameter_m']/2);verts=[tuple(v.co+stemtop) for v in bm.verts];bm.verts.ensure_lookup_table();faces=[tuple(v.index for v in f.verts) for f in bm.faces];bm.free();mesh('R13_FINIAL_BALL',verts,faces,metal,'visible_apex_ball_candidate')
hidden=[]
for name in ['P04_PAV_ROOF_SLOPE','P04_PAV_LANTERN','P04_PAV_CAP']:
 ob=bpy.data.objects[name];ob.hide_render=True;ob.hide_set(True);hidden.append(name)
S['stage']='R13 source four-sided pavilion lantern and panelized roof';S['current_file']=out.name;bpy.data.texts.new('R13_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,panels=panels,frame_count=len(frames),outer_canonical=outer.tolist(),inner_canonical=inner.tolist(),inner_scale=factor,source_facets=facets,changed_inherited_objects=hidden,hidden_superseded=hidden,tower_faces=4,source_image_grid_visible='089: 3 columns x 3 rows on two visible sides',unseen_faces_symmetry_hypothesis=True,construction_acceptance=False);(B/'reports/R13_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R13',len(made),len(panels),len(frames))
