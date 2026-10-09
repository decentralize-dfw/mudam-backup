"""R97 source-bounded service stair and coordinated floor/ceiling openings."""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
B=Path(__file__).resolve().parents[1];R=B.parent;base='MUDAM_R96_UST_KAT_DUVAR_AYRIMI_v004.blend';out=B/'scenes/MUDAM_R97_SERVIS_MERDIVENI_v003.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'reports/R96_build_report.json').read_text());UP=P['upper_z'];root=bpy.data.collections.new('R97_SERVICE_STAIR_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);mat=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];made=[];changed=[];steps=[];up=Vector((0,0,1));source=json.loads((B/'reports/R97_service_pdf_paths.json').read_text());assert [o['id'] for o in source]==list(range(68,94))
def pt(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def mesh(name,vs,fs,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([list(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='L00_LP1',zone_id='SERVICE_STAIR',source_ids='PDF2016_page5_paths68_93,103',status='conditional_stair_reconstruction',assumption_note='24 radial graphic divisions observed, not a verified construction riser count. Clockwise canonical ascent,24 equal rises,40degree upper landing and180mm tread/slab thickness are candidates.').items():o[k]=v
 made.append(name);return o

def prism(name,poly,z0,z1,kind):
 ps=[pt(x,y) for x,y in poly];n=len(ps);lookup={tuple(p):i for i,p in enumerate(ps)}
 def ix(p):return p if isinstance(p,int) else lookup[tuple(p)]
 tris=tessellate_polygon([ps]);fs=[tuple(ix(p) for p in reversed(t)) for t in tris]+[tuple(ix(p)+n for p in t) for t in tris]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,[p+up*z for z in [z0,z1] for p in ps],fs,kind)
k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];inner=[[(x-ox)/k,(y-251.865-oy)/k] for x,y in source[1]['pts'][:-1]];center=[sum(p[i] for p in inner)/len(inner) for i in range(2)];outer=P['service_stair_boundary']
def crossing(poly,a):
 d=[math.cos(a),math.sin(a)];hits=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  e=[q[0]-p[0],q[1]-p[1]];v=[p[0]-center[0],p[1]-center[1]];den=d[0]*e[1]-d[1]*e[0]
  if abs(den)<1e-10:continue
  t=(v[0]*e[1]-v[1]*e[0])/den;s=(v[0]*d[1]-v[1]*d[0])/den
  if t>0 and -.00001<=s<=1.00001:hits.append(t)
 assert hits,(poly,a)
 t=min(hits);return [center[0]+t*d[0],center[1]+t*d[1]]
# Preserve polygon corners in each tread so straight octagonal walls are followed exactly.
corner_angles=[math.atan2(p[1]-center[1],p[0]-center[0]) for poly in [inner,outer] for p in poly]
bounds=[math.radians(-70+i*320/23) for i in range(24)]+[math.radians(290)]
for j in range(24):
 a,b=bounds[j:j+2];angles=[a,b]
 for v in corner_angles:
  for shift in range(-1,3):
   t=v+shift*math.tau
   if a+1e-8<t<b-1e-8:angles.append(t)
 angles=sorted(set(angles));poly=[crossing(outer,t) for t in angles]+[crossing(inner,t) for t in reversed(angles)];top=UP*(j+1)/24;name=f'R97_SERVICE_TREAD_{j+1:02}';ob=prism(name,poly,top-.18,top,'service_tread_and_landing_candidate')
 for vi,(x,y) in enumerate(poly):
  angle=math.atan2(y-center[1],x-center[0])
  while angle<a-1e-8:angle+=math.tau
  while angle>b+1e-8:angle-=math.tau
  t=max(0,min(1,(angle-a)/(b-a)));ob.data.vertices[vi].co.z=top-.18-UP/24*(1-t)
 bm=bmesh.new();bm.from_mesh(ob.data)
 for face in list(bm.faces):
  if face.is_valid and face.calc_area()<1e-10:bmesh.ops.dissolve_edges(bm,edges=[max(face.edges,key=lambda e:e.calc_length())],use_verts=False)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 a0=crossing(inner,(a+b)/2);b0=crossing(outer,(a+b)/2);xy=[(x+y)/2 for x,y in zip(a0,b0)];steps.append(dict(name=name,top=top,center=list(pt(*xy,top)),canonical=xy,angles_deg=[math.degrees(a),math.degrees(b)],polygon=poly,is_upper_landing=j==23))
# Continue the already source-traced upper well walls down to the ground floor.
for i in range(7):
 ob=bpy.data.objects[f'R96_SERVICE_STAIR_BOUNDARY_{i}'];ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
 for v in ob.data.vertices:
  p=ob.matrix_world@v.co
  if abs(p.z-UP)<1e-4:p.z=0;v.co=inv@p
 changed.append(ob.name)
def volume(me):
 bm=bmesh.new();bm.from_mesh(me);v=abs(bm.calc_volume(signed=True));bm.free();return v
cuts=[]
def apply_cut(ob,cut,label):
 old=ob.data;oldvol=volume(old);ob.data=old.copy();bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name)
 if abs(volume(ob.data)-oldvol)<1e-7:
  unused=ob.data;ob.data=old;bpy.data.meshes.remove(unused);return
 changed.append(ob.name);cuts.append(dict(name=ob.name,before_volume=oldvol,after_volume=volume(ob.data),reason=label))
# Clear suspended ceiling surfaces through the actual stair well, never the entire room.
cut=prism('R97_TEMP_WELL_CUT',outer,.01,UP+.01,'temporary_cutter')
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and not ob.hide_render and ob.name.startswith(('R39_PUBLIC_CEILING_','R33_CEILING_','P05_FLOOR_LP1_')):apply_cut(ob,cut,'R97 service stair well clearance')
made.remove(cut.name);bpy.data.objects.remove(cut,do_unlink=True)
# The ground-service north partition otherwise blocks the plan's stair doorway.
cut=prism('R97_TEMP_GROUND_PORTAL',[[643.59,651],[658.31,651],[658.31,660],[643.59,660]],-.01,2.3,'temporary_cutter')
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and not ob.hide_render and ob.name.startswith('R33_WALL_SERVICE_'):apply_cut(ob,cut,'R97 source ground service stair portal')
made.remove(cut.name);bpy.data.objects.remove(cut,do_unlink=True)
limits=['PDF2016 curves70..93 contain24 graphic radial divisions. They support a spiral stair, not a surveyed24-riser specification.','0 to +1 rise4.8590748m inherited;24 rises give202.46mm. Ascent direction,40degree top landing,180mm slabs and exact headroom are modelling candidates.','Central octagonal opening follows path69; outer well follows existing R96 source boundary. No central column or hidden reinforcement invented.','Service stair lower-basement/roof continuation, railing and finish specification unresolved. Not construction/safety compliance.','User priority maintained: openings and wall/ceiling coordination before door and material details.']
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=sorted(set(changed)),steps=steps,cuts=cuts,inner_canonical=inner,outer_canonical=outer,center_canonical=center,upper_z=UP,graphic_divisions=24,construction_acceptance=False,limits=limits);bpy.context.scene['stage']='R97 service stair candidate and coordinated source well';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R97_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R97_build_report.json').write_text(json.dumps(r,indent=2));print('R97',len(made),'new',len(changed),'changed',cuts)
