from pathlib import Path
import bpy,bmesh,json,math,numpy as np
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];q=json.loads((R/'reports/R175_BRIDGE_MEASUREMENTS.json').read_text());data=np.array(q['samples']);v=data[(abs(data[:,1])<4.5)&(data[:,3]>.8)&(data[:,2]>-49)&(data[:,2]<-45)];coef=np.polyfit(v[:,0],v[:,2],1);a=np.array(q['a']);u=np.array(q['u']);n=np.array(q['n'])
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R174_ALT_MAHALLE_EKLER_v001.blend'));col=bpy.data.collections.new('R175_AUTHORED_RAIL_VIADUCT');bpy.context.scene.collection.children.link(col)
gv=[];gf=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name in ['R154_FAR_GROUND','R154_FAR_ROADS']:
  o.data.calc_loop_triangles();k=len(gv);gv.extend(o.matrix_world@v.co for v in o.data.vertices);gf.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
ground=BVHTree.FromPolygons(gv,gf,all_triangles=True)
def deck(s):return float(coef[0]*s+coef[1])
def point(s,d,z):p=a+u*s+n*d;return (float(p[0]),float(p[1]),float(z))
def mat(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;return m
stone=bpy.data.materials.get('R154_FORT_STONE_PBR');ballast=mat('R175_BALLAST',(.11,.105,.095));steel=mat('R175_RAIL_STEEL',(.22,.23,.24));sleepers=mat('R175_SLEEPERS',(.17,.15,.13))
def prism(name,profile,ds,material):
 count=len(profile);vs=[point(s,d,z) for d in ds for s,z in profile];faces=[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)];vec=[Vector((s,z,0)) for s,z in profile]
 for t in tessellate_polygon([vec]):faces.extend([tuple(reversed(t)),tuple(i+count for i in t)])
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(material);uv=me.uv_layers.new()
 for f in me.polygons:
  normal=f.normal;tu=Vector((0,0,1)).cross(normal).normalized() if abs(normal.z)<.7 else Vector((1,0,0));tv=normal.cross(tu).normalized()
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(tu)/4,p.dot(tv)/4)
 return o
centers=[.0,17.65,35.3,52.95,70.6,88.25,105.9];radius=7.15;half=5.45;archrecords=[]
for i,c in enumerate(centers):
 spring=deck(c)-1.7-radius;curve=[(c-radius*math.cos(math.pi*j/24),spring+radius*math.sin(math.pi*j/24)) for j in range(25)]
 prism('R175_ARCH_%02d'%i,[(c-radius,deck(c-radius)-.18),(c+radius,deck(c+radius)-.18)]+list(reversed(curve)),[-half,half],stone)
 archrecords.append({'center':c,'radius':radius,'spring':spring,'method':'Analytic semicircle from visible source elevation; repeated obscured spans inferred'})
for i,(lo,hi) in enumerate(zip([-9]+[c+radius for c in centers],[c-radius for c in centers]+[115])):
 if hi<=lo:continue
 p=a+u*((lo+hi)/2);h,*_=ground.ray_cast(Vector((*p,100)),Vector((0,0,-1)),300);base=(h.z-.3) if h else -78
 prism('R175_PIER_%02d'%i,[(lo,base),(hi,base),(hi,deck(hi)-.18),(lo,deck(lo)-.18)],[-half,half],stone)
prism('R175_BALLAST_DECK',[(-9,deck(-9)-.2),(115,deck(115)-.2),(115,deck(115)+.02),(-9,deck(-9)+.02)],[-5.2,5.2],ballast)
for side in [-1,1]:
 d=side*5.3;prism('R175_PARAPET_'+str(side),[(-9,deck(-9)),(115,deck(115)),(115,deck(115)+.65),(-9,deck(-9)+.65)],[d-.2,d+.2],stone)
for ti,track in enumerate([-1.82,1.82]):
 for ri,delta in enumerate([-.7175,.7175]):
  d=track+delta;prism('R175_RAIL_%s_%s'%(ti,ri),[(-9,deck(-9)+.15),(115,deck(115)+.15),(115,deck(115)+.28),(-9,deck(-9)+.28)],[d-.035,d+.035],steel)
 for j,s in enumerate(np.arange(-8.5,115,.75)):
  prism('R175_SLEEPER_%s_%03d'%(ti,j),[(s-.11,deck(s)+.02),(s+.11,deck(s)+.02),(s+.11,deck(s)+.14),(s-.11,deck(s)+.14)],[track-1.2,track+1.2],sleepers)
report={'accepted':False,'source':'ACT top/elevation and OSM tracks26435587/840229558, gauge1435mm','roof_fit':coef.tolist(),'deck_fit_samples':len(v),'arches':archrecords,'limitations':['Occluded first spans extrapolate visible repeat rhythm','Arch dimensions manually measured from registered elevation, not survey','Parapet section and sleeper sections provisional','Full reference comparison pending']};(R/'reports/R175_VIADUCT_v001.json').write_text(json.dumps(report,indent=2))
s=bpy.context.scene;t=Vector((*list(a+u*50),-57));s.camera.location=t+Vector((*list(n*150),75));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=160;s.render.resolution_x=1400;s.render.resolution_y=900;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R175_DEMIRYOLU_VIYADUK_v001.blend'),compress=True)
for o in s.objects:o.select_set(o.name.startswith('R175_'))
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r175_viaduct_REVIEW.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
s.render.filepath=str(R/'renders/qa/R175_authored_viaduct.png');bpy.ops.render.render(write_still=True);print('R175_DONE')
