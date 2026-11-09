"""R150 terrain candidate. Not published until wall/bridge boundary acceptance."""
from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Matrix
B=Path(__file__).resolve().parents[1];R=B.parent;p=json.loads((B/'.local_source_cache/r150_terrain_filtered.json').read_text());base=json.loads((B/'reports/R149_build_report.json').read_text())['file'];out=B/'scenes/MUDAM_R150_LIDAR_HENDEK_ADAY_v002.blend';assert not out.exists();assert hashlib.sha256((R/p['source']).read_bytes()).hexdigest()==p['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(R/base));checks=[]
for row in p['surfaces']:
 o=bpy.data.objects[row['name']];mats=list(o.data.materials);vs=row['vertices'];n=len(vs);faces=row['triangles']+[[i+n for i in reversed(f)] for f in row['triangles']]+[[b,a,a+n,b+n] for a,b in row['boundary_edges']];vs=vs+[[x,y,z-.25] for x,y,z in vs];me=bpy.data.meshes.new('R150_'+o.name);me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);checks.append(dict(name=o.name,nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces),volume=bm.calc_volume(signed=True),min_z=row['z_min'],max_z=row['z_max'],xy_area=row['footprint_area_m2']));bm.free();assert not checks[-1]['nonmanifold'] and not checks[-1]['zero_faces'] and checks[-1]['volume']>0
 for m in mats:me.materials.append(m)
 uv=me.uv_layers.new(name='R55_CONTEXT_METRIC_UV')
 for f in me.polygons:
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.x/4,q.y/3)
 o.data=me;o.matrix_world=Matrix.Identity(4);o['source_ids']='ACT_LIDAR2024_MNT,OSM';o['status']='terrain_candidate_pending_boundary_acceptance';o['assumption_note']='Official class2 points with geometric deck exclusion and linear interpolation on 1m grid; building zero conditional; gaps up to 9.27m are not measured ground. Existing footprint retained.'

from mathutils import Vector
for row in p['wall_base_extensions']:
 o=bpy.data.objects[row['name']];inverse=o.matrix_world.inverted()
 for v in o.data.vertices:
  q=o.matrix_world@v.co
  if abs(q.z-row['old_base'])<1e-4:q.z=row['new_base'];v.co=inverse@q
 o.data.update();uv=o.data.uv_layers.get('R55_CONTEXT_METRIC_UV');assert uv
 for f in o.data.polygons:
  normal=(o.matrix_world.to_3x3()@f.normal).normalized();u=Vector((0,0,1)).cross(normal).normalized() if abs(normal.z)<.95 else Vector((1,0,0));u=-u if u.x<-.00001 else u;vaxis=normal.cross(u).normalized()
  for li in f.loop_indices:
   q=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/4,q.dot(vaxis)/3)
 o['assumption_note']='Existing context wall base extended below adjacent LiDAR-derived terrain; head and width unchanged. Footing depth unmeasured; interpolation gaps recorded in R150 coverage receipt.'

bpy.context.scene['stage']='R150 LiDAR terrain candidate - boundary integration pending';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
r=dict(file=out.relative_to(R).as_posix(),base_scene=Path(base).name,changed_inherited_objects=[x['name'] for x in p['surfaces']]+[x['name'] for x in p['wall_base_extensions']],wall_base_extensions=p['wall_base_extensions'],coverage=p['coverage'],terrain_method=p['terrain_method'],closed_objects=[],checks=checks,source=p['source'],source_sha256=p['source_sha256'],datum_national_m=p['datum_national_m'],datum_spread_m=p['datum_spread_m'],accepted=False,construction_acceptance=False,remaining=['Historic wall base integration, especially R68 where source terrain is below existing base.','Bridge and facade terrain interface checks','Source visual comparison and local boundary verification before production export.'])
(B/'reports/R150_build_report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
