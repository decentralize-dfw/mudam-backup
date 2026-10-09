from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
B=Path(__file__).resolve().parents[1];R=B.parent;C=json.loads((B/'config/foundation.json').read_text())['calibration'];base=json.loads((B/'reports/R115_build_report.json').read_text());out=B/'scenes/MUDAM_R116_SEKIZ_ISARET_KABUK_v006.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/base['file']))
UP=4.8590748;LOW=-5.3262935;Z=Vector((0,0,1));made=[];changed=set();ops=[];root=bpy.data.collections.new('R116_USER_MARKED_SHELL_REPAIRS');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE']
def pt(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def native(x,y):
 s,dx,dy=C['basement_registration']['source_to_canonical'];return [s*x+dx,s*y+dy]
def prism(name,poly,z0,z1,mat=stone,issue=''):
 ps=[pt(*p) for p in poly];n=len(ps);lookup={tuple(p):i for i,p in enumerate(ps)}
 def ix(v):return v if isinstance(v,int) else lookup[tuple(v)]
 tri=tessellate_polygon([ps]);fs=[tuple(ix(v) for v in reversed(t)) for t in tri]+[tuple(ix(v)+n for v in t) for t in tri]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata([p+Z*z for z in [z0,z1] for p in ps],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type='marked_architectural_boundary_repair',issue_id=issue,source_ids='102,103,104,user_20261010_SS1_SS8',status='user_corrected_boundary_candidate_dimensions',assumption_note='User-marked boundary correction on existing registered plan. Existing elevations retained; hidden construction and precise dimensions not surveyed.').items():o[k]=v
 made.append(name);return o
def rect(name,x0,x1,y0,y1,z0,z1,mat=stone,issue=''):return prism(name,[[x0,y0],[x1,y0],[x1,y1],[x0,y1]],z0,z1,mat,issue)
def uvrect(name,u0,u1,v0,v1,z0,z1,mat=stone,issue=''):return prism(name,[[(u+v)/2,(u-v)/2] for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]],z0,z1,mat,issue)
def hide(name,issue):
 o=bpy.data.objects[name];o.hide_render=True;o.hide_set(True);o['R116_issue']=issue;changed.add(name);ops.append(dict(name=name,operation='supersede',issue=issue))
def bake(o):
 deps=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);o.modifiers.clear();o.data=me

def volume(o):
 bm=bmesh.new();bm.from_mesh(o.data);v=abs(bm.calc_volume());bm.free();return v

def boolean(o,cut,operation,issue):
 bake(o);old=o.data.copy();before=volume(o);bpy.context.view_layer.objects.active=o;m=o.modifiers.new('R116 '+issue,'BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);after=volume(o)
 if abs(before-after)<1e-7:o.data=old;return
 changed.add(o.name);ops.append(dict(name=o.name,operation=operation,issue=issue,before_volume=before,after_volume=after));o['R116_issue']=issue
 if after<1e-8:o.hide_render=True;o.hide_set(True)
def drop(o):
 made.remove(o.name);bpy.data.objects.remove(o,do_unlink=True)
# SS4: user rejects the inserted internal subdivision. Preserve exterior and stair shell.
for n in ['R87_ROOM_SIDE','R87_ROOM_FRONT_LEFT','R87_ROOM_FRONT_RIGHT','R87_ROOM_DOOR_HEAD']:hide(n,'SS4_1_2')
# SS4_3 missing continuation on cafe side, avoiding the west stair access at far end.
uvrect('R116_PETITE_CAFE_BOUNDARY',1160.61,1164.18,455.57,578,UP,13.723118,stone,'SS4_3')
# SS1: floor skins must terminate inside the facade, not on its exterior plane.
cut=rect('R116_TEMP_E_FLOOR',289.75,1000,0,1000,UP-.3,UP+.1)
boolean(bpy.data.objects['P05_FLOOR_LP1_E0'],cut,'INTERSECT','SS1_1 floor exterior sliver');drop(cut)
# Pavilion slab perimeter inset 20mm; keep the existing stair opening untouched.
poly=json.loads((B/'config/foundation.json').read_text())['polygons']['PAV'];center=[sum(p[i] for p in poly)/len(poly) for i in range(2)];inset=.02/C['meters_per_canonical_pixel'];shrunk=[]
for p in poly:
 d=math.dist(p,center);shrunk.append([center[i]+(p[i]-center[i])*(d-inset)/d for i in range(2)])
cut=prism('R116_TEMP_PAV_INSET',shrunk,-10,1)
for n in ['R17_GROUND_FLOOR','R25_LOWER_PAVILION_FLOOR']:boolean(bpy.data.objects[n],cut,'INTERSECT','SS1_3 slab concealed within stone');
drop(cut)
# SS1_2: rebuild the modern lower backing on the historic-window inner plane.
# Retire the crossed old lower face; retain the photographed upper recesses.
wr=json.loads((B/'reports/R54_build_report.json').read_text());wp=json.loads((B/'config/lower_windows_wall_relative.json').read_text());origin=Vector(wr['origin']);axis=Vector(wr['axis']);inside=Vector(wr['inside'])
def canonical(p):
 M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];d=M[0][0]*M[1][1]-M[0][1]*M[1][0];a=p.x+293425-M[0][2];b=p.y+5499960-M[1][2];return [((M[1][1]*a-M[0][1]*b)/d-ox)/k,((-M[1][0]*a+M[0][0]*b)/d-oy)/k]
def wallbox(name,t0,t1,d0,d1,z0,z1):return prism(name,[canonical(origin+axis*t+inside*d) for t,d in [(t0,d0),(t1,d0),(t1,d1),(t0,d1)]],z0,z1,stone,'SS1_2')
lower=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('R27_') and min((o.matrix_world@v.co).z for v in o.data.vertices)<-1]
coords=[o.matrix_world@v.co for o in lower for v in o.data.vertices];t0=min((p-origin).dot(axis) for p in coords);t1=max((p-origin).dot(axis) for p in coords);d1=max(1.0,max((p-origin).dot(inside) for p in coords))
cut=rect('R116_TEMP_OLD_LOWER',0,1100,0,1100,-15,-.8)
for o in lower:boolean(o,cut,'DIFFERENCE','SS1_2 retire crossed lower facade')
drop(cut)
# Exact shared grid extrusion: avoid coplanar Boolean fragments at the five reveals.
back=wallbox('R116_LOWER_FACADE_BACKING',t0,t1,.65,1.0,LOW,-.8)
ticks=sorted([t0,t1]+[t+v*wp['inner_width_m']/2 for t in wp['centers_along_wall_m'] for v in [-1,1]]);zs=[LOW,wp['inner_sill_z'],wp['glass_head_z'],-.8];cells=set()
for i in range(len(ticks)-1):
 for j in range(3):
  mid=(ticks[i]+ticks[i+1])/2
  if j==1 and any(abs(mid-t)<wp['inner_width_m']/2 for t in wp['centers_along_wall_m']):continue
  cells.add((i,j))
verts=[];faces=[];lookup={}
def vi(t,d,z):
 key=(round(t,8),d,z)
 if key not in lookup:lookup[key]=len(verts);verts.append(origin+axis*t+inside*d+Z*z)
 return lookup[key]
for i,j in cells:
 aa,bb=ticks[i:i+2];lo,hi=zs[j:j+2];q=[vi(t,d,z) for d in [.65,1.0] for t,z in [(aa,lo),(bb,lo),(bb,hi),(aa,hi)]]
 faces.extend([tuple(q[k] for k in [0,3,2,1]),tuple(q[k] for k in [4,5,6,7])])
 for neighbor,ids in [((i-1,j),[0,4,7,3]),((i+1,j),[1,2,6,5]),((i,j-1),[0,1,5,4]),((i,j+1),[3,7,6,2])]:
  if neighbor not in cells:faces.append(tuple(q[k] for k in ids))
me=bpy.data.meshes.new('R116_LOWER_BACKING_GRID');me.from_pydata(verts,[],faces);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(stone);back.data=me
for i in range(1,6):hide(f'R54_WINDOW_{i:02d}_BACK_HEAD','SS1_2 replaced by continuous lower backing head')
# SS2/5 duplicate floor layers: resolve actual intersections, not a z-offset hack.
for a,b,issue in [('R28_E_CIRCULATION_FLOOR','P05_FLOOR_L00_E0','SS2'),('R28_W_CIRCULATION_FLOOR','P05_FLOOR_L00_W0','SS2'),('R87_UPPER_FLOOR','P05_FLOOR_LP1_W0','SS5'),('R23_WEST_RETURN_FLOOR_0','P05_FLOOR_LP1_W0','SS5'),('R23_WEST_RETURN_FLOOR_1','P05_FLOOR_LP1_W0','SS5'),('R23_WEST_RETURN_FLOOR_0','R87_UPPER_FLOOR','SS5'),('R23_WEST_RETURN_FLOOR_1','R87_UPPER_FLOOR','SS5')]:
 boolean(bpy.data.objects[a],bpy.data.objects[b],'DIFFERENCE',issue+' coplanar floor duplicate')
# SS6_3 landing backing was flush with bridge finish; lower its top to slab underside.
o=bpy.data.objects['R04_RECESS_TOP_BELOW_LANDING'];bake(o);inv=o.matrix_world.inverted()
for v in o.data.vertices:
 p=o.matrix_world@v.co
 if p.z>UP-.201:p.z=UP-.2;v.co=inv@p
changed.add(o.name);ops.append(dict(name=o.name,operation='lower backing top to bridge underside',issue='SS6_3'))
# Upper bridge north wall lines, leaving the actual stair outlet and lift door approach.
rect('R116_BRIDGE_NORTH_WEST',465,521.2,555.5,558.0,UP,12.523118,stone,'SS6_1')
rect('R116_BRIDGE_NORTH_EAST',595,644.74,555.5,558.0,UP,12.523118,stone,'SS6_2')
# SS3/7: fill the thin seam between the source portal jamb and stair recess jamb.
prism('R116_STAIR_PORTAL_JAMB_JOIN',[[464.95,474.73],[468.13,474.34],[474.11,469.11],[466.89,476.33]],0,8.259075,stone,'SS3_SS7')
# Carry the gallery wall down to the existing portal beam top; eliminate the exposed wall-core slit.
o=bpy.data.objects['R73_E_CONTINUOUS_GALLERY_WALL'];bake(o);inv=o.matrix_world.inverted()
for v in o.data.vertices:
 p=o.matrix_world@v.co
 if abs(p.z-4.35)<.0001:p.z=4.12;v.co=inv@p
changed.add(o.name);ops.append(dict(name=o.name,operation='continue lower edge to existing beam top',issue='SS2_SS7'))
# SS8_1/2: trace the full recess floor rather than leaving margins beside the doorway.
for side,x0,x1,y0 in [('L',480,489,397),('R',555,565,397)]:
 patch=prism('R116_AUD_ENTRY_FLOOR_'+side,[native(x,y) for x,y in [(x0,y0),(x1,y0),(x1,424),(x0,424)]],LOW-.2,LOW,stone,'SS8_1_2')
 for n in ['R29_FOYER_FLOOR','R19_ROOM_FLOOR','R19_ENTRY_FLOOR_'+side]:
  source=bpy.data.objects[n];cut=source.copy();cut.data=source.data.copy();cut.modifiers.clear();root.objects.link(cut);iv=cut.matrix_world.inverted()
  for v in cut.data.vertices:
   p=cut.matrix_world@v.co;p.z+=.01 if p.z>LOW-.1 else -.01;v.co=iv@p
  boolean(patch,cut,'DIFFERENCE','SS8 floor patch without overlaps');bpy.data.objects.remove(cut,do_unlink=True)
 bm=bmesh.new();bm.from_mesh(patch.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(patch.data);bm.free()
# SS7 wall-end return: close the exposed upper gallery wall core to the stair jamb.
prism('R116_E_GALLERY_END_RETURN',[[457.87825,467.12150],[459.99630,466.21406],[466.89356,476.33035],[464.95335,474.73704]],0,13.923118,stone,'SS2_SS7')
# SS8_3/4: the small front volumes are enclosed rooms; keep a door-sized central opening.
for side,x0,x1,y in [('E',435,454,424),('W',591,612,424)]:
 mid=(x0+x1)/2;half=.5/(C['meters_per_canonical_pixel']*C['basement_registration']['source_to_canonical'][0])
 for suffix,a,b,z0,z1 in [('LEFT',x0,mid-half,LOW,LOW+4.67),('RIGHT',mid+half,x1,LOW,LOW+4.67),('HEAD',mid-half,mid+half,LOW+2.2,LOW+4.67)]:
  prism('R116_FOYER_'+side+'_'+suffix,[native(x,yy) for x,yy in [(a,y-.7),(b,y-.7),(b,y+.7),(a,y+.7)]],z0,z1,stone,'SS8_3_4')
 # Plain closed leaf is explicitly a non-product placeholder in the existing side-room front.
 leaf=prism('R116_FOYER_'+side+'_CLOSED_LEAF',[native(x,yy) for x,yy in [(mid-half+.12,y-.18),(mid+half-.12,y-.18),(mid+half-.12,y+.18),(mid-half+.12,y+.18)]],LOW+.015,LOW+2.185,white,'SS8_3_4');leaf['assumption_note']='User confirms this side volume is not open. 104 fixes room footprint; 1m leaf and 2.2m head are representative, door product and exact size unknown.'
# Record a candidate, not a claim of perfect as-built reconstruction.
r=dict(file=out.relative_to(R).as_posix(),base_scene=Path(base['file']).name,closed_objects=made,changed_inherited_objects=sorted(changed),operations=ops,construction_acceptance=False,visual_acceptance=False,limits=['Eight marked groups require same-view visual verification before acceptance.','Source boundaries plus explicit user corrections; inherited heights and new side-room door sizes remain unmeasured.','SS2 rear wall alignment and SS7 upper corner need visual confirmation after these edits.'])
bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R116_build_report.json').write_text(json.dumps(r,indent=2),encoding='utf8');print('R116 candidate',len(made),'new',len(changed),'changed')
