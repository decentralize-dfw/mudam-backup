from pathlib import Path
import bpy,json
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R157_ARAZI_YOLLAR_AGACLAR_v003.blend'))
changed=[]
for me in list(bpy.data.meshes):
 if not me.name.startswith('R157_TREE_PROTOTYPE_False_'):continue
 vertices=[tuple(v.co) for v in me.vertices]; faces=[]; materials=[]; polygons=list(me.polygons); i=0
 while i<len(polygons):
  p=polygons[i]
  if p.material_index==0:
   faces.append(tuple(p.vertices));materials.append(0);i+=1
  else:
   q=polygons[i+1];a=list(p.vertices);b=list(q.vertices)
   assert a[0]==b[0] and a[3]==b[1]
   faces.append((a[0],a[1],a[3],b[2]));materials.append(p.material_index);i+=2
 new=bpy.data.meshes.new(me.name+'_WEB');new.from_pydata(vertices,[],faces);new.update()
 for m in me.materials:new.materials.append(m)
 for p,slot in zip(new.polygons,materials):p.material_index=slot;p.use_smooth=slot==0
 users=[o for o in bpy.data.objects if o.type=='MESH' and o.data==me]
 for o in users:o.data=new
 changed.append({'prototype':me.name,'instances':len(users),'leaves':sum(m!=0 for m in materials)})
assert len(changed)==4,changed
out=R/'scenes/MUDAM_R157_ARAZI_YOLLAR_AGACLAR_v004.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.name.startswith('R157_TREE_'):o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/vegetation.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
r=json.loads((R/'reports/R157_BUILD.json').read_text());r.update(scene=out.name,far_leaf_optimization=changed,near_tree_geometry_unchanged=True)
(R/'reports/R157_BUILD.json').write_text(json.dumps(r,indent=2))
print('R157_FAR_LEAVES_OPTIMIZED',changed,flush=True)
