import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R253_OVAL_KAVISLI_CEPHE_ADAY_v001.blend'));d=json.loads((R/'config/r252_oval_architecture.json').read_text());old=[Vector(p) for p in d['outer']];smooth=set(list(range(2,6))+list(range(8,14))+list(range(16,20))+list(range(22,27)));glazed=set(list(range(8,14))+list(range(16,20))+list(range(22,27)));ring=[];tags=[]
for i,p1 in enumerate(old):
 p0=old[(i-1)%len(old)];p2=old[(i+1)%len(old)];p3=old[(i+2)%len(old)];n=max(1,math.ceil((p2-p1).length/1.3))
 for j in range(n):
  t=j/n
  p=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t) if i in smooth else p1.lerp(p2,t)
  ring.append(p);tags.append(i)
area=sum(a.x*b.y-b.x*a.y for a,b in zip(ring,ring[1:]+ring[:1]));inner=[]
for i,p in enumerate(ring):
 a=(p-ring[i-1]).normalized();b=(ring[(i+1)%len(ring)]-p).normalized();na=Vector((-a.y,a.x))*(1 if area>0 else -1);nb=Vector((-b.y,b.x))*(1 if area>0 else -1);nn=(na+nb).normalized();inner.append(p+nn*.4/max(.35,nn.dot(nb)))

from mathutils.geometry import tessellate_polygon
stone=bpy.data.materials['R252_PALE_LIMESTONE'];roofmat=bpy.data.materials['R252_GRAVEL'];metal=bpy.data.materials['R252_LIGHT_FRAMES'];level=json.loads((R/'reports/R252_OVAL_ARCHITECTURE.json').read_text())['roofLevel']
def mesh(name,v,f,m):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.materials.append(m);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def prism(name,points,z0,z1,m):
 poly=[Vector((p[0],p[1],0)) for p in points];n=len(poly);v=[(p.x,p.y,z) for z in [z0,z1] for p in poly];f=[]
 for tri in tessellate_polygon([poly]):
  ids=[q if isinstance(q,int) else min(range(n),key=lambda i:(poly[i]-q).length_squared) for q in tri];f.extend([tuple(reversed(ids)),tuple(i+n for i in ids)])
 f.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n));return mesh(name,v,f,m)
for name in ['R252_OVAL_ROOF_DECK','R253_OVAL_FLOOR']:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
deck=prism('R254_OVAL_MATCHED_ROOF',ring,level-.20,level+.08,roofmat);prism('R254_OVAL_MATCHED_FLOOR',ring,8.5,8.8,stone)
secs=d['sections'];hole=[r['left'] for r in secs]+[r['right'] for r in secs[::-1]];c=prism('CUT',hole,level-.5,40,stone);bpy.context.view_layer.objects.active=deck;m=deck.modifiers.new('Atrium opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
import numpy as np
coef=json.loads((R/'reports/R252_OVAL_ARCHITECTURE.json').read_text())['ridgeCoefficients'];ts=np.linspace(-1,1,len(secs));left=[Vector((*r['left'],30)) for r in secs];right=[Vector((*r['right'],30)) for r in secs];ridge=[(a+b)/2 for a,b in zip(left,right)]
for i,p in enumerate(ridge):p.z=float(np.polyval(coef,ts[i]))
vv=[];ff=[]
for side,outer in enumerate([left,right]):
 for frac in [1/3,2/3]:
  rail=[a.lerp(b,frac) for a,b in zip(outer,ridge)]
  for a,b in zip(rail,rail[1:]):
   u=(b-a).normalized();v=u.cross(Vector((0,0,1))).normalized();w=u.cross(v).normalized();k=len(vv);vv.extend(tuple(p+v*x+w*y) for p in [a,b] for x,y in [(-.025,-.025),(.025,-.025),(.025,.025),(-.025,.025)]);ff.extend(tuple(k+j for j in f) for f in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
mesh('R254_ATRIUM_LONGITUDINAL_FRAMES',vv,ff,metal)
scene=R/'scenes/MUDAM_R254_OVAL_BUTUNLESIK_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;t=Vector((320,398,20));s.camera.location=t+Vector((80,-100,80));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=100;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R254_oval_integrated.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith(('R252_','R253_','R254_')))
glb=R/'exports/r152_clean/r254_oval_architecture_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(not c['boundary'] and not c['zero'] for c in checks)
(R/'reports/R254_OVAL_INTEGRATED.json').write_text(json.dumps(dict(accepted=False,published=False,checks=checks,roofBoundary='Shared smoothed facade footprint; inherited polygon deck replaced',limits=['Source comparison of unseen lower/rear facade still unresolved','Foundation contacts not yet verified','Roof mechanical housings/end details not yet reconstructed','No region6 or first-six completion claim']),indent=2));print('R254_READY',len(checks),flush=True)
