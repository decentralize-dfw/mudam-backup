import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R320_KUZEY_SUR_HENDEK_BIRLESIM_ADAY_v002.blend'))
stations=json.loads((R/'reports/R323_WEST_CREST_CONTROLS.json').read_text());pts=[Vector(p['measuredCrest']) for p in stations]
t=bpy.data.objects['R152_CLASS2_TERRAIN'];t.data.calc_loop_triangles();bv=BVHTree.FromPolygons([t.matrix_world@v.co for v in t.data.vertices],[list(f.vertices) for f in t.data.loop_triangles],all_triangles=True)
normals=[]
for a,b in zip(pts,pts[1:]):
 d=b-a;d.z=0;d.normalize();normals.append(Vector((-d.y,d.x,0)))
vs=[];ends=[]
for i,p in enumerate(pts):
 n=normals[0] if i==0 else normals[-1] if i==len(pts)-1 else (normals[i-1]+normals[i]).normalized()
 if 0<i<len(pts)-1:n/=max(.35,n.dot(normals[i]))
 sides=[p-n*.40,p+n*.40];low=[]
 for q in sides:
  h=bv.ray_cast(Vector((q.x,q.y,100)),Vector((0,0,-1)),250)[0];assert h is not None;low.append(min(h.z-.25,p.z-.4))
 vs.extend([(sides[0].x,sides[0].y,low[0]),(sides[1].x,sides[1].y,low[1]),tuple(sides[1]),tuple(sides[0])]);ends.append(dict(xyz=list(p),base=low))
fs=[(3,2,1,0),(len(vs)-4,len(vs)-3,len(vs)-2,len(vs)-1)]
for i in range(len(pts)-1):
 for j in range(4):fs.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
me=bpy.data.meshes.new('R321_MUSEUM_WEST_MOAT_RETAINING');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob)
mat=bpy.data.objects['R152_HISTORIC_WALL_49911001'].data.materials[0];me.materials.append(mat);uv=me.uv_layers.new(name='METRIC_UV_4x3m')
for f in me.polygons:
 n=f.normal;u=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.8 else Vector((1,0,0));v=n.cross(u).normalized()
 for li in f.loop_indices:
  q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/4,q.dot(v)/3)
required={getattr(n,'uv_map','') for n in mat.node_tree.nodes} if mat.use_nodes else set()
for name in required-{'','METRIC_UV_4x3m'}:
 layer=me.uv_layers.new(name=name)
 for a,b in zip(layer.data,uv.data):a.uv=b.uv
ob['level_id']='SITE';ob['source']='16 visible crest control stations measured from ACT reference; independently constructed continuous retaining masonry';ob['status']='candidate; three outer ramp corners revised from source sections; width remains provisional';ob['width_uncertainty']='0.8m trace estimate, not survey'
out=R/'scenes/MUDAM_R323_BATI_RAMPA_SUR_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));bpy.ops.object.select_all(action='DESELECT');bpy.data.objects['R321_MUSEUM_WEST_MOAT_RETAINING'].select_set(True)
glb=R/'exports/r152_clean/r323_west_retaining_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-140,-140,75));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-45,-40,-2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=120;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('R321_Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R323_west_retaining.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-4);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),nonmanifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R323_WEST_RETAINING.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,stations=ends,length=sum((b-a).to_2d().length for a,b in zip(pts,pts[1:])),glb=checks,limits=['Width provisional from visible cap, no survey','Three outer ramp stations revised; width and remaining corners still require comparison','Ground behind wall not yet raised into complete terrace','Museum ring not complete']),indent=2));print('R321_READY',checks)
