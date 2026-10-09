"""R96 remove inherited ground-wall intrusions and add source-visible permanent systems."""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base='MUDAM_R95_BES_ISARET_KABUK_DUZELTME_v001.blend';out=B/'scenes/MUDAM_R96_UST_KAT_DUVAR_AYRIMI_v004.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
F=json.loads((B/'config/foundation.json').read_text());C=F['calibration'];P=json.loads((B/'config/side_roof_panels.json').read_text());E=json.loads((B/'config/entry_package.json').read_text());UP=json.loads((B/'reports/R09_build_report.json').read_text())['floor_z'];root=bpy.data.collections.new('R96_UPPER_PLAN_AND_CAFE_STRUCTURE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];records=[];rods=[];up=Vector((0,0,1))
def pt(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def mesh(name,vs,fs,mat,kind,source):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='LP1' if 'SHAFT' in name else 'MULTI',source_ids=source,status='source_topology_candidate_dimensions',assumption_note='Location/topology from source; inherited heights and display member sizes are not measured.').items():ob[k]=v
 made.append(name);return ob
stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];metal=bpy.data.materials['P10_FRAME_PREVIEW'].copy();metal.name='R96_CAFE_SILVER_STRUCTURE_CANDIDATE';n=metal.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(.52,.55,.55,1);n.inputs['Metallic'].default_value=.65;n.inputs['Roughness'].default_value=.36
# These two axis-aligned ground-wall traces cross the diagonal upper room and source doorway.
# Boolean clipping discards their upper continuation without flattening an old doorway mesh.
def box(name,x0,x1,y0,y1,z0,z1):
 ps=[pt(x,y,z) for z in [z0,z1] for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
 return mesh(name,ps,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone,'upper_lift_shaft_boundary_candidate','103,PDF2016')
cut=box('R96_TEMP_UPPER_CUT',760,950,230,440,UP-.2,30)
for name in ['P05_GALLERY_HALL_WEST2','R14_GALLERY_WALL_RETAINED']:
 ob=bpy.data.objects[name];before=[list(ob.matrix_world@v.co) for v in ob.data.vertices];ob.data=ob.data.copy();bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('R96 restrict obsolete ground trace below upper slab','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);ob['R96_note']='Ground wall retained below upper slab; its upper continuation conflicts with both 103 and PDF2016 Petite Galerie Ouest.';changed.append(name);records.append(dict(name=name,before_world=before,max_z_after=max((ob.matrix_world@v.co).z for v in ob.data.vertices)))
made.remove(cut.name);bpy.data.objects.remove(cut,do_unlink=True)
# Resolve the mixed source registration against the existing 103 stair inner faces.
# Keep the 2016 room/door topology, map its two independent axes to 103 room bounds.
M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
def canonical(p):
 a=p.x+293425-M[0][2];b=p.y+5499960-M[1][2];return ((M[1][1]*a-M[0][1]*b)/det-ox)/k,((-M[1][0]*a+M[0][0]*b)/det-oy)/k

def mapped(t,a,b,c,d):
 if t<a:return c+t-a
 if t>b:return d+t-b
 return c+(t-a)*(d-c)/(b-a)
for name in ['R87_ROOM_SIDE','R87_ROOM_FRONT_LEFT','R87_ROOM_FRONT_RIGHT','R87_ROOM_DOOR_HEAD']:
 ob=bpy.data.objects[name];ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
 for v in ob.data.vertices:
  p=ob.matrix_world@v.co;x,y=canonical(p);u=mapped(x+y,1164.18,1221.07,1164.18,1248.43);w=mapped(x-y,496.3,542.79,488,574.43);v.co=inv@pt((u+w)/2,(u-w)/2,p.z)
 ob['R96_source_registration']='2016 topology aligned to 103/R14 room inner boundaries: u1164.18..1248.43 v488..574.43. Non-uniform local registration; not metric as-built.';changed.append(name)
for name in ['R87_ROOM_BACK','R87_ROOM_END']:
 ob=bpy.data.objects[name];ob.hide_render=True;ob.hide_set(True);ob['R96_note']='Superseded interior duplicate; source103 room terminates at existing stair stone backing.';changed.append(name)
def uvbox(name,u0,u1,v0,v1,z0,z1):
 ps=[pt((u+v)/2,(u-v)/2,z) for z in [z0,z1] for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]]
 return mesh(name,ps,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone,'source103_petite_room_boundary','103,PDF2016,097')
uvbox('R96_PETITE_BACK_TO_STAIR',1160.61,1173.5,574.43,578,UP,13.723118)
# The former oversized upper floor spilled across the cafe projection. Preserve its ground slab.
cut=uvbox('R96_TEMP_PETITE_RESERVE',1160.61,1300,440,620,4,30)
for name in ['R87_UPPER_FLOOR','R87_VOLUME_FRONT_END']:
 ob=bpy.data.objects[name];ob.data=ob.data.copy();bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('R96 upper room source boundary','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);changed.append(name)
made.remove(cut.name);bpy.data.objects.remove(cut,do_unlink=True)
# Complete the three clearly drawn upper shaft boundaries, keeping the existing door front.
# This is only the +1 shaft enclosure, not a claimed mechanically coordinated shaft through all floors.
th=.25/C['meters_per_canonical_pixel'];TOP=UP+3.3
box('R96_SHAFT_NORTH',648.88-th,681.42+th,500.93-th,500.93,UP,TOP)
box('R96_SHAFT_WEST',648.88-th,648.88,500.93,529.52,UP,TOP)
box('R96_SHAFT_EAST',681.42,681.42+th,500.93,529.52,UP,TOP)
# PDF2016 +1 explicitly shows the room east of Documentation and its service stair.
# White visitor-plan areas are not automatically voids. Restore the source room shell.
from mathutils.geometry import tessellate_polygon
def prism(name,coords,z0,z1,kind):
 poly=[pt(x,y) for x,y in coords];N=len(poly);lookup={tuple(p):i for i,p in enumerate(poly)}
 def ix(p):return p if isinstance(p,int) else lookup[tuple(p)]
 tris=tessellate_polygon([poly]);faces=[tuple(ix(p) for p in reversed(t)) for t in tris]+[tuple(ix(p)+N for p in t) for t in tris]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 return mesh(name,[p+up*z for z in [z0,z1] for p in poly],faces,stone,kind,'PDF2016_page5_LP1,103')
room=[[623.93,605.63],[680.71,605.63],[680.71,620.46],[692.11,609.06],[728.36,645.31],[694.05,679.61],[684.84,670.4],[684.85,655.62],[623.77,655.62],[623.77,647.58],[611.29,647.58],[611.29,632.33],[623.76,632.33]]
prism('R96_DOCUMENTATION_EAST_FLOOR',room,UP-.2,UP,'source_upper_room_floor')
ROOMTOP=UP+2.7
prism('R96_DOCUMENTATION_EAST_CEILING',room,ROOMTOP,ROOMTOP+.18,'source_room_ceiling_candidate_height')
def boundary(name,a,b,z0=UP,z1=ROOMTOP):
 pa,pb=pt(*a),pt(*b);normal=(pb-pa).normalized().cross(up)*.3
 # polygon follows screen-clockwise source contour; derive outward on source axes
 normal=-normal
 vs=[pa,pb,pb+normal,pa+normal];N=4
 return mesh(name,[p+up*z for z in [z0,z1] for p in vs],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone,'source_upper_room_wall','PDF2016_page5_LP1,103')
# The west connector is already bounded by R09; do not close that door.
for i in range(9):
 a=room[i];b=room[(i+1)%len(room)]
 if i==7:
  boundary('R96_SERVICE_PORTAL_RIGHT',a,[658.31,655.62]);boundary('R96_SERVICE_PORTAL_LEFT',[643.59,655.62],b);boundary('R96_SERVICE_PORTAL_HEAD',[658.31,655.62],[643.59,655.62],UP+2.3,ROOMTOP)
 else:boundary(f'R96_DOCUMENTATION_EAST_WALL_{i}',a,b)
# Complete the short north jamb up to the existing Documentation connector.
boundary('R96_DOCUMENTATION_EAST_WALL_12',room[12],room[0])
# Join the room to the existing bridge/gallery faces rather than leaving scale-registration slits.
prism('R96_DOCUMENTATION_NORTH_JOIN',[[619.81,598],[691.84,598],[680.71,605.63],[623.93,605.63],[623.76,632.33],[619.65,632.33]],UP-.2,ROOMTOP,'source_room_to_bridge_solid_join_candidate')
prism('R96_DOCUMENTATION_GALLERY_JOIN',[[692.11,609.06],[728.36,645.31],[737.02,636.72],[694.1948,595.5826]],UP-.2,ROOMTOP,'source_room_to_gallery_solid_join_candidate')
# The service stair opening remains an opening; no invented flat floor fills the stair.
shaft=[[643.59,655.62],[630.29,669.16],[630.44,686.32],[642.68,698.35],[659.84,698.2],[671.87,685.96],[671.72,668.8],[658.31,655.62]]
for i,(a,b) in enumerate(zip(shaft,shaft[1:])):boundary(f'R96_SERVICE_STAIR_BOUNDARY_{i}',a,b)
# Source photo shows a silver dropped-node/rod network beneath the curved cafe roof.
# Attach to the EXISTING P11 frame grid; do not mirror the east roof shape.
curve=F['polygons']['WEST_CAFE'][:-2];lengths=[0]
for a,b in zip(curve,curve[1:]):lengths.append(lengths[-1]+math.dist(a,b))
def sample(t):
 d=t*lengths[-1]
 for i in range(len(lengths)-1):
  if d<=lengths[i+1]+1e-8:
   f=(d-lengths[i])/(lengths[i+1]-lengths[i]);return [curve[i][j]*(1-f)+curve[i+1][j]*f for j in range(2)]
 return curve[-1]
lo=E['lower_roof']['low_eave_z'];hi=E['lower_roof']['band_bottom_z'];N=P['west_columns'];NY=P['west_slope_rows']
def grid(i,j):
 t=i/N;a=sample(t);b=[688+174*t,432-174*t];return pt(*a,lo).lerp(pt(*b,hi+2.55*math.sin(math.pi*t)),j/NY)
def tube(name,a,b,diam):
 axis=(b-a).normalized();ref=up if abs(axis.z)<.9 else Vector((1,0,0));u=axis.cross(ref).normalized()*diam/2;v=axis.cross(u).normalized()*diam/2;ns=12;ring=[u*math.cos(i*math.tau/ns)+v*math.sin(i*math.tau/ns) for i in range(ns)];ob=mesh(name,[p+q for p in [a,b] for q in ring],[tuple(range(ns-1,-1,-1)),tuple(range(ns,ns*2))]+[(i,(i+1)%ns,(i+1)%ns+ns,i+ns) for i in range(ns)],metal,'cafe_internal_strut_or_tension_rod_candidate','user_cafe_photo_2026-10-09,093');rods.append(dict(name=name,a=list(a),b=list(b),diameter=diam));return ob
for i in range(1,N):
 for j in range(1,NY):
  p=grid(i,j);normal=(grid(i+1,j)-grid(i-1,j)).cross(grid(i,j+1)-grid(i,j-1)).normalized()
  if normal.z<0:normal=-normal
  node=p-normal*P['strut_drop_m'];tube(f'R96_CAFE_STRUT_{i:02}_{j}',p-normal*.08,node,P['strut_diameter_m'])
  for q,(di,dj) in enumerate([(-1,0),(1,0),(0,-1),(0,1)]):tube(f'R96_CAFE_ROD_{i:02}_{j}_{q}',node,grid(i+di,j+dj)-normal*.06,P['rod_diameter_m'])
limits=['R96 removes two confirmed legacy upper-floor intrusions. Petite room topology from PDF locally re-registered in two axes to current103 stair inner faces. Duplicate inner back/end removed; old upper slab over cafe trimmed. Door proportions remain conditional; no metric survey acceptance.','Upper lift shaft sides follow PDF footprint; height3.3m and thickness0.25m remain candidates; no mechanical shaft acceptance.','Cafe dropped nodes and rods are visibly supported by user photo.85 nodes,425 members follow inherited18x6 grid, with unmeasured .42m drop/.085m strut/.012m rod. This is representative architecture, not fabrication detail.','SS3 white zones around Studio/Documentation are not verified public +1 floor; visible lower ceilings and actual voids must not be indiscriminately filled. PDF2016 confirms the omitted east Documentation/service room. Its floor and perimeter are restored; ceiling height follows adjacent Studio candidate. Service stair boundary restored, treads and vertical continuity remain open.','No artwork, temporary exhibition partitions or cafe furniture added.']
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=changed,records=records,documentation_east_room=room,service_stair_boundary=shaft,petite_registration=dict(old_uv=[1164.18,1221.07,496.3,542.79],new_uv=[1164.18,1248.43,488,574.43]),upper_z=UP,rods=rods,construction_acceptance=False,limits=limits)
bpy.context.scene['stage']='R96 upper intrusive walls removed; source upper shaft and cafe rod layer';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R96_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R96_build_report.json').write_text(json.dumps(r,indent=2));print('R96',len(made),'new',changed)
