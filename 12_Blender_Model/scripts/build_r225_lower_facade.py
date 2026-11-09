from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R224_ERASMUS_GERCEK_ACIKLIK_ADAY_v001.blend'));d=json.loads((R/'config/r225_lower_openings_projected.json').read_text());a=Vector(d['origin']);u=Vector(d['u']);n=Vector(d['normal']);old=bpy.data.objects['R219_ERASMUS_FRONT_1'];base=min((old.matrix_world@v.co).z for v in old.data.vertices);roof=max((old.matrix_world@v.co).z for v in old.data.vertices);bpy.data.objects.remove(old,do_unlink=True)
stone=bpy.data.materials.new('R225_PALE_MINERAL');stone.diffuse_color=(.54,.49,.43,1);glass=bpy.data.materials.get('R221_BLUE_GREY_GLASS');metal=bpy.data.materials.get('R221_DARK_FRAMES')
def box(name,x0,x1,y0,y1,z0,z1,mat=None):
 vs=[tuple(a+u*x+n*y+Vector((0,0,z)))for z in [z0,z1]for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 if mat:me.materials.append(mat)
 return o
bound=d['openings'][-1];lo,hi=bound['u0'],bound['u1']
from mathutils.bvhtree import BVHTree
vs=[];fs=[]
for name in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN']:
 ob=bpy.data.objects.get(name)
 if ob is None:continue
 ob.data.calc_loop_triangles();k=len(vs);vs.extend(ob.matrix_world@v.co for v in ob.data.vertices);fs.extend([k+i for i in t.vertices]for t in ob.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);samples=[]
for i in range(41):
 for j in range(15):
  p=a+u*(lo+(hi-lo)*i/40)+n*(-7+7*j/14);h=g.ray_cast(Vector((p.x,p.y,100)),Vector((0,0,-1)),200)[0]
  assert h is not None
  samples.append(h.z)
base=min(base,min(samples)-.05)
fit=next(p for p in json.loads((R/'config/r219_front_planes.json').read_text())['parts']if p['id']==1)
def roofz(p):return fit['plane'][0]*(p.x-fit['origin'][0])+fit['plane'][1]*(p.y-fit['origin'][1])+fit['plane'][2]
o=box('R225_ERASMUS_FRONT_1',lo,hi,-7,0,base,roof,stone)
for v in o.data.vertices:
 if abs(v.co.z-roof)<.0001:v.co.z=roofz(v.co)
o.data.update();roof=min(v.co.z for v in o.data.vertices if v.co.z>base+.001)

def cut(c):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('R225_OPENING','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
cut(box('CUT',lo+.35,hi-.35,-6.65,-.35,base+.2,roof-.22))
for i,w in enumerate(d['openings'][:-1]):
 x0,x1,z0,z1=[w[k]for k in ['u0','u1','z0','z1']];assert lo+.15<x0<x1<hi-.15 and base+.2<z0<z1<roof-.2
 cut(box('CUT',x0,x1,-.7,.3,z0,z1));box('R225_GLASS_'+str(i),x0+.045,x1-.045,-.22,-.20,z0+.045,z1-.045,glass)
 for label,xx0,xx1,zz0,zz1 in [('L',x0,x0+.045,z0,z1),('R',x1-.045,x1,z0,z1),('B',x0,x1,z0,z0+.045),('T',x0,x1,z1-.045,z1),('M',(x0+x1)/2-.0225,(x0+x1)/2+.0225,z0,z1)]:box('R225_FRAME_'+str(i)+label,xx0,xx1,-.25,-.15,zz0,zz1,metal)
path=R/'scenes/MUDAM_R225_ERASMUS_ALT_CEPHE_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for x in bpy.context.scene.objects:x.select_set(x.name.startswith('R225_'))
glb=R/'exports/r152_clean/r225_lower_facade_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for x in bpy.context.scene.objects:
 if x.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(x.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001);checks.append(dict(name=x.name,boundary=sum(e.is_boundary for e in bm.edges)));bm.free()
assert all(c['boundary']==0 for c in checks)
(R/'reports/R225_LOWER_FACADE.json').write_text(json.dumps(dict(accepted=False,published=False,observedOpenings=7,terrainSamples=len(samples),terrainMin=min(samples),terrainMax=max(samples),base=base,roofPlane=fit['plane'],oldWidth=d['wallLength'],correctedWidth=hi-lo,source='R221_erasmus_front_source.png',reopen=checks,limits=['Widened frontage traced visually on model facade plane; not surveyed','Roof plane extrapolated over widened bounds; source edge validation pending','Rear depth and wall/frame thickness provisional','Other facades and upper footprint correction remain']),indent=2));print('R225_READY',len(checks),flush=True)
