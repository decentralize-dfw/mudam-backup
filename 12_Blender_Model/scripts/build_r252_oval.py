import bpy,bmesh,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');d=json.loads((R/'config/r252_oval_architecture.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R251_NOVOTEL_CEPHE_BOLUNME_ADAY_v001.blend'))
def mat(name,color,rough,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
stone=mat('R252_PALE_LIMESTONE',(.58,.57,.50),.8);roofmat=mat('R252_GRAVEL',(.22,.205,.17),.94);glass=mat('R252_ATRIUM_GLASS',(.12,.28,.34),.22,.25);metal=mat('R252_LIGHT_FRAMES',(.58,.62,.61),.36,.65)
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(m);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def prism(name,ring,z0,z1,m):
 n=len(ring);v=[(x,y,z) for z in [z0,z1] for x,y in ring];vv=[Vector((x,y,0)) for x,y in ring];f=[]
 for tri in tessellate_polygon([vv]):
  ids=[q if isinstance(q,int) else min(range(n),key=lambda i:(vv[i]-q).length_squared) for q in tri];f.extend([tuple(reversed(ids)),tuple(i+n for i in ids)])
 f.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n));return mesh(name,v,f,m)
def cut(o,c):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Architectural void','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
# Remove only the disconnected oval component from inherited R166 reference envelope.
o=bpy.data.objects.get('R166_MEASURED_ENVELOPE')
removed=0
if o:
 bm=bmesh.new();bm.from_mesh(o.data);verts=[v for v in bm.verts if (o.matrix_world@v.co).y>340];removed=len(verts);bmesh.ops.delete(bm,geom=verts,context='VERTS');bm.to_mesh(o.data);bm.free()
ring=d['outer'];level=float(np.median([p['z'] for p in d['roofObservations']]));body=prism('R252_OVAL_MAIN_BODY',ring,8.5,level,stone)
sections=d['sections'];inner=[s['left'] for s in sections]+[s['right'] for s in sections[::-1]]
# Closed roof annulus and full-height inner court walls, with a separate atrium cover.
cut(body,prism('ATRIUM_VOID',inner,9,40,stone));deck=prism('R252_OVAL_ROOF_DECK',ring,level,level+.08,roofmat);cut(deck,prism('ROOF_VOID',inner,level-.1,40,stone))
t=np.linspace(-1,1,len(sections));coef=np.polyfit(t,[s['ridgeZ'] for s in sections],2);eave=30.0
left=[Vector((*s['left'],eave)) for s in sections];right=[Vector((*s['right'],eave)) for s in sections];ridge=[(a+b)/2 for a,b in zip(left,right)]
for i,p in enumerate(ridge):p.z=float(np.polyval(coef,t[i]))
verts=[];faces=[]
for rail0,rail1 in [(left,ridge),(ridge,right)]:
 for i in range(len(sections)-1):
  q=[rail0[i],rail0[i+1],rail1[i+1],rail1[i]];k=len(verts);verts.extend(tuple(p) for p in q);verts.extend(tuple(p-Vector((0,0,.06))) for p in q);faces.extend(tuple(k+j for j in f) for f in [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
mesh('R252_PITCHED_ATRIUM_GLASS',verts,faces,glass)
# Closed vertical eaves join the raised cover to the main roof; real atrium remains under glazing.
for side,rail in [('L',left),('R',right)]:
 for i,(a,b) in enumerate(zip(rail,rail[1:])):
  u=Vector((b.x-a.x,b.y-a.y,0)).normalized();n=Vector((-u.y,u.x,0))*.06;p=[(a.x,a.y),(b.x,b.y),(b.x+n.x,b.y+n.y),(a.x+n.x,a.y+n.y)];prism(f'R252_ATRIUM_EAVE_{side}_{i}',p,level,30.0,glass)
for index in [0,len(sections)-1]:
 a,c,b=left[index],ridge[index],right[index];u=(b-a).normalized();n=Vector((-u.y,u.x,0))*.06;q=[Vector((a.x,a.y,level)),a,c,b,Vector((b.x,b.y,level))];v=[tuple(p) for p in q]+[tuple(p+n) for p in q];f=[(4,3,2,1,0),(5,6,7,8,9)]+[(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)];mesh('R252_ATRIUM_END_'+str(index),v,f,glass)
# Architectural roof ribs follow the independently fitted roof, not scan triangles.
def beam(name,a,b):
 direction=b-a;u=direction.normalized();v=u.cross(Vector((0,0,1)))
 if v.length<.01:v=Vector((1,0,0))
 v.normalize();w=u.cross(v).normalized();vs=[tuple(p+v*x+w*y) for p in [a,b] for x,y in [(-.035,-.035),(.035,-.035),(.035,.035),(-.035,.035)]];mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],metal)
count=0
for i in range(len(sections)-1):
 n=max(1,round((ridge[i+1]-ridge[i]).length/1.8))
 for j in range(n):
  f=j/n;a=left[i].lerp(left[i+1],f);c=ridge[i].lerp(ridge[i+1],f);b=right[i].lerp(right[i+1],f);beam(f'R252_RIB_{count}_L',a,c);beam(f'R252_RIB_{count}_R',c,b);count+=1
for name,rail in [('L',left),('C',ridge),('R',right)]:
 for i,(a,b) in enumerate(zip(rail,rail[1:])):beam(f'R252_RAIL_{name}_{i}',a,b)
scene=R/'scenes/MUDAM_R252_OVAL_BAGIMSIZ_MIMARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True);bpy.ops.wm.open_mainfile(filepath=str(scene));s=bpy.context.scene;targ=Vector((320,398,20));s.camera.location=targ+Vector((80,-100,80));s.camera.rotation_euler=(targ-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=100;s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R252_oval_architecture.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R252_'))
glb=R/'exports/r152_clean/r252_oval_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R252_OVAL_ARCHITECTURE.json').write_text(json.dumps(dict(accepted=False,published=False,removedReferenceVertices=removed,roofLevel=level,ridgeCoefficients=coef.tolist(),ribs=count,checks=checks,limits=['Independent traced volume, roof annulus and fitted pitched glazed roof only','Facade openings and floor bands still required before any publication','Outer outline curvature and end pavilion profiles require refinement','1.8m rib spacing and70mm sections approximate','Foundation8.5m provisional']),indent=2));print('R252_CANDIDATE',len(checks),flush=True)
