from pathlib import Path
import bpy,bmesh,json,math
R=Path(__file__).resolve().parents[1];path=R/'scenes/MUDAM_R169_CEPHE_GEOMETRI_ADAY_v010.blend';bpy.ops.wm.open_mainfile(filepath=str(path));base=-74.35702575946969;bal=bpy.data.objects['R169_33_LEFT_BALCONIES'];bm=bmesh.new();bm.from_mesh(bal.data);flipped=0
for f in bm.faces:
 zs=[v.co.z for v in f.verts]
 if max(zs)-min(zs)<.00001:
  top=any(abs(zs[0]-(base+h))<.001 for h in [2.3,5.35])
  if (top and f.normal.z<0) or (not top and f.normal.z>0):f.normal_flip();flipped+=1
bm.to_mesh(bal.data);bm.free();bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));results=[]
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 assert all(math.isfinite(x) for v in o.data.vertices for x in v.co),o.name
 deg=sum(p.area<1e-9 for p in o.data.polygons);results.append(dict(name=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),zero_area_faces=deg));assert deg==0,(o.name,deg);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r169_geometry_review_v010.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False,export_extras=True)
(R/'reports/R169_GEOMETRY_REVIEW_v010.json').write_text(json.dumps(dict(scene=path.name,reopened=True,objects=results,balcony_normal_corrections=flipped,accepted=False,published=False,export='exports/r152_clean/r169_geometry_review_v010.glb',scope='Partial reconstruction review only. Source-visible central/side openings and two left balconies; four broad balcony glazing fields provisional. Unfinished right balconies, rear facade and roof dormers prevent production acceptance.'),indent=2));print('REVIEW_EXPORT_VERIFIED')
