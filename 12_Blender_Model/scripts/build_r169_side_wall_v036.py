from pathlib import Path
import bpy,bmesh,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_side_wall_plane.json').read_text());center=Vector(d['center']);inside=Vector(d['inside']);right=Vector(d['right']);base=d['base'];origin=center+inside*d['offset'];u0,u1=-2.,4.5;z0=base+8.6
A=np.array([[(h['pixel'][0]-800)*.01,(500-h['pixel'][1])*.01,1] for h in d['hits']]);dep=np.array([h['offset'] for h in d['hits']]);coef=np.linalg.lstsq(A,dep,rcond=None)[0];residual=A@coef-dep
def depth(u,z):return float(coef[0]*u+coef[1]*(z-base-7.5)+coef[2])
# Six source-visible fields; the occluded rightmost tall field is excluded.
rects=[]
holes=[(max(u0,(x0-800)*.01),(x1-800)*.01,base+7.5+(500-y1)*.01,base+7.5+(500-y0)*.01) for x0,y0,x1,y1 in rects]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_CATI_ALANLARI_ADAY_v034.blend'));roof=bpy.data.objects['R169_ROW_CONTINUOUS_HIP'];edge_samples=[v for v in json.loads((D/'row_eave_normal_samples.json').read_text()) if v['edge']==1 and v['inset']==0];ea=Vector((edge_samples[0]['x'],edge_samples[0]['y'],0));eb=Vector((edge_samples[-1]['x'],edge_samples[-1]['y'],0));et=(eb-ea).normalized();en=Vector((et.y,-et.x,0));en=en if en.dot(inside)>0 else -en;boundary=[];shifted=0
bm=bmesh.new();bm.from_mesh(roof.data)
for j in range(21):
 u=u0+(u1-u0)*j/20
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=center+right*u,plane_no=right)
bm.to_mesh(roof.data);bm.free()
for v in roof.data.vertices:
 old=v.co.copy();u=(old-center).dot(right);dist=(old-ea).dot(en)
 if abs(dist)<.003 and u0 <= u <= u1:
  target=center+right*u+inside*depth(u,old.z);v.co.x=target.x;v.co.y=target.y;boundary.append((u,old.z));shifted+=1
roof.data.update();boundary=sorted(set(boundary));assert len(boundary)>5
roof.data.calc_loop_triangles();tree=BVHTree.FromPolygons([v.co for v in roof.data.vertices],[list(t.vertices) for t in roof.data.loop_triangles],all_triangles=True)
def top(u):return float(np.interp(u,[v[0] for v in boundary],[v[1] for v in boundary]))
heights=[top(u0+(u1-u0)*i/20) for i in range(21)];z1=max(heights)+.02
body=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(body.data)
for normal,point in [(right,origin+right*u0),(right,origin+right*u1),(Vector((0,0,1)),Vector((0,0,z0))),(Vector((0,0,1)),Vector((0,0,z1)))]:
 fs=[]
 for f in bm.faces:
  uu=[(v.co-origin).dot(right) for v in f.verts];zz=[v.co.z for v in f.verts];dd=[(v.co-origin).dot(inside) for v in f.verts]
  if min(uu)<u1+.2 and max(uu)>u0-.2 and min(zz)<z1+.2 and max(zz)>z0-.2 and min(dd)<2 and max(dd)>-2:fs.append(f);es=set(e for f in fs for e in f.edges);vs=set(v for f in fs for v in f.verts);bmesh.ops.bisect_plane(bm,geom=list(fs)+list(es)+list(vs),dist=1e-6,plane_co=point,plane_no=normal)
drop=[f for f in bm.faces if u0<(f.calc_center_median()-origin).dot(right)<u1 and z0<f.calc_center_median().z<z1 and abs((f.calc_center_median()-origin).dot(inside))<2];removed=len(drop);bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(body.data);bm.free()
verts=[];faces=[];mids=[]
def point(u,z,depth=0):return tuple(center+right*u+Vector((0,0,z))+inside*(float(coef[0]*u+coef[1]*(z-base-7.5)+coef[2])+depth))
def quad(coords,mi):
 off=len(verts);verts.extend(coords);faces.append(list(range(off,off+4)));mids.append(mi)
xs=sorted(set([u0,u1]+[v[0] for v in boundary if u0<v[0]<u1]+[u0+(u1-u0)*i/20 for i in range(1,20)]+[v for h in holes for v in h[:2]]));zs=sorted(set([z0,z1]+[v for h in holes for v in h[2:]]))
for l,r in zip(xs,xs[1:]):
 for bot,upper in zip(zs,zs[1:]):
  if any(a<(l+r)/2<b and c<(bot+upper)/2<e for a,b,c,e in holes):continue
  tl,tr=min(upper,top(l)),min(upper,top(r))
  if min(tl,tr)<=bot:continue
  quad([point(l,bot),point(r,bot),point(r,tr),point(l,tl)],0)
for l,r,bot,upper in holes:
 tl,tr=min(upper,top(l)),min(upper,top(r))
 quad([point(l,bot,.08),point(r,bot,.08),point(r,tr,.08),point(l,tl,.08)],1)
 for p,q in [((l,bot),(r,bot)),((r,bot),(r,tr)),((r,tr),(l,tl)),((l,tl),(l,bot))]:quad([point(*p),point(*q),point(*q,.08),point(*p,.08)],0)
me=bpy.data.meshes.new('R169_ROW_SIDE_UPPER_BAND');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
for name,color in [('LIMESTONE',(.62,.61,.52,1)),('GLAZING',(.045,.105,.13,1))]:
 m=bpy.data.materials.new('R169_ROW_'+name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;me.materials.append(m)
for f,mi in zip(me.polygons,mids):f.material_index=mi
bm=bmesh.new();bm.from_mesh(me);bm.normal_update()
for f in bm.faces:
 if f.normal.dot(inside)>.8:f.normal_flip()
bm.to_mesh(me);bm.free()
for obj in [body,ob]:
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9]
 if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
 bm.to_mesh(obj.data);bm.free()
out=R/'scenes/MUDAM_R169_YAN_DUVAR_ADAY_v036.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R169_SIDE_WALL_v036.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,source_plane_offset=d['offset'],plane_coefficients=coef.tolist(),plane_sample_rmse_m=float(np.sqrt(np.mean(residual**2))),aligned_roof_boundary_vertices=shifted,removed_wall_faces=removed,source_fields=rects,limits=['Source appearance blurred; field boundaries approximate','0.08m recess assumed','Upper wall only; occluded right field excluded','Roof boundary and upper wall use one fitted source plane; inherited lower facade registration unresolved','Leftmost tall field clipped at source roof scope','Roof intersections and inherited facade transition require review']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-50,-307,-43);s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_side_wall_v036.png');bpy.ops.render.render(write_still=True)


