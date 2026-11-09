from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_TERAS_ADAY_v003.blend'));data=json.loads((R/'reports/R172_TERRACES_v003.json').read_text());changes=[]
for row in data['terraces']:
 if not row['accepted']:continue
 xy=row['xy'];n=len(xy);plane=row['plane'];origin=row['origin'];zs=[plane[0]*(x-origin[0])+plane[1]*(y-origin[1])+plane[2] for x,y in xy];verts=[(x,y,z+.04) for (x,y),z in zip(xy,zs)]+[(x,y,160) for x,y in xy];faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 for tri in tessellate_polygon([[Vector((x,y,0)) for x,y in xy]]):
  ix=list(tri);faces.extend([tuple(reversed(ix)),tuple(j+n for j in ix)])
 me=bpy.data.meshes.new('CUT_MOAT');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();c=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(c)
 for obj in list(bpy.context.scene.objects):
  if obj.type!='MESH' or not (obj.name in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN'] or obj.name.startswith('R152_PATH_')):continue
  box=[obj.matrix_world@Vector(p) for p in obj.bound_box]
  if any(max(p[k] for p in box)<min(v[k] for v in verts) or min(p[k] for p in box)>max(v[k] for v in verts) for k in range(3)):continue
  before=len(obj.data.polygons);bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Source-traced moat void','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name)
  if before!=len(obj.data.polygons):changes.append([obj.name,before,len(obj.data.polygons)])
 bpy.data.objects.remove(c,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_HENDEK_ADAY_v004.blend'),compress=True)
s=bpy.context.scene;target=Vector((-210,-175,-35));s.camera.location=target+Vector((70,-150,180));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=280;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R172_fort_moat_v004.png');bpy.ops.render.render(write_still=True)
(R/'reports/R172_MOAT_CUT_v004.json').write_text(json.dumps(dict(accepted=False,changes=changes,pending=['Moat retaining side junctions','Remaining moat and terrace levels','Full reference comparison']),indent=2));print('MOAT_CUT',changes)

