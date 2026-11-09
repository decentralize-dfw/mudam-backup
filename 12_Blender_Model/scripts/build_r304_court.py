from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R303_KALE_KUZEY_DOGU_TERASLARI_ADAY_v001.blend'));r=json.loads((R/'config/r304_court_geometry.json').read_text());o=bpy.data.objects['R303_NORTH_COURT'];bm=bmesh.new();bm.from_mesh(o.data);old=BVHTree.FromBMesh(bm,epsilon=.001);base=min(v.co.z for v in bm.verts);top=r['vertices'];bottom=[]
for x,y,z in top:
 h,*_=old.ray_cast(Vector((x,y,-100)),Vector((0,0,1)),200);bottom.append((x,y,min(h.z if h else base,z-.3)))
bm.free();n=len(top);edges={}
for f in r['faces']:
 for a,b in zip(f,f[1:]+f[:1]):k=tuple(sorted((a,b)));edges[k]=edges.get(k,0)+1
fs=r['faces']+[tuple(n+i for i in reversed(f)) for f in r['faces']]+[(a,b,b+n,a+n) for (a,b),count in edges.items() if count==1];me=bpy.data.meshes.new('R304_NORTH_COURT_BANK');me.from_pydata(top+bottom,[],fs);me.update()
for m in o.data.materials:me.materials.append(m)
for p in me.polygons:
 if p.index>=2*len(r['faces']):p.material_index=1
uv=me.uv_layers.new()
for p in me.polygons:
 for li in p.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((v.x+v.y)/4,v.z/3) if p.material_index else (v.x/8,v.y/8)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o.data=me;o.name='R304_NORTH_COURT_BANK';path=R/'scenes/MUDAM_R304_KALE_KUZEY_AVLU_TOPRAK_SEDI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
# Verify saved complete scene, then export the two complete terrace solids.
bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;t=Vector((-175,-135,-15));s.camera.location=t+Vector((100,-160,200));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=300;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R304_fort_candidate.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name in ['R304_NORTH_COURT_BANK','R303_EAST_UPPER_TERRACE'])
glb=R/'exports/r152_clean/r304_fort_terraces_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(c['boundary'] or c['zero'] for c in checks)
(R/'reports/R304_FORT_TERRACES.json').write_text(json.dumps(dict(accepted=False,published=False,checks=checks,northBank=r,scope='Two complete independent terrain/terrace solids; north bank crest source heights, inner slope width provisional. Not full fort acceptance'),indent=2));print('R304_READY')
