import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R487_KUZEYBATI_ALT_GECIT_ADAY_v001.blend'));log=[]
o=bpy.data.objects['R485_NW_HISTORIC_RETAINING_WALL'];o.data.uv_layers.active.name='R55_CONTEXT_METRIC_UV';log.append('Historic wall UV name now matches material explicit UV node.')
o=bpy.data.objects['R485_NW_LAWN'];me=o.data;uv=me.uv_layers.get('UVMap');micro=me.uv_layers.get('MicroUV') or me.uv_layers.new(name='MicroUV')
for l in me.loops:
 v=o.matrix_world@me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x+500)/1150,(v.y+450)/1100);micro.data[l.index].uv=(v.x/6,v.y/6)
me.uv_layers.active=uv;log.append('Lawn uses same georeferenced landcover atlas UV and 6m micro normal UV as surrounding terrain; recovered affine residual <1e-6.')
o=bpy.data.objects['R487_NW_MINERAL_PASSAGE'];me=o.data;N=len(me.vertices)//2
for v in list(me.vertices)[N:]:v.co.z=-8
me.materials.append(bpy.data.materials['R129_HISTORIC_MASONRY_APPEARANCE_CANDIDATE']);uv=me.uv_layers.new(name='R55_CONTEXT_METRIC_UV')
me.update()
for p in me.polygons:
 if abs(p.normal.z)<.5:p.material_index=1
 for i in p.loop_indices:
  v=me.vertices[me.loops[i].vertex_index].co;uv.data[i].uv=((v.x+v.y)/5.656854,v.z/3)
log.append('Passage underside extended below adjacent ground as hidden structural closure, not claimed surveyed foundation.')
checks={}
for name in ['R485_NW_LAWN','R485_NW_HISTORIC_RETAINING_WALL','R486_NW_COURT_RETAINING_EDGE','R487_NW_MINERAL_PASSAGE']:
 me=bpy.data.objects[name].data;bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));checks[name]={'nonManifold':sum(not e.is_manifold for e in bm.edges),'zeroArea':sum(f.calc_area()<1e-10 for f in bm.faces)};bm.to_mesh(me);bm.free();assert not any(checks[name].values()),(name,checks[name])
out=R/'scenes/MUDAM_R488_AVLU_SUR_MALZEME_BAGLANTI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R488_BUILD.json').write_text(json.dumps(dict(changes=log,checks=checks,reopened=True,accepted=False,published=False),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-80,0,35));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-48,37,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=43;s.render.filepath=str(R/'renders/qa/R488_northwest_oblique.png');bpy.ops.render.render(write_still=True)
