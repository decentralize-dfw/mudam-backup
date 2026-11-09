from pathlib import Path
import bpy,bmesh,json,math
import numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'roof_planes_164179202.json').read_text());points=np.array(d['points']);ang=float(np.load(D/'164179202.npz')['angle']);cs,sn=math.cos(ang),math.sin(ang)
def local(p):return np.array([cs*p.x+sn*p.y,-sn*p.x+cs*p.y])
def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def hull(p):
 q=sorted(set(map(tuple,p)));a=[];b=[]
 for v in q:
  while len(a)>1 and cross(a[-2],a[-1],v)<=0:a.pop()
  a.append(v)
 for v in q[::-1]:
  while len(b)>1 and cross(b[-2],b[-1],v)<=0:b.pop()
  b.append(v)
 return a[:-1]+b[:-1]
def inside(p,h):return all(cross(a,b,p)>=-1e-6 for a,b in zip(h,h[1:]+h[:1]))
# Use only independently supported major slopes; the fourth fit duplicates a slope.
planes=[np.array(p['coeff']) for p in d['planes'][:3]];hulls=[hull(points[p['indices'],:2]) for p in d['planes'][:3]]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_SIRA_CATI_ADAY_v019.blend'));o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data);layer=bm.faces.layers.int.new('supported_plane');groups={};faces_before=len(bm.faces)
for f in bm.faces:
 f[layer]=-1
 if f.normal.z<.35:continue
 coords=[local(v.co) for v in f.verts];valid=[]
 for i,(p,h) in enumerate(zip(planes,hulls)):
  if not all(inside(x,h) for x in coords):continue
  errors=[abs(p[0]*x[0]+p[1]*x[1]+p[2]-v.co.z) for x,v in zip(coords,f.verts)]
  if max(errors)<.22:valid.append((sum(errors)/len(errors),i))
 if valid:
  i=min(valid)[1];f[layer]=i
  for v in f.verts:groups.setdefault(v,set()).add(i)
changed=[]
for v,labels in groups.items():
 if len(labels)!=1:continue
 p=planes[next(iter(labels))];x,y=local(v.co);z=p[0]*x+p[1]*y+p[2];changed.append(abs(z-v.co.z));v.co.z=z
m=bpy.data.materials.new('R169_ROW_SOURCE_SLATE');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.19,.225,.24,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;o.data.materials.append(m);mi=len(o.data.materials)-1
for f in bm.faces:
 if f[layer]>=0:f.material_index=mi
bm.normal_update();supported=sum(f[layer]>=0 for f in bm.faces)
# Remove internal coplanar diagonals only; retain source-feature and patch boundaries.
edges=[e for e in bm.edges if len(e.link_faces)==2 and e.link_faces[0][layer]>=0 and e.link_faces[0][layer]==e.link_faces[1][layer] and e.calc_face_angle(99)<1e-4]
if edges:bmesh.ops.dissolve_edges(bm,edges=edges,use_verts=False,use_face_split=False)
bm.normal_update();bad=[f for f in bm.faces if f.calc_area()<1e-9];assert not bad
bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>3 and f[layer]>=0]);degenerate=[f for f in bm.faces if f.calc_area()<1e-9];removed_zero_area=len(degenerate)
if degenerate:bmesh.ops.delete(bm,geom=degenerate,context='FACES_ONLY')
faces_after=len(bm.faces);bm.to_mesh(o.data);bm.free();o.data.calc_loop_triangles();assert all(t.area>=1e-9 for t in o.data.loop_triangles)
out=R/'scenes/MUDAM_R169_SIRA_DUZLEM_ADAY_v021.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
report=dict(scene=out.name,accepted=False,published=False,supported_faces=supported,projected_vertices=len(changed),max_vertex_move_m=max(changed),faces_before=faces_before,faces_after=faces_after,removed_coplanar_diagonals=len(edges),removed_zero_area=removed_zero_area,limits=['Only source-supported major roof slopes; convex support excludes unmeasured eaves','Retained dormers and source features remain rough','Supported slopes use provisional slate color; source atlas UVs are not stretched over dissolved faces','No complete building acceptance or publication']);(R/'reports/R169_COHERENT_SLOPES_v021.json').write_text(json.dumps(report,indent=2));print('R169_SLOPES_BUILT',report,flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-320,-45);s.camera.rotation_euler=(Vector((-67,-299,-66))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_row_roof_v021.png');bpy.ops.render.render(write_still=True)
