import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R482_AVLU_YOL_SEV_BIRLESIM_ADAY_v002.blend'));d=json.loads((R/'reports/R484_NW_WALL_PIECEWISE_CREST.json').read_text());assert d['max']<.1
p=Vector((-53.3,16.5));q=Vector((-26.3,43.5));n=Vector((-1,1)).normalized()*.7;c=d['crestCoefficients']
def crest(y):return c[0]+c[1]*(y-30)+sum(c[i+2]*max(0,y-k) for i,k in enumerate(d['knots']))
vs=[];fs=[];stations=[16.5,21.5,24,39,43.5]
for y in stations:
 P=Vector((y-69.8,y));a=P+n;b=P-n;vs.extend([(a.x,a.y,-7.5),(b.x,b.y,-7.5),(b.x,b.y,crest(b.y)),(a.x,a.y,crest(a.y))])
for i in range(len(stations)-1):
 for j in range(4):fs.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
fs.extend([(3,2,1,0),tuple(range(len(vs)-4,len(vs)))])
me=bpy.data.meshes.new('R484_NW_HISTORIC_RETAINING_WALL');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check={'nonManifold':sum(not e.is_manifold for e in bm.edges),'zeroArea':sum(f.calc_area()<1e-10 for f in bm.faces)};bm.to_mesh(me);bm.free();assert not any(check.values());o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);o['level_id']='SITE';o['source']='Independent planar retaining wall along visible source crest. Axis/width photographic estimates;11 held-out crest points max.0612m. Underground closure -7.5m not surveyed footing.';ma=bpy.data.objects['R152_HISTORIC_WALL_49911001'].data.materials[0];me.materials.append(ma);uv=me.uv_layers.new(name='UVMap');axis=(q-p).normalized()
for poly in me.polygons:
 for li in poly.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;u=(Vector((v.x,v.y))-p).dot(axis);uv.data[li].uv=(u/4,v.z/3) if abs(poly.normal.z)<.8 else (v.x/4,v.y/3)
name=o.name;out=R/'scenes/MUDAM_R484_KUZEYBATI_ISTINAT_DUVARI_ADAY_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);reopen={'nonManifold':sum(not e.is_manifold for e in bm.edges),'zeroArea':sum(f.calc_area()<1e-10 for f in bm.faces)};bm.free();(R/'reports/R484_v002_WALL_BUILD.json').write_text(json.dumps(dict(scene=out.name,check=check,reopen=reopen,accepted=False,published=False,limits=['Width and axis are traced visual candidates.','Full crest extent/end connections and lower passage still require completion.','Foundation closure below terrain is modeling envelope, not surveyed foundation.']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-80,0,35));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-48,37,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=43;s.render.filepath=str(R/'renders/qa/R484_v002_northwest_oblique.png');bpy.ops.render.render(write_still=True)
