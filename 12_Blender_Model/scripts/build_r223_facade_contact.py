from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R222_ERASMUS_ALT_CEPHE_ADAY_v001.blend'));d=json.loads((R/'config/r221_front_openings_projected.json').read_text());a=Vector(d['origin']);u=Vector(d['u']);n=Vector(d['normal']);o=bpy.data.objects['R216_ERASMUS_WING_0']
# Source close view shows facade left edge near pixel414, beyond the roof-only trace.
shift=-.90;changed=0
for v in o.data.vertices:
 if u.dot(v.co-a)<1.0:v.co+=u*shift;changed+=1
o.data.update()
def box(name,x0,x1,y0,y1,z0,z1,mat=None):
 vs=[tuple(a+u*x+n*y+Vector((0,0,z)))for z in [z0,z1]for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 if mat:me.materials.append(mat)
 return ob
w=d['openings'][0];x0,x1,z0,z1=[w[k]for k in ['u0','u1','z0','z1']];cut=box('CUT',x0,x1,-1,.3,z0,z1);bpy.context.view_layer.objects.active=o;m=o.modifiers.new('R223_FIRST_WINDOW','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
box('R223_GLASS_0',x0+.045,x1-.045,-.21,-.19,z0+.045,z1-.045,bpy.data.materials['R221_BLUE_GREY_GLASS'])
for label,xx0,xx1,zz0,zz1 in [('L',x0,x0+.045,z0,z1),('R',x1-.045,x1,z0,z1),('B',x0,x1,z0,z0+.045),('T',x0,x1,z1-.045,z1),('M',(x0+x1)/2-.0225,(x0+x1)/2+.0225,z0,z1)]:box('R223_FRAME_0'+label,xx0,xx1,-.24,-.14,zz0,zz1,bpy.data.materials['R221_DARK_FRAMES'])
vs=[];fs=[]
for name in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN']:
 ob=bpy.data.objects.get(name)
 if ob is None:continue
 ob.data.calc_loop_triangles();k=len(vs);vs.extend(ob.matrix_world@v.co for v in ob.data.vertices);fs.extend([k+i for i in t.vertices]for t in ob.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);front=bpy.data.objects['R222_ERASMUS_FRONT_0'];bmin=min(v.co.z for v in front.data.vertices);f=json.loads((R/'config/r222_lower_openings_projected.json').read_text());origin=Vector(f['origin']);fu=Vector(f['u']);fn=Vector(f['normal']);lo=f['openings'][-1]['u0'];hi=f['openings'][-1]['u1'];samples=[]
for i in range(41):
 for j in range(15):
  p=origin+fu*(lo+(hi-lo)*i/40)+fn*(-7+7*j/14);h=g.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),200)[0]
  if h is None:raise RuntimeError('Terrain sample missing')
  samples.append(h.z)
newbase=min(bmin,min(samples)-.05)
for v in front.data.vertices:
 if abs(v.co.z-bmin)<.0001:v.co.z=newbase
front.data.update();path=R/'scenes/MUDAM_R223_ERASMUS_CEPHE_OTURUM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for ob in bpy.context.scene.objects:ob.select_set(ob.name.startswith(('R221_','R222_','R223_'))or ob.name=='R216_ERASMUS_WING_0')
glb=R/'exports/r152_clean/r223_facade_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges)));bm.free()
assert all(c['boundary']==0 for c in checks)
(R/'reports/R223_FACADE_CONTACT.json').write_text(json.dumps(dict(accepted=False,published=False,upperWindows=5,lowerWindows=7,leftFootprintShift=shift,shiftedVertices=changed,terrainSamples=len(samples),terrainMin=min(samples),terrainMax=max(samples),previousBase=bmin,newBase=newbase,maxSampledUndersideGap=newbase-min(samples),reopen=checks,limitations=['Left edge correction visually inferred, not survey','Ground sampling checks underside only; surrounding hardscape and facade burial still require visual source review','Other wings rear links courtyard buildings and materials still incomplete']),indent=2));print('R223',newbase,min(samples),max(samples),flush=True)
