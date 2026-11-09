from pathlib import Path
import bpy,json,hashlib,struct
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
def sig(o):
 h=hashlib.sha256()
 for row in o.matrix_world:h.update(struct.pack('4d',*row))
 for v in o.data.vertices:h.update(struct.pack('3d',*v.co))
 for f in o.data.polygons:h.update(struct.pack(str(len(f.vertices))+'I',*f.vertices))
 return h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R152_TEMIZ_YAKIN_CEVRE_v009.blend'));old={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R153_PHILHARMONIE_CEVRE_v002.blend'));scene=bpy.context.scene;changes=[n for n,h in old.items() if n not in scene.objects or sig(scene.objects[n])!=h];col=bpy.data.collections['R153_PHILHARMONIE_CLEAN'];bad=[o.name for o in col.objects if any(f.area<1e-10 for f in o.data.polygons)]
p=scene.objects['R153_PLAZA_SOURCE_OUTLINE'];bvh=BVHTree.FromPolygons([p.matrix_world@v.co for v in p.data.vertices],[list(f.vertices) for f in p.data.polygons]);data=json.loads((R/'.local_source_cache/r152/philharmonie_clean.json').read_text());missing=[]
for i,(x,y) in enumerate(data['columns']):
 hit=bvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)[0]
 if hit is None or hit.z<data['base']-.15-.01:missing.append(i)
report=dict(scene=bpy.data.filepath,inherited_mesh_changes=changes,new_objects=len(col.objects),zero_area_objects=bad,columns_checked=len(data['columns']),unsupported_column_indices=missing,placeholder_trees=[o.name for o in scene.objects if o.name.startswith('R152_TREE_')],scope='Candidate mesh and footprint checks only. Does not accept surveyed position, plaza levels, facade completeness or entrance stairs.')
(R/'reports/R153_PHILHARMONIE_QA.json').write_text(json.dumps(report,indent=2));assert not changes and not bad and not missing and not report['placeholder_trees'];print('R153_LOCAL_QA_PASS',flush=True)
