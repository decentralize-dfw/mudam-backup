from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');d=json.loads((R/'config/r231_cross_link_measure.json').read_text());assert d['heldOutP90']<.2 and d['support']>.9
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R229_ERASMUS_AVLU_CEPHE_ADAY_v001.blend'))
a=Vector((*d['start'],0));u=Vector((*d['axis'],0));v=Vector((*d['trans'],0));L=d['length'];w=d['width']/2;c=d['fit']
def z(s,t):return c[0]+c[1]*s+c[2]*t+c[3]*t*t
def pt(s,t,h):return tuple(a+u*s+v*t+Vector((0,0,h)))
mat=bpy.data.materials.new('R231_GLASS');mat.diffuse_color=(.19,.35,.36,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.19,.35,.36,1);bs.inputs['Roughness'].default_value=.23;bs.inputs['Transmission Weight'].default_value=.55
stone=bpy.data.materials.new('R231_BASE');stone.diffuse_color=(.42,.40,.36,1)
def mesh(name,vs,fs,material):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);assert not any(e.is_boundary for e in bm.edges);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(material);return o
# Closed analytic curved roof shell; independent topology, no source mesh.
N=24;vs=[pt(s,-w+2*w*j/N,z(s,-w+2*w*j/N)-off)for off in [0,.06]for s in [0,L]for j in range(N+1)];k=N+1;fs=[]
for j in range(N):fs.extend([(j,j+1,k+j+1,k+j),(2*k+j,3*k+j,3*k+j+1,2*k+j+1),(j,2*k+j,2*k+j+1,j+1),(k+j,k+j+1,3*k+j+1,3*k+j)])
fs.extend([(0,k,3*k,2*k),(N,2*k+N,3*k+N,k+N)]);mesh('R231_CURVED_GLAZED_ROOF',vs,fs,mat)
vs=[];fs=[]
for name in ['R154_FAR_GROUND','R152_CLASS2_TERRAIN']:
 ob=bpy.data.objects.get(name)
 if ob is None:continue
 ob.data.calc_loop_triangles();q=len(vs);vs.extend(ob.matrix_world@x.co for x in ob.data.vertices);fs.extend([q+i for i in t.vertices]for t in ob.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);heights=[]
for i in range(31):
 for j in range(5):
  p=Vector(pt(L*i/30,-w+2*w*j/4,100));hit=g.ray_cast(p,Vector((0,0,-1)),200)[0];assert hit is not None;heights.append(hit.z)
base=min(heights)-.05
faces=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4)for i in range(4)]
for side,t in enumerate([-w,w]):
 coords=[(0,t),(L,t),(L,t+(.05 if side==0 else -.05)),(0,t+(.05 if side==0 else -.05))];mesh('R231_GLAZED_SIDE_'+str(side),[pt(s,q,base)for s,q in coords]+[pt(s,q,z(s,t)-.06)for s,q in coords],faces,mat)
# End panels follow the analytic roof section and remain closed solids.
for idx,s in enumerate([0,L]):
 ds=.05 if idx==0 else -.05;ring=[(-w,base),(w,base)]+[(w-2*w*j/N,z(s,w-2*w*j/N)-.06)for j in range(N+1)];nr=len(ring);vs=[pt(ss,t,h)for ss in [s,s+ds]for t,h in ring];fs=[tuple(reversed(range(nr))),tuple(range(nr,2*nr))]+[(i,(i+1)%nr,(i+1)%nr+nr,i+nr)for i in range(nr)];mesh('R231_GLAZED_END_'+str(idx),vs,fs,mat)
path=R/'scenes/MUDAM_R231_ERASMUS_CAM_BAGLANTI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for ob in bpy.context.scene.objects:ob.select_set(ob.name.startswith('R231_'))
glb=R/'exports/r152_clean/r231_glazed_link_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001);checks.append(dict(name=ob.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(not x['boundary'] and not x['zero']for x in checks)
(R/'reports/R231_GLAZED_LINK.json').write_text(json.dumps(dict(accepted=False,published=False,measurement=d,base=base,terrainSamples=len(heights),reopen=checks,limits=['Measured near-planar cross connector envelope; frames/doors/interior floor and T-junction overlap unresolved','Side and end enclosure base follows modeled terrain; source level relationship needs further review','Glass material and .05/.06 thickness provisional','Whole complex and junctions not accepted']),indent=2));print('R231_READY',checks)
