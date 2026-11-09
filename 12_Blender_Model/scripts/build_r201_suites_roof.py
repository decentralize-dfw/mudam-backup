from pathlib import Path
import bpy,json,math,bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R200_BUTUN_VIYADUK_v001.blend'))

for old in list(bpy.data.objects):
 if old.name.startswith(('R183_NOVOTEL_SUITES','R201_NOVOTEL_SUITES')):bpy.data.objects.remove(old,do_unlink=True)
r=json.loads((R/'config/r201_suites_closed_roof.json').read_text());verts=[];faces=[];mi=[]
def face(p,m):
 k=len(verts);verts.extend(p);faces.append(tuple(range(k,k+len(p))));mi.append(m)
white=bpy.data.materials['R176_PALE_MINERAL'];glass=bpy.data.materials['R176_RECESSED_GLASS'];frame=bpy.data.materials['R176_WINDOW_FRAME'];roof=bpy.data.materials['R176_ROOF_GRAVEL']
base=11.1;top=31.35;levels=[base,16.35,19.35,22.35,25.35,28.35,top]
for aa,bb in zip(r['outer'],r['outer'][1:]+r['outer'][:1]):
 a,b=Vector(aa),Vector(bb);length=(b-a).length
 if length<.01:continue
 u=(b-a).normalized();n=Vector((u.y,-u.x));count=max(1,round(length/3.2));pitch=length/count
 def pt(x,z,inset=0):q=a+u*x-n*inset;return(q.x,q.y,z)
 for f,(z0,z1) in enumerate(zip(levels,levels[1:])):
  for j in range(count):
   x0=j*pitch;x1=(j+1)*pitch;left=x0+.16;right=x1-.16;lo=z0+(.2 if f==0 else .7);hi=z1-(.3 if f==0 else .45)
   face([pt(x0,z0),pt(x1,z0),pt(x1,lo),pt(x0,lo)],0);face([pt(x0,hi),pt(x1,hi),pt(x1,z1),pt(x0,z1)],0)
   face([pt(x0,lo),pt(left,lo),pt(left,hi),pt(x0,hi)],0);face([pt(right,lo),pt(x1,lo),pt(x1,hi),pt(right,hi)],0)
   cs=[(left,lo),(right,lo),(right,hi),(left,hi)]
   for c,d in zip(cs,cs[1:]+cs[:1]):face([pt(*c),pt(*d),pt(*d,.18),pt(*c,.18)],2)
   mid=(left+right)/2
   face([pt(left,lo,.18),pt(mid-.045,lo,.18),pt(mid-.045,hi,.18),pt(left,hi,.18)],1)
   face([pt(mid+.045,lo,.18),pt(right,lo,.18),pt(right,hi,.18),pt(mid+.045,hi,.18)],1)
   face([pt(mid-.045,lo,.18),pt(mid+.045,lo,.18),pt(mid+.045,hi,.18),pt(mid-.045,hi,.18)],2)
 # Continuous parapet corresponds to roof edge in source; closed underside is retained.
 face([pt(0,top),pt(length,top),pt(length,32.1),pt(0,32.1)],0)
# A continuous roof shell: inner parapet, solid coping, stepped technical roof.
for tri in r['triangles']:face([(x,y,base) for x,y in reversed(tri)],0)
for tri in r['roof_triangles']:face([(x,y,top) for x,y in tri],3)
for tri in r['coping_triangles']:face([(x,y,32.1) for x,y in tri],0)
for a,b in zip(r['inner'],r['inner'][1:]+r['inner'][:1]):face([(a[0],a[1],top),(b[0],b[1],top),(b[0],b[1],32.1),(a[0],a[1],32.1)],0)
block=r['raised_roof_domain'];zt=r['raised_top']
for a,b in zip(block,block[1:]+block[:1]):face([(a[0],a[1],top),(b[0],b[1],top),(b[0],b[1],zt),(a[0],a[1],zt)],0)
for tri in tessellate_polygon([[Vector((x,y,zt)) for x,y in block]]):face([(block[i][0],block[i][1],zt) for i in tri],3)
me=bpy.data.meshes.new('R201_NOVOTEL_SUITES');me.from_pydata(verts,[],faces);me.update()
for m in [white,glass,frame,roof]:me.materials.append(m)
for p,i in zip(me.polygons,mi):p.material_index=i
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
(R/'reports/R201_SUITES_ROOF.json').write_text(json.dumps(dict(accepted=False,change='Rebuilt whole roof as continuous stepped architectural shell; inner parapet faces and coping, technical volume joined through roof opening',dimensions=dict(mainRoof=31.35,parapet=32.1,copingWidth=.24),limits=['Coping width0.24m architectural assumption','Facade module/source agreement and ground interface remain pending']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R201_KUZEY_KAPALI_CATILAR_v001.blend'),compress=True)
s=bpy.context.scene;t=Vector((350,420,15));s.camera.location=t+Vector((50,-180,100));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=210;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R201_suites_closed_roof_v001.png');bpy.ops.render.render(write_still=True)
print('R183_DONE')

