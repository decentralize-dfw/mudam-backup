"""Independent piecewise planar crest reconstruction, not a scan surface transfer."""
import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
src=R/'scenes/MUDAM_R314_ECCL_GUNEY_KOSE_OTURUM_ADAY_v001.blend'
out=R/'scenes/MUDAM_R317_KUZEY_SUR_KOT_ADAY_v002.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
o=bpy.data.objects['R152_HISTORIC_WALL_49911001'];old=[tuple(v.co) for v in o.data.vertices]
# Sparse architectural stations: stable visible coping observations at top-view pixels
# (700,212), (720,212), (740,212), (760,214), (800,214), (840,216), (860,216).
# Keep existing map centerline and width: their accuracy is not certified by these rays.
controls=[(-10.0,.20),(-6.857,.15),(-3.714,-.30),(18.3,-.36)]
def crest(x):
 for (a,za),(b,zb) in zip(controls,controls[1:]):
  if x<=b:return za+(zb-za)*(x-a)/(b-a)
 return controls[-1][1]
groups={}
for v in o.data.vertices:
 q=o.matrix_world@v.co;groups.setdefault((round(q.x,4),round(q.y,4)),[]).append((v,q))
samples=json.loads((R/'reports/R317_TERRACE_SAMPLES.json').read_text())['source']
valid=[p for p in samples if p['spread']<.2]
A=np.array([[*p['xy'],1] for p in valid]);z=np.array([p['medianZ'] for p in valid]);plane=np.linalg.lstsq(A,z,rcond=None)[0];residual=A@plane-z
assert max(abs(residual))<.15
changes=[];basechanges=[]
for group in groups.values():
 if len(group)<2:continue
 low=min(q.z for v,q in group);high=max(q.z for v,q in group)
 for v,q in group:
  if -10.2<=q.x<=18.3 and abs(q.z-high)<1e-5 and high-low>.1:
   before=q.z;q.z=crest(q.x);v.co=o.matrix_world.inverted()@q;changes.append(dict(vertex=v.index,xy=list(q)[:2],before=before,after=q.z))
  elif -10.2<=q.x<=18.3 and abs(q.z-low)<1e-5 and high-low>.1:
   before=q.z;q.z=min(q.z,float(plane@[q.x,q.y,1])-.4)
   if q.z<before-1e-6:v.co=o.matrix_world.inverted()@q;basechanges.append(dict(vertex=v.index,before=before,after=q.z))
assert changes
o.data.update();o['R317_method']='Sparse independent planar coping stations from visible ACT reference. No mesh or photo texture transfer.';o['R317_status']='Local crest candidate; bases, wall width and ground contact still require independent verification.'
# Regenerate metric UVs only on changed wall so moved coping does not stretch its masonry.
for layer in o.data.uv_layers:
 for f in o.data.polygons:
  n=f.normal;u=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.8 else Vector((1,0,0));v=n.cross(u).normalized()
  for li in f.loop_indices:
   q=o.data.vertices[o.data.loops[li].vertex_index].co;layer.data[li].uv=(q.dot(u)/4,q.dot(v)/3)
def check(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
 r=dict(boundary=sum(e.is_boundary for e in bm.edges),nonmanifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();return r
report=dict(scene=out.name,accepted=False,published=False,scope='North wall crest and buried base extension, approximately28.5m; complete museum ring remains unaccepted',controls=controls,changes=changes,baseExtensions=basechanges,groundPlane=dict(coefficients=plane.tolist(),samples=len(valid),maxResidual=float(max(abs(residual))),note='Independent sloping plane fitted to stable visible grass points; buried footing depth is not surveyed'),geometry=check(o),limits=['No surveyed accuracy or full-ring acceptance','Existing width and centerline retained pending wall-face measurement','Terrain unchanged; wall bases only extended downward to remove exposed gaps','ACT crest observations have local reconstruction uncertainty'])
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));o=bpy.data.objects["R152_HISTORIC_WALL_49911001"];report['reopen']=check(o)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
glb=R/'exports/r152_clean/r317_north_wall_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(0,46,5));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((0,61,-2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=45
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=650;s.render.resolution_percentage=100
s.world=bpy.data.worlds.new('R317_Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R317_north_wall_revised.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));report['glb']=[dict(name=ob.name,**check(ob)) for ob in bpy.context.scene.objects if ob.type=='MESH'];(R/'reports/R317_NORTH_WALL_RECONSTRUCTION.json').write_text(json.dumps(report,indent=2));print('R317_READY',report['geometry'],report['glb'])

