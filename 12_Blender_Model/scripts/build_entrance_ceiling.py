"""R39 close public circulation ceilings while retaining separate service ceilings."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(Path(__file__).parent));from plan_cells import cells;from plan_union import inside
P=json.loads((B/'config/entrance_ceiling.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R39_GIRIS_TAVAN_BUTUNLUGU_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P16_ENTRANCE_CEILING_COORDINATION');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);mat=bpy.data.materials['R32_LIMESTONE_APPEARANCE_CANDIDATE'];made=[];changed=[];rows=[];up=Vector((0,0,1))
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def uvmap(ob):
 me=ob.data;uv=me.uv_layers.get('R32_METRIC_SURFACE_UV') or me.uv_layers.new(name='R32_METRIC_SURFACE_UV')
 for f in me.polygons:
  n=f.normal;u=Vector((1,0,0)) if abs(n.z)>.5 else Vector((-n.y,n.x,0)).normalized();v=Vector((0,1,0)) if abs(n.z)>.5 else up
  for li in f.loop_indices:
   q=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/3.2,q.dot(v)/2.4)
polys=cells(P['public_outer'],list(P['existing_room_ceilings'].values()))
for i,poly in enumerate(polys):
 name=f'R39_PUBLIC_CEILING_{i:02d}';n=len(poly);vs=[tuple(point(x,y,z)) for z in [P['ceiling_z'],P['ceiling_z']+P['ceiling_thickness_m']] for x,y in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat);uvmap(ob)
 for k,v in dict(element_id=name,element_type='public_circulation_ceiling_finish_candidate',zone_id='ENTRANCE_SERVICES',level_id='L00',source_ids='014,017,102,103,PDF2016',confidence_xy='C plan footprint',confidence_z='D inherited ceiling candidate',status='conditional_plan_ceiling',assumption_note='Nonoverlapping surface cells; separate WC/shop/cloak ceilings retained. Thickness and height unmeasured.').items():ob[k]=v
 made.append(name);rows.append(dict(name=name,canonical=poly))
# Public-facing service walls receive the stone finish seen at circulation.
origin=point(0,0);ux=point(1,0)-origin;uy=point(0,1)-origin;s2=ux.length_squared
for ob in list(bpy.context.scene.objects):
 if not ob.name.startswith('R33_WALL_WC_'):continue
 me=ob.data.copy();ob.data=me;slot=len(me.materials);me.materials.append(mat);assigned=[]
 for f in me.polygons:
  if abs(f.normal.z)>.1:continue
  q=ob.matrix_world@f.center+f.normal*.02-origin;xy=[q.dot(ux)/s2,q.dot(uy)/s2]
  if inside(xy,P['public_outer']) and not any(inside(xy,poly) for poly in P['existing_room_ceilings'].values()):f.material_index=slot;assigned.append(f.index)
 if assigned:uvmap(ob);ob['public_finish_revision']='R39 stone family per014/017; exact module unmeasured'
 changed.append(ob.name)
bpy.context.scene['stage']='R39 entrance ceiling continuity';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R39_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R39_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=changed,ceiling_cells=rows,ceiling_z=P['ceiling_z'],construction_acceptance=False),indent=2),encoding='utf8')
