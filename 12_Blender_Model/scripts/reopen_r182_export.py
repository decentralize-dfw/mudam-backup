from pathlib import Path
import bpy,json,math
R=Path(__file__).resolve().parents[1];ways={str(w['id']):w for w in json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text(encoding='utf8'))}
bpy.ops.wm.read_factory_settings(use_empty=True);p=R/'exports/r152_clean/r182_district_terrain_REVIEW.glb';bpy.ops.import_scene.gltf(filepath=str(p));records=[];triangles=bad=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles);bad+=sum(t.area<1e-10 for t in o.data.loop_triangles)
 id=o.name.removeprefix('R182_DISTRICT_') if o.name.startswith('R182_DISTRICT_') else o.name[5:] if o.name.startswith(('R171_','R174_')) else ''
 if id not in ways:continue
 xy=[(x-293425,y-5499960) for x,y in ways[id]['xy']];error=0
 for v in o.data.vertices:
  q=o.matrix_world@v.co;error=max(error,min(math.hypot(q.x-x,q.y-y) for x,y in xy))
 records.append(dict(id=id,maximum_footprint_vertex_error=error))
assert len(records)==134,len(records)
assert max(r['maximum_footprint_vertex_error'] for r in records)<.001
assert bad==0,bad
report=dict(glb_reopened=True,triangles=triangles,degenerate=bad,buildings=records,maximum_footprint_error=max(r['maximum_footprint_vertex_error'] for r in records),scope='134 user-authorized abstract masses on OSM footprints plus10 mapped hardscape polygons and exterior measured terrain extension; unknown heights remain explicit neutral8m assumptions',accepted_scope='Technical/source-footprint checks only; full11-region completion NOT claimed')
(R/'reports/R182_REOPEN_v003.json').write_text(json.dumps(report,indent=2));print('R182_REOPEN_OK',triangles,report['maximum_footprint_error'])
