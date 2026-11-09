from pathlib import Path
import bpy,bmesh,json,math,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_whole_roof_samples_v045.json').read_text());ring=[Vector((*p,0)) for p in d['ring']];nx=d['nx'];ny=d['ny'];verts=d['vertices'];cut=-65.65
# Constrained local least-squares smoothing: preserve steps and ridges, limit correction.
z=np.array([p[2] for p in verts]).reshape(ny,nx);outz=z.copy()
for j in range(1,ny-1):
 for i in range(1,nx-1):
  patch=z[j-1:j+2,i-1:i+2];yy,xx=np.mgrid[-1:2,-1:2];A=np.c_[xx.ravel(),yy.ravel(),np.ones(9)];coef=np.linalg.lstsq(A,patch.ravel(),rcond=None)[0];res=patch.ravel()-A@coef
  if np.max(np.abs(res))<.075:outz[j,i]=coef[2]
for k,p in enumerate(verts):p[2]=float(outz.flat[k])
def inside(p):
 cr=[(b.x-a.x)*(p.y-a.y)-(b.y-a.y)*(p.x-a.x) for a,b in zip(ring,ring[1:]+ring[:1])];return min(cr)>-1e-5 or max(cr)<1e-5
xmin=min(p.x for p in ring);xmax=max(p.x for p in ring);ymin=min(p.y for p in ring);ymax=max(p.y for p in ring)
def intersects(f):return max(v.co.x for v in f.verts)>=xmin and min(v.co.x for v in f.verts)<=xmax and max(v.co.y for v in f.verts)>=ymin and min(v.co.y for v in f.verts)<=ymax and max(v.co.z for v in f.verts)>=cut
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_SIRA_CATI_ADAY_v019.blend'))
o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data);fs=[f for f in bm.faces if intersects(f)];bmesh.ops.split(bm,geom=fs,use_only_faces=True)
for a,b in zip(ring,ring[1:]+ring[:1]):
 fs=[f for f in bm.faces if intersects(f)];es={e for f in fs for e in f.edges};vs={v for f in fs for v in f.verts};bmesh.ops.bisect_plane(bm,geom=list(fs)+list(es)+list(vs),dist=1e-6,plane_co=a,plane_no=Vector((b.y-a.y,a.x-b.x,0)))
fs=[f for f in bm.faces if intersects(f)];es={e for f in fs for e in f.edges};vs={v for f in fs for v in f.verts};bmesh.ops.bisect_plane(bm,geom=list(fs)+list(es)+list(vs),dist=1e-6,plane_co=Vector((0,0,cut)),plane_no=Vector((0,0,1)))
drop=[f for f in bm.faces if inside(f.calc_center_median()) and f.calc_center_median().z>cut-1e-6];removed=len(drop);bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(o.data);bm.free()
faces=[]
for j in range(ny-1):
 for i in range(nx-1):
  k=j*nx+i
  # Shortest height diagonal avoids exaggerated saddle folds.
  if abs(verts[k][2]-verts[k+nx+1][2])<abs(verts[k+1][2]-verts[k+nx][2]):faces.extend([(k,k+1,k+nx+1),(k,k+nx+1,k+nx)])
  else:faces.extend([(k,k+1,k+nx),(k+1,k+nx+1,k+nx)])
# Assign coherent measured planes by triangle fit; fit boundaries jointly.
planes=np.array([p['coeff'] for p in json.loads((D/'row_whole_roof_planes_v046.json').read_text())[:4]])
points=np.array(verts);labels=[];inc=[set() for v in verts]
for f in faces:
 pts=points[list(f)];errs=np.max(np.abs(pts[:,2,None]-(np.c_[pts[:,:2],np.ones(3)]@planes.T)),axis=0);k=int(np.argmin(errs))
 label=k if errs[k]<.18 else -1;labels.append(label)
 for v in f:inc[v].add(label)
projected=0
for i,ls in enumerate(inc):
 if -1 in ls or not ls:continue
 ids=sorted(ls);A=np.array([[*planes[k,:2],-1] for k in ids]);b=-planes[ids,2];p=points[i];delta=np.linalg.lstsq(A,b-A@p,rcond=None)[0]
 if np.linalg.norm(delta)<.22:verts[i]=(p+delta).tolist();projected+=1
roof_count=len(faces)
edge=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(ny*nx-2,(ny-1)*nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
for a,b in zip(edge,edge[1:]+edge[:1]):
 off=len(verts);verts.extend([(verts[a][0],verts[a][1],cut),(verts[b][0],verts[b][1],cut)]);faces.append((a,off,off+1,b))
me=bpy.data.meshes.new('R169_WHOLE_SOURCE_ROOF');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
for name,color in [('R169_MEASURED_SLATE',(.13,.17,.19,1)),('R169_EAVE_WALL',(.43,.40,.34,1))]:
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.83;me.materials.append(m)
for f in me.polygons:
 f.material_index=int(f.index>=roof_count);f.use_smooth=f.index<roof_count
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 obj.data.calc_loop_triangles();ids={t.polygon_index for t in obj.data.loop_triangles if t.area<1e-9}
 if ids:
  bm=bmesh.new();bm.from_mesh(obj.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in ids],context='FACES_ONLY');bm.to_mesh(obj.data);bm.free()
path=R/'scenes/MUDAM_R169_BUTUN_KAYNAK_CATI_ADAY_v046.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
(R/'reports/R169_WHOLE_ROOF_v046.json').write_text(json.dumps(dict(scene=path.name,accepted=False,published=False,source_samples=nx*ny,plane_projected_vertices=projected,removed_faces=removed,roof_triangles=roof_count,maximum_smoothing_m=float(np.max(abs(z-outz))),limits=['Whole surface rebuilt from source sections, no source mesh copied','Roof outline manually traced; boundary and facade joins need visual acceptance','No claim of exact construction details or complete building']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20
for tag,pos in [('rear',(-80,-285,-48)),('front',(-50,-307,-43)),('top',(-67,-299,-30))]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/('renders/qa/R169_whole_v046_'+tag+'.png'));bpy.ops.render.render(write_still=True)
print('WHOLE_REBUILD_DONE',removed,roof_count)
