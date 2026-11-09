from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R236_KALE_AVLU_YOL_OTURUM_ADAY_v001.blend'))
d=json.loads((R/'config/r239_ruin_partitions.json').read_text());p=[Vector(q) for q in d['points']];v=[Vector((q.x,q.y)) for q in p];dirs=[(v[i+1]-v[i]).normalized() for i in range(2)];n=[Vector((-q.y,q.x)) for q in dirs];mid=(n[0]+n[1]).normalized();offs=[n[0]*.325,mid*(.325/mid.dot(n[0])),n[1]*.325];ring=[v[i]+offs[i] for i in range(3)]+[v[i]-offs[i] for i in range(2,-1,-1)];tops=[p[i].z for i in [0,1,2,2,1,0]];floor=-18.532771
vs=[(q.x,q.y,floor) for q in ring]+[(q.x,q.y,z) for q,z in zip(ring,tops)];fs=[(5,4,1,0),(4,3,2,1),(6,7,10,11),(7,8,9,10)]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
me=bpy.data.meshes.new('R239_RUIN_INNER_PARTITIONS');me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials['R154_FORT_STONE_PBR']);uv=me.uv_layers.new()
for l in me.loops:q=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((q.x+q.y)/3,q.z/2)
o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
path=R/'scenes/MUDAM_R239_KALE_IC_KALINTI_DUVARLARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;t=Vector((-229.6,-192.1,-18));s.camera.location=t+Vector((35,-45,45));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=48;s.render.resolution_x=1000;s.render.resolution_y=850;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R239_ruin_candidate.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R239_'))
g=R/'exports/r152_clean/r239_ruin_partitions_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(g),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(g));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces),finite=all(math.isfinite(c) for v in bm.verts for c in v.co)));bm.free()
assert all(c['finite'] and c['boundary']==0 and c['zero']==0 for c in checks)
(R/'reports/R239_RUIN_PARTITIONS.json').write_text(json.dumps(dict(accepted=False,published=False,measurement=d,reopen=checks,wallThickness=.65,limits=['Thickness follows existing approximate ruin walls; not surveyed','Broken stone profiles and end connections pending','Court grade and source agreement not accepted']),indent=2));print('R239_READY')
