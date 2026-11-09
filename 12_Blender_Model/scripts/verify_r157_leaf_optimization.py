from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1]
def snapshot(version):
 bpy.ops.wm.open_mainfile(filepath=str(R/f'scenes/MUDAM_R157_ARAZI_YOLLAR_AGACLAR_{version}.blend'))
 result={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  far=o.data.name.startswith('R157_TREE_PROTOTYPE_False_')
  data=[tuple(tuple(row) for row in o.matrix_world),o.hide_render]
  if not far:data.extend([tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons)])
  result[o.name]=hashlib.sha256(repr(data).encode()).hexdigest()
 return result
a=snapshot('v003');b=snapshot('v004');changed=[k for k in a if a[k]!=b.get(k)]
assert not changed and a.keys()==b.keys(),changed
result={'scene':'MUDAM_R157_ARAZI_YOLLAR_AGACLAR_v004.blend','reopened':True,'unexpected_changes':changed,'near_trees_terrain_roads_building_geometry_preserved':True,'all_tree_transforms_preserved':True,'prior_ground_contact_report':'R157_GROUND_QA.json','web_test_fps_before':17.2,'web_test_fps_after':18.8,'performance_scope':'Same device, five layers, 12 second viewer camera test; not a general performance guarantee.','remaining':['Road junction and path-edge detailing','Vegetation visual refinement and rendering performance'],'whole_site_accepted':False}
(R/'reports/R157_RELEASE_CHECK.json').write_text(json.dumps(result,indent=2))
print('R157_REOPEN_AND_INHERITANCE_PASSED',flush=True)
