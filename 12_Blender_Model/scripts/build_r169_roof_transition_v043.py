from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];d=json.loads((R/'.local_source_cache/r169/row_transition_grid.json').read_text());assert d['p90']<.08 and d['maximum']<.15;verts=d['vertices'];faces=d['faces'];ring=[Vector(verts[i]) for i in [0,8,80,72]];tree=BVHTree.FromPolygons([Vector(p) for p in verts],faces,all_triangles=True)
def inside(p):
 cr=[(q.x-a.x)*(p.y-a.y)-(q.y-a.y)*(p.x-a.x) for a,q in zip(ring,ring[1:]+ring[:1])];return min(cr)>-1e-5 or max(cr)<1e-5
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_ORTU_BIRLESIM_ADAY_v042.blend'));changes=[]
for name in ['R169_MEASURED_ENVELOPE','R169_ROW_CONTINUOUS_HIP','R169_ROW_REAR_ROOF_EXTENT']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data)
 for a,b in zip(ring,ring[1:]+ring[:1]):
  fs=[f for f in bm.faces if f.calc_center_median().z>-65] if name=='R169_MEASURED_ENVELOPE' else list(bm.faces)
  es={e for f in fs for e in f.edges};vs={v for f in fs for v in f.verts};bmesh.ops.bisect_plane(bm,geom=list(fs)+list(es)+list(vs),dist=1e-6,plane_co=a,plane_no=Vector((b.y-a.y,a.x-b.x,0)))
 drop=[]
 for f in bm.faces:
  p=f.calc_center_median()
  if not inside(p):continue
  h,*_=tree.ray_cast(Vector((p.x,p.y,50)),Vector((0,0,-1)),200)
  if h is not None and (name!='R169_MEASURED_ENVELOPE' or (abs(p.z-h.z)<.25 and f.normal.z>.35)):drop.append(f)
 changes.append(dict(object=name,removed_faces=len(drop)));bmesh.ops.delete(bm,geom=drop,context='FACES');bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(o.data);bm.free()
me=bpy.data.meshes.new('R169_SOURCE_SECTION_ROOF_TRANSITION');me.from_pydata(verts,[],faces);me.materials.append(bpy.data.objects['R169_ROW_CONTINUOUS_HIP'].data.materials[0]);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);bm=bmesh.new();bm.from_mesh(me);bm.normal_update()
for f in bm.faces:
 if f.normal.z<0:f.normal_flip()
bm.to_mesh(me);bm.free();
for name in ['R169_MEASURED_ENVELOPE','R169_ROW_CONTINUOUS_HIP','R169_ROW_REAR_ROOF_EXTENT','R169_SOURCE_SECTION_ROOF_TRANSITION']:
 obj=bpy.data.objects[name];obj.data.calc_loop_triangles();badids={tr.polygon_index for tr in obj.data.loop_triangles if tr.area<1e-9}
 if badids:
  bm=bmesh.new();bm.from_mesh(obj.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in badids],context='FACES_ONLY');bm.to_mesh(obj.data);bm.free()
out=R/'scenes/MUDAM_R169_KESITLI_CATI_GECISI_ADAY_v043.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R169_ROOF_TRANSITION_v043.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,source_samples=81,independent_checks=128,p90_m=d['p90'],max_error_m=d['maximum'],changes=changes,limits=['Section-derived roof surface; not imported scan mesh','Perimeter joins and inherited fragments need visual resolution','No whole roof or building acceptance']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-285,-48);s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_roof_transition_v043.png');bpy.ops.render.render(write_still=True)









