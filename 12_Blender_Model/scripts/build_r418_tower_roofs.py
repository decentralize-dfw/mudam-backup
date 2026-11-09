import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R417_KALE_ACIK_UC_ORTU_ADAY_v001.blend'));data=json.loads((R/'reports/R418_TOWER_CAP_PLANES.json').read_text());raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());changes=[]
for t in raw['towers']:
 label=t['name'];fit=data[label];assert fit['valid'];a,b=fit['coef'];r=t['radius']+.2;cx,cy=t['center'];eave=a+b*r;roof=t['roof'];old=bpy.data.objects['R154_TOWER_CAP_'+label];old.hide_render=True;old.hide_viewport=True;old.hide_set(True);vs=[];fs=[];n=128
 profile=[(r,eave),(.23,a+b*.23),(.23,a+b*.23-.10),(r,eave-.10)]
 for rr,z in profile:
  for j in range(n):u=2*math.pi*j/n;vs.append((cx+rr*math.cos(u),cy+rr*math.sin(u),z))
 for k in range(4):
  for j in range(n):fs.append((k*n+j,k*n+(j+1)%n,((k+1)%4)*n+(j+1)%n,((k+1)%4)*n+j))
 me=bpy.data.meshes.new('R418_TOWER_CONICAL_ROOF_'+label);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(old.data.materials[0]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for f in me.polygons:f.use_smooth=True
 ob['level_id']='SITE';ob['source']='Independent conical roof fitted to classified ACT 2024 controls, Zinneke rooftop photos confirm slope. No source mesh or photograph transferred.'
 name='R407_CENTRAL_TOWER_BODY' if label=='CENTRE' else 'R154_TOWER_'+label;body=bpy.data.objects[name];delta=eave-roof;changed=0
 for v in body.data.vertices:
  if v.co.z>roof-.6:v.co.z+=delta*min(1,(v.co.z-(roof-.6))/.6);changed+=1
 body.data.update();acorn=bpy.data.objects['R154_ACORN_'+label];acorn.location.z+=(a+b*.23)-(roof+.26)
 changes.append(dict(tower=label,cap=ob.name,eave=eave,oldEave=roof,corniceDelta=delta,corniceVertices=changed,fit={k:v for k,v in fit.items() if k!='samples'}))
out=R/'scenes/MUDAM_R418_KALE_OLCULU_KULE_CATILARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for row in changes:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[row['cap']].data);checks.append(dict(name=row['cap'],nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(v['nonManifold'] or v['zeroArea'] for v in checks)
(R/'reports/R418_TOWER_ROOFS.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changes=changes,checks=checks,limits=['Conical profile supported by held-out classified returns; decorative acorn shape remains inherited and not measured.','Whole museum ring remains incomplete.']),indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-46,-37,5.4));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-61.6,-53.15,3.1))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=35;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R418_roof_eye.png');bpy.ops.render.render(write_still=True)
