"""P11: separate side-roof systems, GH lower bands and pavilion link glazing."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(Path(__file__).resolve().parent))
from roof_panel_math import clip,area,inset
P=json.loads((B/'config/side_roof_panels.json').read_text());F=json.loads((B/'config/foundation.json').read_text());E=json.loads((B/'config/entry_package.json').read_text());Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']}
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_P11_YAN_ORTULER_{version}.blend'
if out.exists():raise RuntimeError('Choose new version')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene
C=F['calibration'];M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset']
def pt(p,z):
 u=k*p[0]+off[0];v=k*p[1]+off[1];return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
root=bpy.data.collections.new('P11_SIDE_ROOF_SYSTEMS_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
cols={}
for key in ['GLASS','FRAMES','INTERNAL_RODS','LINK']:
 c=bpy.data.collections.new('P11_'+key);root.children.link(c);cols[key]=c
glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['P10_FRAME_PREVIEW'];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];made=[];panels=[];keys=set();warps=[];hidden=[]
def mesh(name,verts,faces,col,mat,kind,source):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);cols[col].objects.link(ob);me.materials.append(mat)
 for key,value in dict(element_id=name,element_type=kind,zone_id=name.split('_')[1],level_id='MULTI',source_ids=source,status='conditional_detail_candidate',confidence_xy='C/D source contour',confidence_z='D inherited surface',confidence_detail='D provisional sizes and counts',parameter_ids='side_roof_panels.json',export_group='P11_CONDITIONAL',assumption_note='Separate east/west source geometry. Counts, profiles and internal rods are hypotheses. See source-specific config and report.').items():ob[key]=value
 made.append(name);return ob
def solid(name,p,normal,depth,col,mat,kind,source):
 n=len(p);verts=[tuple(v) for v in p]+[tuple(v-normal*depth) for v in p]
 if n==4:faces=[(0,1,2),(0,2,3),(7,6,5),(7,5,4)]
 else:faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
 faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,verts,faces,col,mat,kind,source)
def beam(name,a,b,normal,source,width=None,depth=None):
 key=tuple(sorted(tuple(round(v,5) for v in p) for p in [a,b]))
 if key in keys or (b-a).length<.025:return
 keys.add(key);side=normal.cross((b-a).normalized()).normalized()*(width or P['frame_width_m'])/2;lift=normal*P['frame_lift_m']
 return solid(name,[a-side+lift,b-side+lift,b+side+lift,a+side+lift],normal,depth or P['frame_depth_m'],'FRAMES',metal,'surface_frame',source)
def tube(name,a,b,diameter,source):
 axis=(b-a).normalized();ref=Vector((0,0,1)) if abs(axis.z)<.9 else Vector((1,0,0));u=axis.cross(ref).normalized()*diameter/2;v=axis.cross(u).normalized()*diameter/2;n=8
 ring=[u*math.cos(i*2*math.pi/n)+v*math.sin(i*2*math.pi/n) for i in range(n)];verts=[tuple(p+r) for p in [a,b] for r in ring];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,verts,faces,'INTERNAL_RODS',metal,'representative_rod_or_strut',source)
def pane(name,p,normal,source):
 center=sum(p,Vector())/len(p);short=min((b-a).length for a,b in zip(p,p[1:]+p[:1]));factor=max(.9,1-.045/max(short,.05));inside=[center+(a-center)*factor for a in p]
 ob=solid(name,inside,normal,P['glass_thickness_m'],'GLASS',glass,'glass_panel',source);panels.append(ob.name)
 warp=max(abs((a-p[0]).dot(normal)) for a in p);warps.append(dict(panel=name,plane_deviation_m=warp));ob['plane_deviation_m']=warp
 for i,(a,b) in enumerate(zip(p,p[1:]+p[:1])):beam(name+'_FRAME_'+str(i),a,b,normal,source)
def quad_grid(name,p,nx,ny,source,rods=False):
 def at(u,v):return p[0]*(1-u)*(1-v)+p[1]*u*(1-v)+p[2]*u*v+p[3]*(1-u)*v
 for i in range(nx):
  for j in range(ny):
   q=[at(i/nx,j/ny),at((i+1)/nx,j/ny),at((i+1)/nx,(j+1)/ny),at(i/nx,(j+1)/ny)];normal=(q[1]-q[0]).cross(q[3]-q[0]).normalized()
   if normal.z<0:normal=-normal
   ident=f'P11_{name}_{i:02}_{j:02}';pane(ident,q,normal,source)
 if rods:
  for i in range(1,nx):
   for j in range(1,ny):
    atgrid=at(i/nx,j/ny);normal=(p[1]-p[0]).cross(p[3]-p[0]).normalized()
    if normal.z<0:normal=-normal
    node=atgrid-normal*P['strut_drop_m'];tube(f'P11_{name}_STRUT_{i}_{j}',atgrid-normal*.08,node,P['strut_diameter_m'],source)
    for side,(u,v) in enumerate([((i-1)/nx,j/ny),((i+1)/nx,j/ny),(i/nx,(j-1)/ny),(i/nx,(j+1)/ny)]):tube(f'P11_{name}_ROD_{i}_{j}_{side}',node,at(u,v)-normal*.06,P['rod_diameter_m'],source)
def hide(ob):ob.hide_render=True;ob.hide_set(True);ob['status']='superseded_by_P11_panels';hidden.append(ob.name)
def stone_base(name,p,source):
 normal=(p[1]-p[0]).cross(p[3]-p[0]).normalized()
 return solid(name,p,normal,.30,'FRAMES',stone,'opaque_stone_base_envelope',source)
def planar_grid(name,p,nx,ny,source):
 origin=p[0];u=(p[1]-origin).normalized();normal=(p[1]-origin).cross(p[2]-origin).normalized();v=normal.cross(u).normalized()
 if normal.z<0:normal=-normal
 poly=[[(a-origin).dot(u),(a-origin).dot(v)] for a in p];xmin=min(a[0] for a in poly);xmax=max(a[0] for a in poly);ymin=min(a[1] for a in poly);ymax=max(a[1] for a in poly)
 for i in range(nx):
  for j in range(ny):
   cell=poly[:]
   for axis,value,sign in [(0,xmin+(xmax-xmin)*i/nx,1),(0,xmin+(xmax-xmin)*(i+1)/nx,-1),(1,ymin+(ymax-ymin)*j/ny,1),(1,ymin+(ymax-ymin)*(j+1)/ny,-1)]:cell=clip(cell,axis,value,sign)
   # Float32 source corners can produce duplicate or collinear clipped points.
   changed=True
   while changed and len(cell)>3:
    changed=False
    for q in range(len(cell)):
     a,b,c=cell[q-1],cell[q],cell[(q+1)%len(cell)];length=math.dist(a,c)
     distance=abs((c[0]-a[0])*(b[1]-a[1])-(c[1]-a[1])*(b[0]-a[0]))/max(length,1e-12)
     if math.dist(a,b)<1e-5 or distance<1e-5:cell.pop(q);changed=True;break
   if len(cell)>=3 and area(cell)>.0001:pane(f'P11_{name}_{i:02}_{j:02}',[origin+u*a[0]+v*a[1] for a in cell],normal,source)
# East roof remains independent of west curve, including its own provisional module count.
ob=bpy.data.objects['P06_EAST_GLAZED_ROOF'];p=[ob.matrix_world@v.co for v in ob.data.vertices];quad_grid('EAST',p,P['east_columns'],P['east_slope_rows'],'034,036,087,119,102',True);hide(ob)
ob=bpy.data.objects['P06_EAST_LOW_GLAZING'];stone_base('P11_EAST_STONE_BASE',[ob.matrix_world@v.co for v in ob.data.vertices],'034,087,102');hide(ob)
# Re-sample the source polyline. The original scan subdivision must not dictate glazing count.
curve=F['polygons']['WEST_CAFE'][:-2];lengths=[0]
for a,b in zip(curve,curve[1:]):lengths.append(lengths[-1]+math.dist(a,b))
def sample(t):
 d=t*lengths[-1]
 for j in range(len(lengths)-1):
  if d<=lengths[j+1]+1e-8:
   u=(d-lengths[j])/(lengths[j+1]-lengths[j]);return [curve[j][n]*(1-u)+curve[j+1][n]*u for n in range(2)]
 return curve[-1]
lo=E['lower_roof']['low_eave_z'];hi=E['lower_roof']['band_bottom_z'];N=P['west_columns']
for i in range(N):
 t0=i/N;t1=(i+1)/N;a=sample(t0);b=sample(t1);h0=[688+174*t0,432-174*t0];h1=[688+174*t1,432-174*t1]
 q=[pt(a,lo),pt(b,lo),pt(h1,hi+2.55*math.sin(math.pi*t1)),pt(h0,hi+2.55*math.sin(math.pi*t0))]
 quad_grid('WEST_'+str(i),q,1,P['west_slope_rows'],'093,119,102,101')
 stone_base('P11_WEST_STONE_BASE_'+str(i),[pt(a,0),pt(b,0),pt(b,lo),pt(a,lo)],'093,102')
for ob in list(S.objects):
 if ob.name.startswith(('P06_WEST_GLAZED_ROOF_','P06_WEST_LOW_GLAZING_')):hide(ob)
# Main lower vertical band: continue eave module distribution; keep slot as separate face.
for suffix in ['1','7']:
 ob=bpy.data.objects['P06_LOWER_BAND_'+suffix];quad_grid('GH_BAND_'+suffix,[ob.matrix_world@v.co for v in ob.data.vertices],P['lower_band_columns'],P['lower_band_rows'],'119,087,029');hide(ob)
ob=bpy.data.objects['P06_NORTH_GLASS_SLOT'];quad_grid('GH_SLOT',[ob.matrix_world@v.co for v in ob.data.vertices],3,9,'119,087');hide(ob)
for side in ['EAST','WEST']:
 ob=bpy.data.objects['P06_LOWER_SLOPE_'+side];planar_grid('GH_LOWER_'+side,[ob.matrix_world@v.co for v in ob.data.vertices],12,6,'119,087,093');hide(ob)
# Link roof/side modules retain the original registered floor outline.
for name,nx,ny in [('P05_LINK_ROOF',P['link_bays'],1),('P05_LINK_SIDE_0',P['link_bays'],1),('P05_LINK_SIDE_2',P['link_bays'],1)]:
 ob=bpy.data.objects[name];p=[ob.matrix_world@v.co for v in ob.data.vertices];quad_grid('LINK_'+name.removeprefix('P05_LINK_'),p,nx,ny,'067,116,102');hide(ob)
 if name.endswith('ROOF'):
  for i in range(nx):
   a=p[0].lerp(p[1],i/nx);b=p[0].lerp(p[1],(i+1)/nx);c=p[3].lerp(p[2],(i+1)/nx);d=p[3].lerp(p[2],i/nx)
   for j,(u,v) in enumerate([(a,c),(b,d)]):tube(f'P11_LINK_CROSS_{i}_{j}',u-Vector((0,0,.12)),v-Vector((0,0,.12)),P['rod_diameter_m'],'067')
S['stage']='P11 side roof glazing, representative east struts/rods and link roof portals; counts and sizes conditional';S['current_file']=out.name
txt=bpy.data.texts.new('P11_READ_ME');txt.write(json.dumps(P,indent=2))
S.camera=bpy.data.objects['P07_PHOTO_087_CONDITIONAL'];S.render.resolution_x=1920;S.render.resolution_y=1281;S.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
for key,size in [('087',(1920,1281)),('116',(2000,1333))]:
 S.camera=bpy.data.objects['P07_PHOTO_'+key+'_CONDITIONAL'];S.render.resolution_x,S.render.resolution_y=size;S.render.filepath=str(B/f'renders/qa/P11_{key}.png');bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),objects=len(made),closed_objects=made,panel_count=len(panels),hidden_superseded=hidden,warp_checks=warps,max_panel_plane_deviation_m=max(w['plane_deviation_m'] for w in warps),internal_structure_status='representative_east_layer_only',pavilion_panelization=False,construction_acceptance=False)
(B/'reports/P11_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('P11_SAVED',out,'panels',len(panels),'max_warp',report['max_panel_plane_deviation_m'])
