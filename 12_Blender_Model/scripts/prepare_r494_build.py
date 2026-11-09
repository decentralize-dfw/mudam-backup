from pathlib import Path
R=Path('12_Blender_Model');base=(R/'scripts/build_r487_passage.py').read_text();clip=base[base.index('def clip('):base.index("c=D['coefficients']")]
header='''import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R492_SUR_CEVRE_UV_DUZELTME_ADAY_v001.blend'));D=json.loads((R/'reports/R494_WALL_FACE_PLANE.json').read_text());a,b,c=D['planeYfromXZ'];stations=[49.04445,53,55.5,58,64,68,72.13087]
def top(x):return min(-1.45,-2.15+(x-49.04445)*(.7/(58-49.04445)))
def front(x,z):return a*x+b*z+c
# Build a closed, independent architectural wall; the source mesh remains reference only.
vs=[];fs=[]
for x in stations:
 z=top(x);yf=front(x,z);vs.extend([(x,front(x,-9),-9),(x,yf+1.1,-9),(x,yf+1.1,z),(x,yf,z)])
for i in range(len(stations)-1):
 for j in range(4):fs.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
fs.extend([(3,2,1,0),tuple(range(len(vs)-4,len(vs)))]);me=bpy.data.meshes.new('R494_SOUTH_PAVILION_OUTER_RETAINING_WALL');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.to_mesh(me);bm.free();assert not any(check.values());ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);ob['level_id']='SITE';ob['source']='OSM838550868 first long southern segment, independent planar face fitted to visible ACT wall. Width1.1m and hidden bottom-9m modeling envelope. Crest estimated from visible ACT profile/ground returns; full source acceptance pending.';me.materials.append(bpy.data.materials['R129_HISTORIC_MASONRY_APPEARANCE_CANDIDATE']);uv=me.uv_layers.new(name='R55_CONTEXT_METRIC_UV')
for p in me.polygons:
 for li in p.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x/4,v.z/3) if abs(p.normal.z)<.8 else(v.x/4,v.y/3)
poly=[(stations[0],front(stations[0],-9)),(stations[-1],front(stations[-1],-9)),(stations[-1],front(stations[-1],top(stations[-1]))+1.1),(stations[0],front(stations[0],top(stations[0]))+1.1)];tris=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]]);regions=[[poly[i] if isinstance(i,int) else(i.x,i.y) for i in f]for f in tris];records=[]
'''
tail='''
out=R/'scenes/MUDAM_R494_PAVYON_DIS_ISTINAT_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R494_BUILD.json').write_text(json.dumps(dict(check=check,cuts=records,reopened=True,accepted=False,published=False,limits=['Source-face planar residual RMS.221m,max.379m; not source-fidelity accepted.','Crest transition and unseen base remain candidates.','Eastern return and western end connection incomplete.']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=680;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(90,-105,55));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((28,-36,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=75;s.render.filepath=str(R/'renders/qa/R494_pavilion_candidate.png');bpy.ops.render.render(write_still=True)
'''
(R/'scripts/build_r494_outer_wall.py').write_text(header+clip+tail)
