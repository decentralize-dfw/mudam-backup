from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
def tree(objects):
 vs=[];fs=[]
 for o in objects:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in f.vertices] for f in o.data.loop_triangles)
 return BVHTree.FromPolygons(vs,fs,all_triangles=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r169/source.blend'));source=tree(list(bpy.context.scene.objects))
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_CATI_UZANTI_ADAY_v039.blend'));roof=tree([bpy.data.objects[n] for n in ['R169_ROW_CONTINUOUS_HIP','R169_ROW_REAR_ROOF_EXTENT']]);o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data);drop=[];evidence=[];tested=0
for f in bm.faces:
 p=f.calc_center_median()
 if not(-74<p.x<-60 and -306<p.y<-290 and p.z>-65):continue
 h,*_=roof.ray_cast(Vector((p.x,p.y,50)),Vector((0,0,-1)),200)
 if h is None or p.z-h.z<.2:continue
 tested+=1;checks=[]
 for q in [p]+[p.lerp(v.co,.8) for v in f.verts]:
  sr,*_=source.ray_cast(Vector((q.x,q.y,50)),Vector((0,0,-1)),200);rr,*_=roof.ray_cast(Vector((q.x,q.y,50)),Vector((0,0,-1)),200)
  if sr is None or rr is None:break
  checks.append(dict(candidate_above_source=q.z-sr.z,source_roof_residual=sr.z-rr.z))
 if len(checks)==len(f.verts)+1 and all(v['candidate_above_source']>.2 and abs(v['source_roof_residual'])<.18 for v in checks):drop.append(f);evidence.append(dict(center=list(p),area=f.calc_area(),samples=checks))
report=dict(tested_faces=tested,unsupported_faces=len(drop),evidence=evidence,accepted=False,published=False,method='All centroid and80percent vertex samples must be >0.2m above ACT, with ACT within0.18m of authored roof at every sample. Only existing authored roof coverage considered.')
print('SOURCE_CLASSIFICATION',tested,len(drop),flush=True)
(R/'reports/R169_UNSUPPORTED_ROOF_FACES.json').write_text(json.dumps(report,indent=2))
if not drop:bm.free();raise SystemExit('No confidently unsupported faces; scene not altered')
bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(o.data);bm.free();out=R/'scenes/MUDAM_R169_KAYNAK_DESTEKSIZ_PARCA_ADAY_v040.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-285,-48);s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_source_cleanup_v040.png');bpy.ops.render.render(write_still=True)






