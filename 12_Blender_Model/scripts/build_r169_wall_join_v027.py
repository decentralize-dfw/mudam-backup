from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';rows=[r for r in json.loads((D/'row_eave_normal_samples.json').read_text()) if r['edge']==2 and r['inset']==0];a=Vector((rows[0]['x'],rows[0]['y'],0));b=Vector((rows[-1]['x'],rows[-1]['y'],0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));n=n if (Vector((-67,-299,0))-a).dot(n)>0 else -n;length=(b-a).length
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_KAYNAK_SACAK_ADAY_v026.blend'));roof=bpy.data.objects['R169_ROW_CONTINUOUS_HIP'];roof.data.calc_loop_triangles();tree=BVHTree.FromPolygons([roof.matrix_world@v.co for v in roof.data.vertices],[list(tr.vertices) for tr in roof.data.loop_triangles],all_triangles=True);body=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(body.data);verts=[];faces=[];distances=[]
for e in bm.edges:
 if not e.is_boundary:continue
 p=(e.verts[0].co+e.verts[1].co)/2;u=(p-a).dot(t);depth=(p-a).dot(n);normal=e.link_faces[0].normal
 if not(0<u<length and -.05<depth<.6 and -65.5<p.z<-62 and abs(normal.z)<.35 and normal.dot(-n)>.5):continue
 if abs((e.verts[1].co-e.verts[0].co).dot(t))<.02:continue
 old=[v.co.copy() for v in e.verts];new=[]
 for v in old:
  q=v.copy();dep=(q-a).dot(n)
  if dep<.002:q+=n*(.002-dep)
  h,*_=tree.ray_cast(Vector((q.x,q.y,50)),Vector((0,0,-1)),200)
  if h is None or h.z-v.z<-.08 or h.z-v.z>1.2:break
  new.append(h)
 if len(new)!=2:continue
 if max((p-q).length for p,q in zip(new,old))<.001:continue
 off=len(verts);verts.extend([tuple(old[0]),tuple(old[1]),tuple(new[1]),tuple(new[0])]);faces.append([off,off+1,off+2,off+3]);distances.extend((p-q).length for p,q in zip(new,old))
bm.free();me=bpy.data.meshes.new('R169_ROW_EAVE_WALL_JOIN');me.from_pydata(verts,[],faces);me.update();obj=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(obj);mat=bpy.data.materials.new('R169_ROW_EAVE_JOIN_STONE');mat.use_nodes=True;mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.39,.40,.37,1);mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;me.materials.append(mat);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));small=[f for f in bm.faces if f.calc_area()<1e-9]
if small:bmesh.ops.delete(bm,geom=small,context='FACES_ONLY')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();out=R/'scenes/MUDAM_R169_SACAK_DUVAR_BAG_ADAY_v027.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));report=dict(scene=out.name,accepted=False,published=False,joined_edges=len(faces),max_connector_length_m=max(distances) if distances else 0,scope='Only outward-facing near-eave wall boundary edges connected to source-derived roof; inherited meshes unchanged; no roof feature snapping',limits=['Connection geometry between modeled surfaces, not measured cornice section','Remaining source fragments and roof feature seams require review']);(R/'reports/R169_WALL_JOIN_v027.json').write_text(json.dumps(report,indent=2));print('EAVE_JOIN',report,flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-320,-45);s.camera.rotation_euler=(Vector((-67,-299,-66))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_row_roof_v027.png');bpy.ops.render.render(write_still=True)
