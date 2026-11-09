import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R501_BATI_SUR_AGAC_KOTU_DUZELTME_ADAY_v001.blend'));d=json.loads((R/'reports/R504_SOUTH_ROOF_PARAMETERS.json').read_text());cx,cy,r=d['edge']['fit'];a,b=d['roofPlane'];oldcenter=Vector((-57.4,-63.1));center=Vector((cx,cy));ratio=r/4.7;eave=a+b*r;oldEave=4.9410600662231445;delta=eave-oldEave;changed=[]
for name in ['R424_SOUTH_TOWER_BODY','R424_SOUTH_BLIND_ARCADES','R424_SOUTH_RECESSED_DOOR']:
 o=bpy.data.objects[name]
 for v in o.data.vertices:
  q=o.matrix_world@v.co;xy=center+(Vector((q.x,q.y))-oldcenter)*ratio;q.x,q.y=xy;q.z+=delta*max(0,min(1,(q.z-1.4464751482)/(oldEave-1.4464751482)));v.co=o.matrix_world.inverted()@q
 o.data.update();changed.append(name)
o=bpy.data.objects['R446_SOUTH_CORBEL_BELT']
for v in o.data.vertices:
 q=o.matrix_world@v.co;w=max(0,min(1,(q.z-1.06647515)/.28));xy=Vector((q.x,q.y));target=center+(xy-oldcenter)*ratio;xy=xy.lerp(target,w);q.x,q.y=xy;v.co=o.matrix_world.inverted()@q
o.data.update();changed.append(o.name)
o=bpy.data.objects['R418_TOWER_CONICAL_ROOF_SOUTH'];me=o.data;n=128
for k,(rr,z) in enumerate([(r,eave),(.23,a+b*.23),(.23,a+b*.23-.10),(r,eave-.10)]):
 for j in range(n):u=math.tau*j/n;me.vertices[k*n+j].co=(cx+rr*math.cos(u),cy+rr*math.sin(u),z)
me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();normals=[None]*len(me.loops)
for f in me.polygons:
 for li in f.loop_indices:
  q=me.vertices[me.loops[li].vertex_index].co;u=Vector((q.x-cx,q.y-cy,0)).normalized()
  normal=Vector((-b*u.x,-b*u.y,1)).normalized() if f.normal.z>.5 else -Vector((-b*u.x,-b*u.y,1)).normalized() if f.normal.z<-.5 else u*(1 if f.normal.dot(u)>0 else -1)
  normals[li]=normal
 f.use_smooth=True
me.normals_split_custom_set(normals);changed.append(o.name)
o=bpy.data.objects['R425_SOUTH_ACORN_FINIAL'];o.location.x+=cx+57.4;o.location.y+=cy+63.1;o.location.z+=(a+b*.23)-5.94629430770874;changed.append(o.name)
checks=[]
for name in changed:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);row=dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();checks.append(row)
assert not any(v['nonManifold'] or v['zeroArea'] for v in checks),checks
out=R/'scenes/MUDAM_R504_GUNEY_KULE_CATISI_OTURUM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));roof=bpy.data.objects['R418_TOWER_CONICAL_ROOF_SOUTH'];body=bpy.data.objects['R424_SOUTH_TOWER_BODY'];top=max((body.matrix_world@v.co).z for v in body.data.vertices);assert abs(top-eave)<1e-5;(R/'reports/R504_BUILD.json').write_text(json.dumps(dict(changed=changed,checks=checks,reopened=True,eave=eave,bodyTop=top,roofBodyVerticalGap=abs(top-eave),oldRadius=4.7,newRadius=r,accepted=False,published=False,parameters='R504_SOUTH_ROOF_PARAMETERS.json'),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=950;s.render.resolution_y=950;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-64,-55,70));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-64,-55,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=34;s.render.filepath=str(R/'renders/qa/R504_tower_roofs_candidate.png');bpy.ops.render.render(write_still=True)
