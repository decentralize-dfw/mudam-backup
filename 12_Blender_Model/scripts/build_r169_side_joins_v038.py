from pathlib import Path
import bpy,bmesh,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_side_wall_plane.json').read_text());r=json.loads((R/'reports/R169_SIDE_WALL_v037.json').read_text());c=Vector(d['center']);n=Vector(d['inside']);t=Vector(d['right']);base=d['base'];coef=r['plane_coefficients'];u0,u1=-2.,4.5;z0=base+8.6
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_YAN_DUVAR_ADAY_v037.blend'));body=bpy.data.objects['R169_MEASURED_ENVELOPE'];band=bpy.data.objects['R169_ROW_SIDE_UPPER_BAND'];zmax=max(v.co.z for v in band.data.vertices);bm=bmesh.new();bm.from_mesh(body.data);vs=[];fs=[];lengths=[]
def target(p):
 u=(p-c).dot(t);return c+t*u+n*(coef[0]*u+coef[1]*(p.z-base-7.5)+coef[2])+Vector((0,0,p.z))
for e in bm.edges:
 if len(e.link_faces)!=1:continue
 a,b=[v.co.copy() for v in e.verts];us=[(p-c).dot(t) for p in (a,b)];ds=[(p-c).dot(n) for p in (a,b)]
 if min(us)<u0-.005 or max(us)>u1+.005 or min(a.z,b.z)<z0-.005 or max(a.z,b.z)>zmax+.005 or max(abs(x-d['offset']) for x in ds)>1:continue
 if not(any(max(abs(u-end) for u in us)<.005 for end in (u0,u1)) or max(abs(p.z-z0) for p in (a,b))<.005):continue
 aa,bb=target(a),target(b);width=max((aa-a).length,(bb-b).length)
 if width<.001 or width>.35:continue
 off=len(vs);vs.extend([tuple(a),tuple(b),tuple(bb),tuple(aa)]);fs.append([off+i for i in range(4)]);lengths.append(width)
bm.free();assert fs,'No compatible inherited boundary edges'
me=bpy.data.meshes.new('R169_ROW_SIDE_BAND_JOINS');me.from_pydata(vs,[],fs);me.materials.append(band.data.materials[0]);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9];bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.normal_update();bm.to_mesh(me);bm.free()
out=R/'scenes/MUDAM_R169_YAN_BAGLANTI_ADAY_v038.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R169_SIDE_JOINS_v038.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,joined_edges=len(fs),maximum_join_m=max(lengths),scope='Only inherited cut edges at side band ends and lower boundary; no roof or source geometry displaced',limits=['Inherited scan noise remains','Joins greater than0.35m excluded','Whole facade and roof remain unaccepted']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-50,-307,-43);s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_side_joins_v038.png');bpy.ops.render.render(write_still=True)




