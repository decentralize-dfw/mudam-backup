from pathlib import Path
import bpy,json,math,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R168_DOGU_KAVSAK_ADAY_v002.blend'));road=bpy.data.objects['R168_SOURCE_JUNCTION'];road.data.calc_loop_triangles();bvh=BVHTree.FromPolygons([road.matrix_world@v.co for v in road.data.vertices],[list(t.vertices) for t in road.data.loop_triangles],all_triangles=True)
# Source is a 3000x1300 crop displayed at 2048x887. This trace follows the western planted road island.
pixels=[(201,738),(735,669),(743,672),(749,679),(747,687),(739,697),(719,708),(211,759)]
xy=[Vector((-500+(300+x*3000/2048)*1150/4096,675-(650+y*1300/887)*1150/4096,0)) for x,y in pixels]
# Resample the traced boundary without adding inferred connections.
line=[]
for a,b in zip(xy,xy[1:]+xy[:1]):
 count=max(1,math.ceil((b-a).length/2))
 for j in range(count):line.append(a.lerp(b,j/count))
area=sum(a.x*b.y-a.y*b.x for a,b in zip(line,line[1:]+line[:1]));sign=1 if area>0 else -1
inner=[]
for i,p in enumerate(line):
 t=(line[(i+1)%len(line)]-line[(i-1)%len(line)]).normalized();inner.append(p+Vector((-t.y,t.x,0))*(sign*.18))
v=[];faces=[];mids=[];hits=[]
def height(p):
 h,*_=bvh.ray_cast(Vector((p.x,p.y,150)),Vector((0,0,-1)),400);assert h is not None,tuple(p);hits.append(h.z);return h.z
for a,b in zip(line,inner):
 za,zb=height(a),height(b);v.extend([(a.x,a.y,za-.005),(a.x,a.y,za+.12),(b.x,b.y,zb+.12),(b.x,b.y,zb-.005)])
for i in range(len(line)):
 j=(i+1)%len(line);faces.extend([[4*i,4*j,4*j+1,4*i+1],[4*i+1,4*j+1,4*j+2,4*i+2],[4*i+2,4*j+2,4*j+3,4*i+3],[4*i+3,4*j+3,4*j,4*i]])
me=bpy.data.meshes.new('R170_SOURCE_ISLAND_CURB');me.from_pydata(v,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>0;bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);m=bpy.data.materials.new('R170_PALE_CURB');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.46,.46,.41,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.92;me.materials.append(m)
o['source']='R168_junction_source.png; manually traced western planted median boundary';o['assumptions']='0.18m curb width, 0.12m curb height are provisional; source establishes horizontal boundary, not curb section.'
scene=R/'scenes/MUDAM_R170_KAYNAK_ADA_BORDUR_ADAY_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1500;s.render.resolution_y=800;s.render.resolution_percentage=100;center=sum(xy,Vector())/len(xy);center.z=sum(hits)/len(hits);s.camera.location=center+Vector((0,-120,180));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=250;s.render.filepath=str(R/'renders/qa/R170_island_curb_v002.png');bpy.ops.render.render(write_still=True)
(R/'reports/R170_ISLAND_CURB_v002.json').write_text(json.dumps(dict(scene=scene.name,reopened=True,accepted=False,published=False,boundary_samples=len(line),ground_samples=len(hits),source_pixels=pixels,source_display_size=[2048,887],source_image='R168_junction_source.png',curb_height_m=.12,curb_width_m=.18,limits=['Curb section is assumed; only plan boundary is source traced','Only western island boundary is modeled, no entire road completion','Source color still contains tree shadows and vehicles','R169 candidates not integrated; parent is accepted R168']),indent=2));print('CURB_BUILT',len(line))
