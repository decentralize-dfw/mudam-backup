import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R331_DIS_HENDEK_TABAN_ADAY_v001.blend'))
data=json.loads((R/'reports/R331_OUTER_MOAT_PLANES.json').read_text())
targets={'north_nw':['R152_RUIN_PARTITION_00','R152_HISTORIC_WALL_759551379'],'north_ne':['R152_RUIN_PARTITION_00'],'east_north':['R152_HISTORIC_WALL_453755312','R152_RUIN_PARTITION_10'],'east_side_upper':['R152_HISTORIC_WALL_453755312','R152_RUIN_PARTITION_10']};changes=[]
for region,names in targets.items():
 row=data[region];assert row['valid'];poly=row['outline'];a,b,c=row['plane'];n=len(poly)
 vs=[(x,y,a*x+b*y+c-.05) for x,y in poly]+[(x,y,5) for x,y in poly];faces=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new('Verified moat clearance');me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();cut=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(cut)
 for name in names:
  ob=bpy.data.objects[name];before=len(ob.data.polygons);bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Remove intrusion in measured moat','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);ob['R334_scope']='Remove only intersection with measured R331 moat floor extrusion; keep outside geometry.';changes.append(dict(name=name,region=region,beforeFaces=before,afterFaces=len(ob.data.polygons)))
 bpy.data.objects.remove(cut,do_unlink=True)
checks=[]
for name in sorted({n for ns in targets.values() for n in ns}):
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
out=R/'scenes/MUDAM_R334_HENDEK_CAKISMA_TEMIZLIK_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/'reports/R334_MOAT_CLEARANCE.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changes=changes,meshChecks=checks,limits=['Clearance only; outer coping layout and wall widths still require source refinement.']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
for label,x,y,scale in [('north',-35,68,44),('east',60,-30,42)]:
 bpy.ops.object.camera_add(location=(x,y,70));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((x,y,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=scale;s.render.filepath=str(R/f'renders/qa/R334_{label}_ruin.png');bpy.ops.render.render(write_still=True)
print('R334_READY',checks)
