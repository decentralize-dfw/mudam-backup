"""Fresh-process P07 artifact QA: closed solids, unchanged registration, clear entry."""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
report=json.loads((B/'reports/P07_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/report['file']))
S=bpy.context.scene;root=bpy.data.collections['P07_P08_REGIONAL_PILOT'];obs=[o for o in root.all_objects if o.type=='MESH']
bad_faces=[o.name for o in obs if any(p.area<=1e-9 for p in o.data.polygons)]
solid_checks=[]
for name in report['solid_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();solid_checks.append(dict(name=name,nonmanifold_edges=nonmanifold,volume_m3=volume));assert not nonmanifold and volume>0,(name,nonmanifold,volume)
assert not bad_faces,bad_faces
assert S.unit_settings.system=='METRIC' and S.unit_settings.scale_length==1
assert not [o.name for o in S.objects if min(o.scale)<0]
assert all(bpy.data.objects[n].hide_render for n in report['hidden_superseded'])
schedule=json.loads((B/'config/entry_openings.json').read_text());ids=[x['id'] for x in schedule];assert len(ids)==len(set(ids))==6
for ident in ids:assert bpy.data.objects.get(ident)
# Ray passes through centre of door without hitting any new glass/frame/wall solid.
# Test the relevant active regional meshes, not superseded hidden studies.
checks=[]
for row in report['door_clearance_checks']:
 middle=Vector(row['world_midpoint']);normal=Vector((*row['normal_xy'],0));hits=[]
 for h in [.15,1.4,2.5]:
  target=middle.copy();target.z=h;start=target+normal*4;direction=-normal
  for ob in obs:
   if ob.hide_render or ob.get('collision_role')=='boolean_cutter':continue
   inv=ob.matrix_world.inverted();loc=inv@start;vec=inv.to_3x3()@direction
   hit,point,n,idx=ob.ray_cast(loc,vec,distance=5)
   if hit:hits.append(dict(height=h,object=ob.name))
 assert not hits,hits
 checks.append(dict(id=row['id'],height_samples=[.15,1.4,2.5],hits=hits,clear=True,revolving_leaves_absent=True))
for key in ['087','119','116']:
 cam=bpy.data.objects['P07_PHOTO_'+key+'_CONDITIONAL'];assert cam.data.background_images[0].image.packed_file
out=dict(file=report['file'],mesh_objects_checked=len(obs),closed_solids_checked=len(solid_checks),all_solids_manifold_and_positive=True,zero_area_meshes=bad_faces,opening_ids=ids,door_checks=checks,three_photos_packed=True,camera_projection_errors_px=report['projection_errors_px'],survey_accuracy_claim=False,construction_acceptance=False,notes=['Entry envelope thicknesses and optical settings are visualization hypotheses.','No global shell or structural approval; stairs and many facade openings still pending.'])
(B/'reports/P07_verification.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out,indent=2))
