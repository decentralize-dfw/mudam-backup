"""R93 replace the legacy unframed north atrium glass proxy with framed panes."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent
base='MUDAM_R92_GALERI_GEREKSIZ_BOLME_KALDIRMA_v001.blend';out=B/'scenes/MUDAM_R93_KUZEY_CAM_PROFIL_HIZALAMA_v001.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
C=json.loads((B/'config/foundation.json').read_text())['calibration'];Q=json.loads((B/'config/roof_revision.json').read_text());low=0.0
def point(p,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*p[0]+ox;b=k*p[1]+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
a=point(Q['outer_canonical'][0],low);b=point(Q['outer_canonical'][1],low);u=(b-a).normalized();up=Vector((0,0,1));n=u.cross(up).normalized()
if n.dot(a-point([575,447],low))<0:n=-n
W=(b-a).length;H=Q['eave_z'][0]
hidden=[]
for old in bpy.data.objects:
 if old.name.startswith(('P11_GH_SLOT_','R80_NORTH_SILL_')) and not old.hide_render:
  old.hide_render=True;old.hide_set(True);hidden.append(old.name)
# Read actual adjacent frame centre elevations, rather than independently divide this face.
def centre_z(o):
 zs=[(o.matrix_world@v.co).z for v in o.data.vertices];return (min(zs)+max(zs))/2
adjacent=[]
for side in ['1','7']:
 vals=[]
 for o in bpy.data.objects:
  if o.name.startswith('P11_GH_BAND_'+side+'_') and '_FRAME_' in o.name and not o.hide_render:
   zs=[(o.matrix_world@v.co).z for v in o.data.vertices]
   if max(zs)-min(zs)<.15:vals.append(centre_z(o))
 adjacent.append(sorted(set(round(z,4) for z in vals)))
assert len(adjacent[0])==4 and len(adjacent[1])==4,adjacent
assert max(abs(x-y) for x,y in zip(*adjacent))<.0001
upper=[sum(v)/2 for v in zip(*adjacent)]
pitch=(upper[-1]-upper[0])/3
levels=upper[:]
while levels[0]-pitch>.05:levels.insert(0,levels[0]-pitch)
levels.insert(0,0.0);levels[-1]=H

root=bpy.data.collections.new('R93_NORTH_ATRIUM_GLAZING');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R16_EXTERIOR_DARK_COATING_CANDIDATE'];made=[];cells=[]
def box(name,x0,x1,z0,z1,depth,mat,kind,lift=0):
 ps=[a+u*x+up*z+n*lift for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]];me=bpy.data.meshes.new(name)
 me.from_pydata([list(p) for p in ps]+[list(p-n*depth) for p in ps],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='GRAND_HALL',level_id='ROOF',source_ids='119,087,102,101',status='conditional_source_glazing_reconstruction',confidence_xy='C inherited aperture; D subdivisions',confidence_z='D inherited section heights',assumption_note='119 and 087 show continuous transverse frame lines. Three columns retained; upper rows match adjacent actual band geometry. Lower pitch continues down to a residual bottom module. Dimensions remain candidates.').items():o[k]=v
 made.append(name);return o
nx=3;ny=len(levels)-1;gap=.012;fw=.075
for i in range(nx):
 for j in range(ny):
  x0,x1=W*i/nx,W*(i+1)/nx;z0,z1=levels[j],levels[j+1];name=f'R93_NORTH_GLASS_{i}_{j}'
  box(name,x0+gap,x1-gap,z0+gap,z1-gap,.018,glass,'atrium_glass_panel');cells.append(dict(name=name,center=list(a+u*((x0+x1)/2)+up*((z0+z1)/2))))
for i in range(nx+1):
 x=W*i/nx;box(f'R93_NORTH_MULLION_{i}',x-fw/2,x+fw/2,0,H,.14,metal,'glazing_frame_candidate',.025)
for j in range(ny+1):
 z=levels[j];box(f'R93_NORTH_TRANSOM_{j}',0,W,z-fw/2,z+fw/2,.14,metal,'glazing_frame_candidate',.025)
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=hidden,transom_levels=levels,adjacent_levels=adjacent,origin=list(a),u=list(u),normal=list(n),width=W,height=H,grid=[nx,ny],panels=cells,source_ids=['119','087','102','101'],construction_acceptance=False,limits=['119 and 087 support aligned transverse lines; actual adjacent band frame elevations govern the shared joints.','Three columns retained. Lower rows continue the same pitch with a residual bottom bay; exact module counts and profile dimensions remain unmeasured candidates.','Only north slot panes and frames replaced. Previous user-marked gallery/roof seams remain open work.','No structural connection, seal or fabrication acceptance implied.'])
bpy.context.scene['stage']='R93 north atrium glazing envelope with explicit candidate frames';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R93_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R93_build_report.json').write_text(json.dumps(r,indent=2));print('R93 saved',len(made))
