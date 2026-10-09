from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R75_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));deps=bpy.context.evaluated_depsgraph_get()
def geom(name):
 o=bpy.data.objects[name].evaluated_get(deps);me=o.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];t=BVHTree.FromPolygons(vs,[list(f.vertices) for f in me.polygons]);o.to_mesh_clear();return vs,t
pairs=[('R29_W_DIVIDER_END','R07_STAIRWELL_STONE_WEST'),('R29_W_BOUNDARY_00','R07_STAIRWELL_STONE_NORTH'),('R10_UPPER_DIAGONAL_WALL','R73_E_CONTINUOUS_GALLERY_WALL'),('P07_GH_EAST_PORTAL_JAMB_S','R04_RECESS_JAMB_FOOT'),('R04_RECESS_JAMB_FOOT','P05_MAIN_ATRIUM_BASE_5_R02_BEFORE_R04_AFTER')]
rows=[]
for a,b in pairs:
 av,at=geom(a);bv,bt=geom(b);distances=[bt.find_nearest(v)[3] for v in av]+[at.find_nearest(v)[3] for v in bv];rows.append(dict(a=a,b=b,vertex_surface_min_m=min(d for d in distances if d is not None),surface_intersections=len(at.overlap(bt))))
(B/'reports/DUVAR_UC_TEMASLARI.json').write_text(json.dumps(dict(file=r['file'],pairs=rows,limits='Vertex-to-surface distances and triangle intersections; not a proof of volumetric contact.'),indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
