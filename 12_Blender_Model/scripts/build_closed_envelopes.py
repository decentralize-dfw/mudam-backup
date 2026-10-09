"""R44 close legacy single-face envelopes while retaining the traced front face."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/closed_envelopes.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];M=C['pdf_to_utm_matrix'];ux=Vector((M[0][0],M[1][0],0)).normalized();uy=Vector((M[0][1],M[1][1],0)).normalized();up=Vector((0,0,1));version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R44_KAPALI_KABUKLAR_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));changed=[];rows=[]
for row in P['surfaces']:
 ob=bpy.data.objects[row['name']];old=ob.data;assert len(old.polygons)==1 and not ob.modifiers;poly=old.polygons[0];indices=list(poly.vertices);n=len(indices);front=[old.vertices[i].co.copy() for i in indices];world=[ob.matrix_world@p for p in front];normal=(world[1]-world[0]).cross(world[2]-world[0]).normalized();h=row['canonical_direction_hint'];hint=ux*h[0]+uy*h[1]+up*h[2];direction=normal if normal.dot(hint)>0 else -normal;delta=ob.matrix_world.inverted().to_3x3()@(direction*row['thickness_m']);verts=[tuple(p) for p in front]+[tuple(p+delta) for p in front];faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(ob.name+'_R44_CLOSED');me.from_pydata(verts,[],faces);me.update()
 for mat in old.materials:me.materials.append(mat)
 for face in me.polygons:face.material_index=poly.material_index
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for olduv in old.uv_layers:
  uv=me.uv_layers.new(name=olduv.name);source={idx:olduv.data[li].uv.copy() for idx,li in zip(indices,poly.loop_indices)};mapped={j:source[idx] for j,idx in enumerate(indices)}
  for face in me.polygons:
   nm=(ob.matrix_world.to_3x3().inverted().transposed()@face.normal).normalized();u=Vector((-nm.y,nm.x,0)).normalized() if abs(nm.z)<.95 else ux;v=up if abs(nm.z)<.95 else uy
   for li in face.loop_indices:
    vi=me.loops[li].vertex_index
    if face.index<2:uv.data[li].uv=mapped[vi%n]
    else:
     q=ob.matrix_world@me.vertices[vi].co;uv.data[li].uv=(q.dot(u)/3.2,q.dot(v)/2.4)
 ob.data=me;ob['envelope_closure_revision']='R44';ob['display_thickness_candidate_m']=row['thickness_m'];ob['closure_note']='Existing source face fixed; back surface unmeasured finish envelope, not concrete/structure specification.';changed.append(ob.name);rows.append(dict(name=ob.name,original_front_world=[list(p) for p in world],extrusion_world=list(direction*row['thickness_m']),thickness_m=row['thickness_m']))
# Reserve the photographed full-height stair recess in ceiling finishes.
# Offset into the existing wall by 20mm to remove coplanar Boolean interfaces.
def buffer_poly(poly,margin):
 area=sum(p.x*q.y-q.x*p.y for p,q in zip(poly,poly[1:]+poly[:1]));sgn=1 if area>0 else -1;out=[]
 for i,p in enumerate(poly):
  a=poly[i-1];b=poly[(i+1)%len(poly)];u=(p-a).normalized();v=(b-p).normalized();n0=Vector((u.y,-u.x,0))*sgn;n1=Vector((v.y,-v.x,0))*sgn;bis=n0+n1;den=bis.dot(n0);out.append(p+bis*(margin/den) if abs(den)>1e-8 else p+n0*margin)
 return out

def cutter(name,source,z0,z1):
 ob=bpy.data.objects[source];n=len(ob.data.vertices)//2;poly=[ob.matrix_world@v.co for v in list(ob.data.vertices)[:n]]
 for p in poly:p.z=0
 poly=buffer_poly(poly,P['numerical_overlap_m']);verts=[tuple(Vector((p.x,p.y,z))) for z in [z0,z1] for p in poly];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);ob.hide_render=True;ob.hide_set(True);ob.display_type='WIRE';ob['purpose']='20mm numerical intersection inside existing wall, not measured opening';return ob,poly
UP=json.loads((B/'reports/R04_build_report.json').read_text())['upper_level'];cut,poly=cutter('R44_FULL_RECESS_CEILING_RESERVE',P['ceiling_recess_source'],4.0,UP+.2)
canon_origin=Vector((M[0][0]*C['canonical_to_pdf_offset'][0]+M[0][1]*C['canonical_to_pdf_offset'][1]+M[0][2]-293425,M[1][0]*C['canonical_to_pdf_offset'][0]+M[1][1]*C['canonical_to_pdf_offset'][1]+M[1][2]-5499960,0));scale=C['meters_per_canonical_pixel'];reserve=[]
for p in poly:
 q=p-canon_origin;reserve.append([q.dot(ux)/scale,q.dot(uy)/scale])
ceiling_targets=[]
def volume(me):
 bm=bmesh.new();bm.from_mesh(me);v=abs(bm.calc_volume(signed=True));bm.free();return v
for ob in list(bpy.context.scene.objects):
 if not (ob.name.startswith('R39_PUBLIC_CEILING_') or ob.name.startswith('R33_CEILING_')) or ob.hide_render:continue
 old=ob.data;before=volume(old);ob.data=old.copy();bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('R44 full inherited stair recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name)
 if abs(volume(ob.data)-before)<1e-7:
  unused=ob.data;ob.data=old;bpy.data.meshes.remove(unused);continue
 ob['ceiling_stair_coordination']='R44 full R04 recess footprint; source 021/025 open niche';changed.append(ob.name);ceiling_targets.append(ob.name)
fcut,_=cutter('R44_STAIR_FLOOR_NUMERICAL_RESERVE',P['stair_ceiling_cutter'],UP-.6,UP+.2);floor=bpy.data.objects['P05_FLOOR_LP1_BRIDGE'];mods=[m for m in floor.modifiers if m.type=='BOOLEAN' and m.object and m.object.name==P['stair_ceiling_cutter']];assert len(mods)==1;mods[0].object=fcut;changed.append(floor.name)
bpy.context.scene['stage']='R44 closed envelopes and stair ceiling coordination';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R44_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R44_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=changed,changed_inherited_objects=changed,surfaces=rows,stair_ceiling_reserve_canonical=reserve,ceiling_targets=ceiling_targets,numerical_overlap_m=P['numerical_overlap_m'],construction_acceptance=False),indent=2),encoding='utf8')
