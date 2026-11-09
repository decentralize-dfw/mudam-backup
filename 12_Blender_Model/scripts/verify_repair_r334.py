import bpy,bmesh,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
path=R/'scenes/MUDAM_R334_HENDEK_CAKISMA_TEMIZLIK_ADAY_v001.blend';bpy.ops.wm.open_mainfile(filepath=str(path));report=json.loads((R/'reports/R334_MOAT_CLEARANCE.json').read_text());checks=[]
for old in report['meshChecks']:
 ob=bpy.data.objects[old['name']]
 if old['nonManifold'] and ob.name=='R152_HISTORIC_WALL_453755312':
  # Two independently cut moat domains touch on a vertical edge. Resolve
  # this zero-width solid contact with a 20mm clearance at their junction.
  bpy.ops.mesh.primitive_cube_add(size=1,location=(69.03,-21.04,1.2));cut=bpy.context.object;cut.dimensions=(.02,.02,8);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Resolve zero width moat corner contact','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 bm=bmesh.new();bm.from_mesh(ob.data)
 if old['nonManifold']:
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.000001)
  loose=[e for e in bm.edges if not e.link_faces]
  if loose:bmesh.ops.delete(bm,geom=loose,context='EDGES')
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data)
 checks.append(dict(name=ob.name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
report['meshChecks']=checks;bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and (ob.name in {r['name'] for r in checks}|{'R326_NORTH_RUIN_CROSSWALL_02','R327_EAST_RUIN_CENTRAL_COURT','R152_CLASS2_TERRAIN','R152_PATH_759680913','R152_PATH_824216705'} or ob.name.startswith('R331_')):ob.select_set(True)
glb=R/'exports/r152_clean/r334_moat_clearance_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));bad=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':
  nonfinite=sum(not all(math.isfinite(x) for x in v.co) for v in ob.data.vertices);zero=sum(p.area<1e-10 for p in ob.data.polygons)
  if nonfinite or zero:bad.append(dict(name=ob.name,nonFinite=nonfinite,zeroArea=zero))
report['glbRoundtripErrors']=bad;report['glb']=str(glb.relative_to(R));report['reopened']=True
(R/'reports/R334_MOAT_CLEARANCE.json').write_text(json.dumps(report,indent=2));print('R334_VERIFIED',checks,bad)
