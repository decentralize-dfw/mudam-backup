from pathlib import Path
import bpy,bmesh,json,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/pavilion_moat.json').read_text());assert hashlib.sha256((R/P['source_path']).read_bytes()).hexdigest()==P['source_sha256'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R68_PAVYON_HENDEK_KOLU_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('R68_PAVILION_MOAT_CONTEXT');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);Z=Vector((0,0,1));made=[];walls=[];UV='R55_CONTEXT_METRIC_UV';stone=bpy.data.materials['R55_HISTORIC_MASONRY_APPEARANCE_CANDIDATE'];grass=bpy.data.materials['R55_MOAT_TURF_APPEARANCE_CANDIDATE']
def prism(name,poly,z0,z1,mat,kind):
 n=len(poly);vs=[tuple(p+Z*z) for z in [z0,z1] for p in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat);uv=me.uv_layers.new(name=UV)
 for f in me.polygons:
  normal=f.normal;u=Z.cross(normal).normalized() if abs(normal.z)<.95 else Vector((1,0,0));u=-u if u.x<-.00001 else u;v=normal.cross(u).normalized()
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/4,q.dot(v)/3)
 for k,v in dict(element_id=name,element_type=kind,zone_id='MOAT_PAVILION',level_id='SITE',source_ids='067,065,OSM',status='representative_site_context',confidence_xy='C OSM chain; map registration uncertain',confidence_z='D inherited flat moat candidate',confidence_detail='D no surveyed thickness or masonry',assumption_note='pavilion_moat.json records map paths and unmeasured flat levels. Not final terrain,ruin openings or drainage.').items():ob[k]=v
 made.append(name);return ob
poly=[Vector((*q,0)) for q in P['polygon']];prism('R68_MOAT_GROUND',poly,P['ground_top_z']-.25,P['ground_top_z'],grass,'moat_wedge_flat_ground_candidate')
normals=[Z.cross((b-a).normalized()) for a,b in zip(poly,poly[1:]+poly[:1])];offsets=[]
for i in range(len(poly)):
 n=(normals[i-1]+normals[i]).normalized();n/=max(.2,n.dot(normals[i]));offsets.append(n*P['wall_width_m']/2)
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
 j=(i+1)%len(poly);name=f'R68_WALL_{i:02d}';prism(name,[a-offsets[i],b-offsets[j],b+offsets[j],a+offsets[i]],P['wall_base_z'],P['wall_top_z'],stone,'historic_moat_wall_envelope_candidate');seg=P['segments'][i];ob=bpy.data.objects[name];ob['osm_way_id']=seg['way'];ob['osm_segment']=seg['source_segment'];walls.append(dict(name=name,way=seg['way'],source_segment=seg['source_segment'],start=list(a),end=list(b),top=P['wall_top_z']))
bpy.context.scene['stage']='R68 pavilion moat wedge context candidate';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R68_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R68_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=[],walls=walls,ground_z=P['ground_top_z'],construction_acceptance=False),indent=2),encoding='utf8');sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['065','067']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R68_source_receipt.json').write_text(json.dumps(dict(photo_sources=sources,map_source=P['source_path'],map_sha256=P['source_sha256'],segments=P['segments'],limits=P['limits']),indent=2),encoding='utf8');print('R68',len(made),'parts')
