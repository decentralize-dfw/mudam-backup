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
# Reconstruct continuous analytic slopes; all ridges share exact intersections.
planes=[p['coeff'] for p in json.loads((D/'row_whole_roof_planes_v046.json').read_text())[:3]]
def height(x,y):return min(a*x+b*y+c for a,b,c in planes)
def clip(poly,a,b,c):
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  dp=a*p[0]+b*p[1]+c;dq=a*q[0]+b*q[1]+c
  if dp<=1e-9:out.append(p)
  if (dp<0)!=(dq<0):
   t=dp/(dp-dq);out.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return out
verts=[];faces=[]
for i,p in enumerate(planes):
 poly=[(v.x,v.y) for v in ring]
 for j,q in enumerate(planes):
  if i!=j and poly:poly=clip(poly,*[a-b for a,b in zip(p,q)])
 if len(poly)<3:continue
 off=len(verts);verts.extend((x,y,height(x,y)) for x,y in poly);faces.append(tuple(range(off,off+len(poly))))
roof_count=len(faces)
# Segmented eave profiles use the same plane intersections as slopes.
for a,b in zip(ring,ring[1:]+ring[:1]):
 ts=[0.,1.]
 for i,p in enumerate(planes):
  for q in planes[i+1:]:
   c=np.array(p)-q;v0=c[0]*a.x+c[1]*a.y+c[2];v1=c[0]*b.x+c[1]*b.y+c[2]
   if abs(v1-v0)>1e-9:
    t=-v0/(v1-v0)
    if 0<t<1:ts.append(float(t))
 ts=sorted(ts)
 for t,u in zip(ts,ts[1:]):
  p=a.lerp(b,t);q=a.lerp(b,u);off=len(verts);verts.extend([(p.x,p.y,height(p.x,p.y)),(q.x,q.y,height(q.x,q.y)),(q.x,q.y,cut),(p.x,p.y,cut)]);faces.append(tuple(range(off,off+4)))
me=bpy.data.meshes.new('R169_WHOLE_SOURCE_ROOF');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
for name,color in [('R169_MEASURED_SLATE',(.13,.17,.19,1)),('R169_EAVE_WALL',(.43,.40,.34,1))]:
 m=bpy.data.materials.new(name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.83;me.materials.append(m)
for f in me.polygons:f.material_index=int(f.index>=roof_count)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
# Source-visible rear openings are below the eave, not floating roof fragments.
# Position/width follow ray hits; frame width and recess are modeling assumptions.
def mesh(name,vs,fs,mat):
 m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.materials.append(mat);o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);return o
frame=bpy.data.materials.new('R169_REAR_WINDOW_FRAME');frame.diffuse_color=(.48,.49,.46,1)
glass=bpy.data.materials.new('R169_REAR_WINDOW_GLASS');glass.use_nodes=True;bs=glass.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.055,.10,.12,1);bs.inputs['Roughness'].default_value=.22;bs.inputs['Metallic'].default_value=.25
origin=ring[0];tangent=(ring[1]-ring[0]).normalized();normal=Vector((-tangent.y,tangent.x,0))
hits=json.loads((D/'rear_feature_corners_v047.json').read_text())['hits']
for n,ids in enumerate([(0,1),(4,5)]):
 ps=[Vector(hits[i]) for i in ids];us=sorted((p-origin).dot(tangent) for p in ps);top=min(p.z for p in ps)-.08;bottom=[-65.02,-64.50][n]
 # Face offset only 3cm from fascia to avoid coplanar surface flicker.
 def pt(u,z,depth=.035):return tuple(origin+tangent*u+normal*depth+Vector((0,0,z)))
 left,right=us;w=.055;outer=[pt(left,bottom),pt(right,bottom),pt(right,top),pt(left,top)];inner=[pt(left+w,bottom+w,.04),pt(right-w,bottom+w,.04),pt(right-w,top-w,.04),pt(left+w,top-w,.04)]
 mesh('R169_SOURCE_REAR_WINDOW_'+str(n),inner,[(0,1,2,3)],glass);mesh('R169_SOURCE_REAR_FRAME_'+str(n),outer+inner,[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],frame)
 mid=(left+right)/2;mesh('R169_SOURCE_REAR_MULLION_'+str(n),[pt(mid-.022,bottom+w,.045),pt(mid+.022,bottom+w,.045),pt(mid+.022,top-w,.045),pt(mid-.022,top-w,.045)],[(0,1,2,3)],frame)
# Two roof fields traced in the top reference; position follows measured plane.
for n,field in enumerate(json.loads((D/'row_roof_fields.json').read_text())):
 vs=[]
 for x,y in field['pixels']:
  x=-67+(x-700)/70;y=-299+(550-y)/70;vs.append((x,y,height(x,y)+.025))
 mesh('R169_SOURCE_ROOF_FIELD_'+str(n),vs,[(0,1,2,3)],glass)
for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 obj.data.calc_loop_triangles();ids={t.polygon_index for t in obj.data.loop_triangles if t.area<1e-9}
 if ids:
  bm=bmesh.new();bm.from_mesh(obj.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in ids],context='FACES_ONLY');bm.to_mesh(obj.data);bm.free()
path=R/'scenes/MUDAM_R169_BUTUN_KAYNAK_CATI_ADAY_v048.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
(R/'reports/R169_WHOLE_ROOF_v048.json').write_text(json.dumps(dict(scene=path.name,accepted=False,published=False,source_samples=nx*ny,removed_faces=removed,roof_triangles=roof_count,maximum_smoothing_m=float(np.max(abs(z-outz))),limits=['Whole surface rebuilt from source sections, no source mesh copied','Roof outline manually traced; boundary and facade joins need visual acceptance','No claim of exact construction details or complete building']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20
for tag,pos in [('rear',(-80,-285,-48)),('front',(-50,-307,-43)),('top',(-67,-299,-30))]:
 s.camera.location=pos;s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/('renders/qa/R169_whole_v048_'+tag+'.png'));bpy.ops.render.render(write_still=True)
print('WHOLE_REBUILD_DONE',removed,roof_count)
