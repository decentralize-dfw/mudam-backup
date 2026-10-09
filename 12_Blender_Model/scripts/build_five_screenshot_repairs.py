"""R95 explicit repairs for user's five screenshots; independent east/west decisions."""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base='MUDAM_R94_ISARETLI_KABUK_BIRLESIMLERI_v003.blend';out=B/'scenes/MUDAM_R95_BES_ISARET_KABUK_DUZELTME_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/ground_gallery_access.json').read_text());L=json.loads((B/'config/entry_package.json').read_text())['lower_roof'];lo=L['low_eave_z'];hi=L['band_bottom_z'];top=13.923118133013933
root=bpy.data.collections.new('R95_FIVE_SCREENSHOT_FIXES');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];probes=[];surfaces=[];records=[];up=Vector((0,0,1));glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R16_EXTERIOR_DARK_COATING_CANDIDATE'];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE']
def pt(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def solid(name,ps,n,depth,mat,kind,issue):
 N=len(ps);me=bpy.data.meshes.new(name);me.from_pydata([list(p) for p in ps]+[list(p-n*depth) for p in ps],[],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,source_ids='102,103,034,043,087,119,PDF2016,user_SS1_SS5',status='conditional_source_boundary_repair',issue_id=issue,assumption_note='Source boundary / user correction; inherited heights and profile dimensions remain unmeasured candidates.').items():o[k]=v
 made.append(name);return o
keys=set()
def beam(name,a,b,n,issue):
 key=tuple(sorted(tuple(round(v,5) for v in p) for p in [a,b]))
 if key in keys:return
 keys.add(key);side=n.cross((b-a).normalized()).normalized()*.0375;lift=n*.025;solid(name,[a-side+lift,b-side+lift,b+side+lift,a+side+lift],n,.14,metal,'glazing_joint_frame_candidate',issue)
def pane(name,ps,issue):
 n=(ps[1]-ps[0]).cross(ps[2]-ps[0]).normalized();center=sum(ps,Vector())/len(ps)
 # Full pane to shared edge; frame overlays it, avoiding shrink-created gaps.
 solid(name,ps,n,.018,glass,'glazing_joint_panel_candidate',issue);surfaces.append(dict(name=name,vertices=[list(p) for p in ps],normal=list(n),issue=issue))
 for i,(a,b) in enumerate(zip(ps,ps[1:]+ps[:1])):beam(name+'_EDGE_'+str(i),a,b,n,issue)
def wall(name,a,b,z0,z1,width,issue,mat=stone):
 aa=pt(*a,z0);bb=pt(*b,z0);n=(bb-aa).normalized().cross(up);solid(name,[aa,bb,bb+up*(z1-z0),aa+up*(z1-z0)],n,width,mat,'source_enclosure_wall_candidate',issue)
 for t in [.1,.3,.5,.7,.9]:
  for z in [z0+.12,(z0+z1)/2,z1-.12]:probes.append(dict(issue=issue,point=list(aa.lerp(bb,t)+up*(z-z0)),normal=list(n),expected='closed',object=name))
# SS1/2: the two inherited roof surfaces do not share an edge. Build the missing
# connecting glazed strip, plus the vertical return above its high end.
a0=pt(462,334,lo);a1=pt(462,430,hi);b0=pt(462.4,336.1,lo);b1=pt(462.4,441.1,hi)
for j in range(6):
 a=a0.lerp(a1,j/6);b=b0.lerp(b1,j/6);c=b0.lerp(b1,(j+1)/6);d=a0.lerp(a1,(j+1)/6)
 pane(f'R95_EAST_SEAM_{j}_A',[a,b,c],'SS1_SS2');pane(f'R95_EAST_SEAM_{j}_B',[a,c,d],'SS1_SS2')
# Shared band levels and three along-edge bays; meet R26 glass cover below.
for i in range(3):
 y0=430+(460.7-430)*i/3;y1=430+(460.7-430)*(i+1)/3
 for j in range(3):
  z0=hi+(top-hi)*j/3;z1=hi+(top-hi)*(j+1)/3
  pane(f'R95_EAST_RETURN_{i}_{j}',[pt(462.4,y0,z0),pt(462.4,y1,z0),pt(462.4,y1,z1),pt(462.4,y0,z1)],'SS1_SS2')
# Small plan offset (0.4 canonical px) at the band corner needs its own return.
for j in range(3):
 z0=hi+(top-hi)*j/3;z1=hi+(top-hi)*(j+1)/3
 pane(f'R95_EAST_CORNER_{j}',[pt(462,430,z0),pt(462.4,430,z0),pt(462.4,430,z1),pt(462,430,z1)],'SS1_SS2')
# SS3: missing outer end above the flat side-hall glass; retain stair route below.
wall('R95_EAST_OUTER_END_ABOVE_GLASS',(289.5,347.3),(349,347.3),hi,top,.25,'SS3')
# SS4: a high roof-support wall had incorrectly been extended to the ground.
# Remove only its ground-storey part, maintaining the upper shell and stair head.
o=bpy.data.objects['R83_CAFE_BACK_WALL'];before=[list(o.matrix_world@v.co) for v in o.data.vertices];o.data=o.data.copy();inv=o.matrix_world.inverted()
for v in o.data.vertices:
 w=o.matrix_world@v.co
 if w.z<P['ceiling_z']:w.z=P['ceiling_z'];v.co=inv@w
o.data.update();changed.append(o.name);records.append(dict(issue='SS4',name=o.name,before=before,ground_clear_to=P['ceiling_z']))
# SS5: R92 wrongly mirrored the user's WEST deletion onto the separate EAST wall.
poly=P['spur_polygons_canonical']['E'];solid('R95_E_GROUND_GALLERY_ENTRY_WALL',[pt(*p,P['ceiling_z']) for p in poly],up,P['ceiling_z'],white,'ground_gallery_entry_wall','SS5')
for a,b in zip(poly,poly[1:]):
 if math.dist(a,b)<25:continue
 aa=pt(*a);bb=pt(*b);n=(bb-aa).normalized().cross(up)
 for t in [.15,.35,.55,.75,.9]:
  for z in [.3,1.65,3.8]:probes.append(dict(issue='SS5',point=list(aa.lerp(bb,t)+up*z),normal=list(n),expected='closed',object='R95_E_GROUND_GALLERY_ENTRY_WALL'))
# Ground cafe line MUST now be traversable at all diagnostic heights.
aa=pt(710,410);bb=pt(810,310);n=(bb-aa).normalized().cross(up)
for t in [.1,.3,.5,.7,.9]:
 for z in [.3,1.65,3.8]:probes.append(dict(issue='SS4',point=list(aa.lerp(bb,t)+up*z),normal=list(n),expected='open',object='R83_CAFE_BACK_WALL'))
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made+changed,changed_inherited_objects=changed,glazed_surfaces=surfaces,probes=probes,records=records,construction_acceptance=False,limits=['SS1/2 joins existing roof edges; glass modules and steel profiles are candidates, not fabrication details.','SS3 wall follows existing outer end footprint and begins above side-hall glass; upper stair circulation remains below.','SS4 removal is limited to the user-marked ground-storey cafe line; high support enclosure remains.','SS5 restores only the east source-plan wall incorrectly deleted with the west one. West detached wall remains absent.','All inherited height datums and the exact glazing/roof shape remain conditional.'])
bpy.context.scene['stage']='R95 five explicit screenshot repairs';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R95_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R95_build_report.json').write_text(json.dumps(r,indent=2));print('R95',len(made),'new pieces')
