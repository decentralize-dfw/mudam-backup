"""R90 replace the legacy unframed south atrium glass proxy with framed panes."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent
base='MUDAM_R89_ALT_KAT_DOSEME_BIRLESIMI_v001.blend';out=B/'scenes/MUDAM_R90_GUNEY_ATRIUM_CAM_CERCEVE_v001.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
C=json.loads((B/'config/foundation.json').read_text())['calibration'];Q=json.loads((B/'config/roof_revision.json').read_text());low=json.loads((B/'reports/R72_build_report.json').read_text())['join_z']
def point(p,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*p[0]+ox;b=k*p[1]+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
a=point(Q['outer_canonical'][4],low);b=point(Q['outer_canonical'][5],low);u=(b-a).normalized();up=Vector((0,0,1));n=u.cross(up).normalized()
if n.dot(a-point([575,447],low))<0:n=-n
W=(b-a).length;H=Q['eave_z'][4]-low;old=bpy.data.objects['P06_HIGH_EAVE_UPSTAND_4'];old.hide_render=True;old.hide_set(True)
root=bpy.data.collections.new('R90_SOUTH_ATRIUM_GLAZING');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R16_EXTERIOR_DARK_COATING_CANDIDATE'];made=[];cells=[]
def box(name,x0,x1,z0,z1,depth,mat,kind,lift=0):
 ps=[a+u*x+up*z+n*lift for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]];me=bpy.data.meshes.new(name)
 me.from_pydata([list(p) for p in ps]+[list(p-n*depth) for p in ps],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='GRAND_HALL',level_id='ROOF',source_ids='116,102,103,101',status='conditional_source_glazing_reconstruction',confidence_xy='C inherited aperture; D subdivisions',confidence_z='D inherited section heights',assumption_note='116 confirms framed glazing here. Three columns align with adjoining narrow roof; four rows and all profile dimensions are unmeasured candidates.').items():o[k]=v
 made.append(name);return o
nx,ny=3,4;gap=.012;fw=.075
for i in range(nx):
 for j in range(ny):
  x0,x1=W*i/nx,W*(i+1)/nx;z0,z1=H*j/ny,H*(j+1)/ny;name=f'R90_SOUTH_GLASS_{i}_{j}'
  box(name,x0+gap,x1-gap,z0+gap,z1-gap,.018,glass,'atrium_glass_panel');cells.append(dict(name=name,center=list(a+u*((x0+x1)/2)+up*((z0+z1)/2))))
for i in range(nx+1):
 x=W*i/nx;box(f'R90_SOUTH_MULLION_{i}',x-fw/2,x+fw/2,0,H,.14,metal,'glazing_frame_candidate',.025)
for j in range(ny+1):
 z=H*j/ny;box(f'R90_SOUTH_TRANSOM_{j}',0,W,z-fw/2,z+fw/2,.14,metal,'glazing_frame_candidate',.025)
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=[old.name],origin=list(a),u=list(u),normal=list(n),width=W,height=H,grid=[nx,ny],panels=cells,source_ids=['116','102','103','101'],construction_acceptance=False,limits=['Source116 shows a framed south-facing strip; old single tinted proxy lacked all frame geometry.','Aperture, wall and roof silhouette unchanged. Twelve panes and nine frame members replace the proxy.','Three columns follow adjacent narrow roof grid; four rows,75mm frame width,140mm depth and18mm glass are explicit visualization candidates.','No seals, anchors, insulated-glass build-up or structural certification inferred.'])
bpy.context.scene['stage']='R90 south atrium glazing envelope with explicit candidate frames';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R90_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R90_build_report.json').write_text(json.dumps(r,indent=2));print('R90 saved',len(made))
