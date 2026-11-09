import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R571_SUR_ZEMIN_TEMAS_AO_BAKE_ADAY_v001.blend'));o=bpy.data.objects['R154_FORT_MASONRY_BODY'];old=[v.co.copy()for v in o.data.vertices];oldFaces=len(o.data.polygons)
def tree():
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True)
bv=tree();tests=[]
for r in json.loads((R/'reports/R447_PHOTO_OPENING_POSITIONS.json').read_text()):
 p=Vector(r['point']);n=Vector(r['normal']).normalized();start=p+n*2;hit=bv.ray_cast(start,-n,5)[0];tests.append((list(start),list(-n),list(hit)if hit else None))
# Existing outer faces stay in place; only an inward construction shell closes the eave rim.
mat=o.data.materials[0].copy();mat.name='R577_FORT_INNER_MASONRY'
for nd in list(mat.node_tree.nodes):
 if nd.type=='GROUP'and nd.node_tree and nd.node_tree.name.startswith('glTF Material Output'):mat.node_tree.nodes.remove(nd)
o.data.materials.append(mat);bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('R577 inward closed masonry shell','SOLIDIFY');mod.thickness=.20;mod.offset=-1;mod.use_even_offset=True;mod.use_quality_normals=True;mod.material_offset=1;mod.material_offset_rim=1;bpy.ops.object.modifier_apply(modifier=mod.name)
assert max((o.data.vertices[i].co-p).length for i,p in enumerate(old))<1e-6
bm=bmesh.new();bm.from_mesh(o.data);check=dict(boundary=sum(e.is_boundary for e in bm.edges),nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();assert not any(check.values()),check
bv=tree();errs=[]
for start,direction,expected in tests:
 hit=bv.ray_cast(Vector(start),Vector(direction),5)[0]
 assert (hit is None)==(expected is None)
 if hit:errs.append((hit-Vector(expected)).length)
assert max(errs,default=0)<1e-5,errs
o['R577_shell']='Technical inward0.20m wall closure; outside coordinates and documented recess ray depths unchanged. No cap across true roof opening. Thickness is a rendering/construction envelope, not a measured historic wall thickness.'
out=R/'scenes/MUDAM_R577_KALE_DUVAR_KAPALI_KABUK_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));bm=bmesh.new();bm.from_mesh(bpy.data.objects[o.name if False else 'R154_FORT_MASONRY_BODY'].data);assert all(e.is_manifold for e in bm.edges);bm.free();(R/'reports/R577_CLOSED_FORT_SHELL.json').write_text(json.dumps(dict(reopened=True,check=check,originalOuterVertices=len(old),outerVertexMaxMovement=0,oldFaces=oldFaces,newFaces=len(bpy.data.objects['R154_FORT_MASONRY_BODY'].data.polygons),documentedRecessRays=len(tests),recessDepthMaxChange=max(errs,default=0),roofOpeningCapped=False,innerThicknessAssumption=.20,accepted=False,published=False),indent=2));print('R577_SAVED',check,max(errs,default=0),flush=True)
