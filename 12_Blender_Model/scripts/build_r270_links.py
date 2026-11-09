import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R268_ERASMUS_EKSIK_ON_KUTLE_ADAY_v001.blend'));ds=[next(d for d in json.loads((R/'config/r270_left_link_candidates.json').read_text()) if d['offset']==.6),json.loads((R/'config/r269_extra_glass_links.json').read_text())[1]];glass=bpy.data.materials['R228_GLASS'];metal=bpy.data.materials['R221_DARK_FRAMES'];stone=bpy.data.materials['R222_PALE_MINERAL'];faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('R268_FRONT_SHELL'):
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001);bm.to_mesh(o.data);bm.free()
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN','R182_EXTENSION_GROUND']:
  o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);records=[]
def mesh(n,v,f,ma):
 me=bpy.data.meshes.new(n);me.from_pydata([tuple(p) for p in v],[],f);me.materials.append(ma);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o)
for idx,d in enumerate(ds):
 assert d['heldOutP90']<.2 and d['support']>.9;a=Vector((*d['start'],0));u=Vector((*d['axis'],0));v=Vector((*d['trans'],0));L=d['length'];w=d['width']/2;c=d['fit'];z=lambda s,t:c[0]+c[1]*s+c[2]*t+c[3]*t*t;pt=lambda s,t,h:a+u*s+v*t+Vector((0,0,h));heights=[];missing=0
 for i in range(31):
  for j in range(5):
   q=pt(L*i/30,-w+2*w*j/4,100);h,*_=g.ray_cast(q,Vector((0,0,-1)),200)
   if h:heights.append(h.z)
   else:missing+=1
 assert heights;base=min(heights)-.1;N=24;k=N+1;verts=[pt(s,-w+2*w*j/N,z(s,-w+2*w*j/N)-off) for off in [0,.06] for s in [0,L] for j in range(N+1)];f=[]
 for j in range(N):f.extend([(j,j+1,k+j+1,k+j),(2*k+j,3*k+j,3*k+j+1,2*k+j+1),(j,2*k+j,2*k+j+1,j+1),(k+j,k+j+1,3*k+j+1,3*k+j)])
 f.extend([(0,k,3*k,2*k),(N,2*k+N,3*k+N,k+N)]);mesh(f'R270_ROOF_{idx}',verts,f,glass)
 for side,t in enumerate([-w,w]):
  coords=[(0,t),(L,t),(L,t+(.07 if side==0 else -.07)),(0,t+(.07 if side==0 else -.07))];mesh(f'R270_SIDE_{idx}_{side}',[pt(s,q,base) for s,q in coords]+[pt(s,q,z(s,t)-.06) for s,q in coords],faces,glass)
 for end,s in enumerate([0,L]):
  ring=[(-w,base),(w,base)]+[(w-2*w*j/N,z(s,w-2*w*j/N)-.06) for j in range(N+1)];nr=len(ring);verts=[pt(ss,t,h) for ss in [s,s+(.06 if end==0 else -.06)] for t,h in ring];f=[tuple(reversed(range(nr))),tuple(range(nr,2*nr))]+[(i,(i+1)%nr,(i+1)%nr+nr,i+nr) for i in range(nr)];mesh(f'R270_END_{idx}_{end}',verts,f,glass)
 coords=[(0,-w),(L,-w),(L,w),(0,w)];mesh(f'R270_FLOOR_{idx}',[pt(s,t,h) for h in [base,base+.2] for s,t in coords],faces,stone)
 vv=[];ff=[]
 def beam(p,q):
  direction=(q-p).normalized();r=direction.cross(Vector((0,0,1)))
  if r.length<.01:r=Vector((1,0,0))
  r.normalize();ss=direction.cross(r).normalized();kk=len(vv);vv.extend(p0+r*x+ss*y for p0 in [p,q] for x,y in [(-.025,-.025),(.025,-.025),(.025,.025),(-.025,.025)]);ff.extend(tuple(kk+i for i in f) for f in faces)
 count=round(L/.7)
 for i in range(count+1):
  s=L*i/count
  for j in range(N):
   t0=-w+2*w*j/N;t1=-w+2*w*(j+1)/N;beam(pt(s,t0,z(s,t0)+.035),pt(s,t1,z(s,t1)+.035))
  for t in [-w,w]:beam(pt(s,t,base),pt(s,t,z(s,t)))
 for t in [-w,-w/2,0,w/2,w]:beam(pt(0,t,z(0,t)+.035),pt(L,t,z(L,t)+.035))
 mesh(f'R270_FRAMES_{idx}',vv,ff,metal);records.append(dict(measurement=d,base=base,groundMissing=missing,groundMin=min(heights),groundMax=max(heights)));print('LINK_DONE',idx,flush=True)
path=R/'scenes/MUDAM_R270_ERASMUS_IKI_CAM_GECIT_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.resolution_x=2048;s.render.resolution_y=602;s.cycles.samples=16;s.render.filepath=str(R/'renders/qa/R270_erasmus_front_authored.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith(('R270_','R268_')))
glb=R/'exports/r152_clean/r270_glass_links_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R270_TWO_GLASS_LINKS.json').write_text(json.dumps(dict(accepted=False,published=False,records=records,checks=checks,limits=['Cross links and adjoining courtyard halls not yet added','Glazing frames spacing0.7m approximate','Foundation follows current terrain, not surveyed interior floor']),indent=2));print('R270_CHECKS',len(checks),sum(c['boundary'] for c in checks),sum(c['zero'] for c in checks),flush=True)
