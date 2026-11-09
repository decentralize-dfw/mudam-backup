import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R448_KALE_FOTOGRAF_MAZGAL_ACIKLIKLARI_ADAY_v001.blend'));o=bpy.data.objects['R154_FORT_MASONRY_BODY'];fits=json.loads((R/'reports/R445_CLASS1_BASTION_FITS.json').read_text());raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());front=Vector((-raw['direction'][0],-raw['direction'][1]));me=o.data;normals=[None]*len(me.loops);count=0
for face in me.polygons:
 selected=None
 for row in fits:
  cx,cy,a,b=row['fit'];valid=True
  for vi in face.vertices:
   p=me.vertices[vi].co;d=Vector((p.x-cx,p.y-cy));r=d.length
   if r<.1 or abs(r-(a+b*p.z))>.15 or d.normalized().dot(front)<.25:valid=False;break
  if valid:selected=row['fit'];break
 face.use_smooth=True
 for li in face.loop_indices:
  if selected:
   cx,cy,a,b=selected;p=me.vertices[me.loops[li].vertex_index].co;r=math.hypot(p.x-cx,p.y-cy);n=Vector(((p.x-cx)/r,(p.y-cy)/r,-b)).normalized();normals[li]=tuple(n)
  else:normals[li]=tuple(face.normal)
 if selected:count+=1
me.normals_split_custom_set(normals);me.update();out=R/'scenes/MUDAM_R451_KALE_BURC_YUZEY_NORMALLERI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(R/'reports/R451_BASTION_NORMALS.json').write_text(json.dumps(dict(scene=out.name,analyticOuterFaces=count,vertexPositionsChanged=False,source='R445 architectural cone normal; recess and straight wall faces remain planar. Removes aperture-to-base smoothing streaks.',accepted=False,published=False),indent=2));print('R451_SAVED',count,flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-107,-92,6));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-63,-54,1.7))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=50;s.render.filepath=str(R/'renders/qa/R451_front_candidate.png');bpy.ops.render.render(write_still=True)
