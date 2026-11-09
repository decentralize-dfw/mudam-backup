from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model')
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R217_ERASMUS_YEDI_KANAT_ADAY_v001.blend'))
vs=[];fs=[]
for name in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN']:
 o=bpy.data.objects.get(name)
 if not o:continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices]for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
measure=json.loads((R/'config/r218_front_volumes_measured.json').read_text());d={'parts':[p for p in measure['parts'] if p['supported']]};col=bpy.data.collections.new('R218_ERASMUS_FRONT_VOLUMES');bpy.context.scene.collection.children.link(col)
mat=bpy.data.materials.new('R218_UNRESOLVED_FACADE');mat.diffuse_color=(.54,.49,.43,1)
records=[]
for row in d['parts']:
 pts=row['polygon'];roof=row['roof'];bases=[]
 for x,y in pts:
  hit=g.ray_cast(Vector((x,y,80)),Vector((0,0,-1)),200)[0]
  if hit is None:raise RuntimeError('Missing ground')
  bases.append(hit.z-.05)
 if max(bases)>=roof-.5:raise RuntimeError('Invalid envelope height')
 verts=[(x,y,z)for (x,y),z in zip(pts,bases)]+[(x,y,roof)for x,y in pts]
 faces=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)]
 me=bpy.data.meshes.new('R218_ERASMUS_FRONT_'+str(row['id']));me.from_pydata(verts,[],faces);me.materials.append(mat);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);assert not any(e.is_boundary for e in bm.edges);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);col.objects.link(o)
 records.append(dict(name=o.name,roof=roof,groundContactBases=bases,closed=True,openingsModeled=False))
path=R/'scenes/MUDAM_R218_ERASMUS_ON_KUTLE_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for o in bpy.context.scene.objects:o.select_set(o.name.startswith(('R216_ERASMUS_WING_','R217_ERASMUS_WING_','R218_ERASMUS_FRONT_')))
glb=R/'exports/r152_clean/r218_erasmus_envelope_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert len(checks)==10 and all(not c['boundary'] and not c['zero']for c in checks)
report=dict(accepted=False,published=False,scope='Seven upper wings and three source-supported lower street-facing volumes; incomplete architecture',records=records,reopen=checks,method='Independently constructed planar closed volumes; scalar measured roofs and current terrain contact',limits=['Blank facade envelopes are study only; actual windows doors and frames still missing','Remaining wings rear circulation and courtyard construction missing','Ground contact follows current modeled terrain, not surveyed facade base heights','Do not publish as accepted architecture or replace R213 production'])
(R/'reports/R218_ERASMUS_ENVELOPES.json').write_text(json.dumps(report,indent=2))
p=R/'config/context_reconstruction_queue.json';q=json.loads(p.read_text());q['next_actions'].insert(0,'R218 local candidate adds3street-facing lower volumes at7.994,8.027,8.083m fromsource, attached to correspondingR217wings. Ten meshes closed afterGLBreopen. Four otherfront spans failed0.2m residual test and were not invented; investigate sloped roofs/edge traces. Actual facades, rearstrip, courtyards remain incomplete. ProductionR213 unchanged.');p.write_text(json.dumps(q,indent=2)+'\n')
print('R218_LOCAL_CANDIDATE',checks,flush=True)
