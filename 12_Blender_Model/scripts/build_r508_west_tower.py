import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R507_GUNEY_KULE_ZEMIN_TEMASI_ADAY_v001.blend'));d=json.loads((R/'reports/R508_WEST_TOWER_PARAMETERS.json').read_text());cx,cy=d['center'];r=d['radius'];a,b=d['roofPlane'];oldcenter=Vector((-71.5,-47.6));center=Vector((cx,cy));ratio=r/4.7;eave=a+b*r;oldEave=5.125725746154785;delta=eave-oldEave;changed=[]
for name in ['R424_WEST_TOWER_BODY','R424_WEST_BLIND_ARCADES']:
 o=bpy.data.objects[name]
 for v in o.data.vertices:
  q=o.matrix_world@v.co;xy=center+(Vector((q.x,q.y))-oldcenter)*ratio;q.x,q.y=xy;q.z+=delta*max(0,min(1,(q.z-1.4489598274)/(oldEave-1.4489598274)));v.co=o.matrix_world.inverted()@q
 o.data.update();changed.append(name)
o=bpy.data.objects['R446_WEST_CORBEL_BELT']
for v in o.data.vertices:
 q=o.matrix_world@v.co;w=max(0,min(1,(q.z-1.06895983)/.28));xy=Vector((q.x,q.y));target=center+(xy-oldcenter)*ratio;xy=xy.lerp(target,w);q.x,q.y=xy;v.co=o.matrix_world.inverted()@q
o.data.update();changed.append(o.name)
o=bpy.data.objects['R418_TOWER_CONICAL_ROOF_WEST'];me=o.data;n=128
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
o=bpy.data.objects['R425_WEST_ACORN_FINIAL'];o.location.x+=cx+71.5;o.location.y+=cy+47.6;o.location.z+=(a+b*.23)-6.031954765319824;changed.append(o.name)

c=json.loads((R/'reports/R399_FRONT_COURT_PLANES.json').read_text())['tower_forecourt']['plane']
for partIndex,part in enumerate(d['contact']):
 points=[];lookup={};faces=[]
 def index(x,y,z):
  key=(round(x,7),round(y,7),round(z,7))
  if key not in lookup:lookup[key]=len(points);points.append(key)
  return lookup[key]
 def level(x,y):return c[0]*x+c[1]*y+c[2]-.012
 for tri in part['triangles']:
  faces.append(tuple(index(x,y,level(x,y)) for x,y in tri));faces.append(tuple(index(x,y,level(x,y)-.12) for x,y in reversed(tri)))
 ring=part['outline']
 for i,(x,y) in enumerate(ring):
  xx,yy=ring[(i+1)%len(ring)];faces.append((index(x,y,level(x,y)),index(xx,yy,level(xx,yy)),index(xx,yy,level(xx,yy)-.12),index(x,y,level(x,y)-.12)))
 name='R508_WEST_COURT_CONTACT_'+str(partIndex);me=bpy.data.meshes.new(name);me.from_pydata(points,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials['R402_LOW_COURT_GRASS']);o['level_id']='SITE';o['source']='Measured court plane fills old tower-foot domain uncovered by registered axis correction; original surrounding ground preserved.';changed.append(name)

checks=[]
for name in changed:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);row=dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();checks.append(row)
assert not any(v['nonManifold'] or v['zeroArea'] for v in checks),checks
out=R/'scenes/MUDAM_R508_BATI_KULE_EKSEN_ZEMIN_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));roof=bpy.data.objects['R418_TOWER_CONICAL_ROOF_WEST'];body=bpy.data.objects['R424_WEST_TOWER_BODY'];top=max((body.matrix_world@v.co).z for v in body.data.vertices);assert abs(top-eave)<1e-5;(R/'reports/R508_BUILD.json').write_text(json.dumps(dict(changed=changed,checks=checks,reopened=True,eave=eave,bodyTop=top,roofBodyVerticalGap=abs(top-eave),oldRadius=4.7,newRadius=r,accepted=False,published=False,parameters='R508_WEST_TOWER_PARAMETERS.json'),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=950;s.render.resolution_y=950;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-64,-55,70));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-64,-55,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=34;s.render.filepath=str(R/'renders/qa/R508_tower_roofs_candidate.png');bpy.ops.render.render(write_still=True)
