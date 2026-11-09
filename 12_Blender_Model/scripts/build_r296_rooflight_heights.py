from pathlib import Path
import bpy,bmesh,json
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R295_DOGU_IKI_BUYUK_CATI_ADAY_v001.blend'))
heights=json.loads((R/'config/r296_rooflight_heights.json').read_text());records=[]
for i,d in enumerate(heights):
 if i<40:glass=f'R295_ROOFLIGHT_GLASS_{i:02}';prefix=f'R295_ROOFLIGHT_REVEAL_{i:02}_'
 else:glass=f'R295_ROUND_GLASS_{i-40}';prefix=f'R295_ROUND_REVEAL_{i-40}_'
 ob=bpy.data.objects[glass];target=d['median'];old=max(v.co.z for v in ob.data.vertices)
 for v in ob.data.vertices:v.co.z+=target-old
 for frame in [o for o in bpy.context.scene.objects if o.name.startswith(prefix)]:
  lo=min(v.co.z for v in frame.data.vertices);hi=max(v.co.z for v in frame.data.vertices)
  for v in frame.data.vertices:v.co.z=lo+(v.co.z-lo)/(hi-lo)*(target+.06-lo)
 records.append(dict(name=glass,old=old,new=target,sourceSpread=d['p90']-d['p10']))
path=R/'scenes/MUDAM_R296_DOGU_GUNEY_CATI_ISIKLIKLAR_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
s.camera.location=(250,77,180);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=150;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R296_south_roof_authored.png');bpy.ops.render.render(write_still=True)
for ob in s.objects:ob.select_set(ob.name.startswith('R295_'))
glb=R/'exports/r152_clean/r296_south_roof_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R296_SOUTH_ROOF.json').write_text(json.dumps(dict(accepted=False,published=False,scene=str(path),rooflightChanges=records,checks=checks,limits=['One newly traced upper light retains provisional height','Roof is independently planar; whole reference residual includes vegetation and unresolved features','Podium facades and ground connections not rebuilt/accepted; roof only candidate','Public Context3 remains R213']),indent=2));print('R296_READY',flush=True)
