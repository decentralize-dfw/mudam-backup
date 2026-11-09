from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'row_upper_wall_plane.json').read_text());center=Vector(d['center']);inside=Vector(d['inside']);right=Vector(d['right']);base=d['base'];origin=center+inside*d['offset'];u0,u1=-4.1,3.;z0=base+8.9
# Six source-visible fields; the occluded rightmost tall field is excluded.
rects=[(375,440,502,580),(745,425,880,578),(552,473,609,532),(620,473,674,532),(928,473,983,532),(997,473,1057,532)]
holes=[(max(u0,(x0-800)*.01),(x1-800)*.01,base+10+(500-y1)*.01,base+10+(500-y0)*.01) for x0,y0,x1,y1 in rects]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_KAYNAK_SACAK_ADAY_v026.blend'));roof=bpy.data.objects['R169_ROW_CONTINUOUS_HIP'];roof.data.calc_loop_triangles();tree=BVHTree.FromPolygons([v.co for v in roof.data.vertices],[list(t.vertices) for t in roof.data.loop_triangles],all_triangles=True)
def top(u):
 p=origin+right*u
 for step in [0,.025,.05,.1,.2,.3]:
  q=p+inside*step;h,*_=tree.ray_cast(Vector((q.x,q.y,50)),Vector((0,0,-1)),200)
  if h is not None:return h.z
 raise RuntimeError(('No supported roof near wall',u))
heights=[top(u0+(u1-u0)*i/20) for i in range(21)];z1=max(heights)+.02
body=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(body.data)
for normal,point in [(right,origin+right*u0),(right,origin+right*u1),(Vector((0,0,1)),Vector((0,0,z0))),(Vector((0,0,1)),Vector((0,0,z1)))]:
 fs=[f for f in bm.faces if abs((f.calc_center_median()-origin).dot(inside))<2 and u0-.2<(f.calc_center_median()-origin).dot(right)<u1+.2 and z0-.2<f.calc_center_median().z<z1+.2];es=set(e for f in fs for e in f.edges);vs=set(v for f in fs for v in f.verts);bmesh.ops.bisect_plane(bm,geom=list(fs)+list(es)+list(vs),dist=1e-6,plane_co=point,plane_no=normal)
drop=[f for f in bm.faces if u0<(f.calc_center_median()-origin).dot(right)<u1 and z0<f.calc_center_median().z<z1 and abs((f.calc_center_median()-origin).dot(inside))<2];removed=len(drop);bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(body.data);bm.free()
verts=[];faces=[];mids=[]
def point(u,z,depth=0):return tuple(origin+right*u+Vector((0,0,z))+inside*depth)
def quad(coords,mi):
 off=len(verts);verts.extend(coords);faces.append(list(range(off,off+4)));mids.append(mi)
xs=sorted(set([u0,u1]+[u0+(u1-u0)*i/20 for i in range(1,20)]+[v for h in holes for v in h[:2]]));zs=sorted(set([z0,z1]+[v for h in holes for v in h[2:]]))
for l,r in zip(xs,xs[1:]):
 for bot,upper in zip(zs,zs[1:]):
  if any(a<(l+r)/2<b and c<(bot+upper)/2<e for a,b,c,e in holes):continue
  tl,tr=min(upper,top(l)),min(upper,top(r))
  if min(tl,tr)<=bot:continue
  quad([point(l,bot),point(r,bot),point(r,tr),point(l,tl)],0)
for l,r,bot,upper in holes:
 tl,tr=min(upper,top(l)-.02),min(upper,top(r)-.02)
 quad([point(l,bot,.08),point(r,bot,.08),point(r,tr,.08),point(l,tl,.08)],1)
 for p,q in [((l,bot),(r,bot)),((r,bot),(r,tr)),((r,tr),(l,tl)),((l,tl),(l,bot))]:quad([point(*p),point(*q),point(*q,.08),point(*p,.08)],0)
me=bpy.data.meshes.new('R169_ROW_UPPER_WALL');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
for name,color in [('LIMESTONE',(.62,.61,.52,1)),('GLAZING',(.045,.105,.13,1))]:
 m=bpy.data.materials.new('R169_ROW_'+name);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=color;me.materials.append(m)
for f,mi in zip(me.polygons,mids):f.material_index=mi
bm=bmesh.new();bm.from_mesh(me);bm.normal_update()
for f in bm.faces:
 if f.normal.dot(inside)>.8:f.normal_flip()
bm.to_mesh(me);bm.free()
out=R/'scenes/MUDAM_R169_UST_DUVAR_ADAY_v029.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R169_UPPER_WALL_v029.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,source_plane_offset=d['offset'],removed_wall_faces=removed,source_fields=rects,limits=['Source appearance blurred; field boundaries approximate','0.08m recess assumed','Upper wall only; occluded right field excluded','Roof edge sampled up to0.3m inward where source wall plane lies outside manual roof outline; registration unresolved','Leftmost tall field clipped at source roof scope','Roof intersections and inherited facade transition require review']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-320,-45);s.camera.rotation_euler=(Vector((-67,-299,-66))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_row_roof_v029.png');bpy.ops.render.render(write_still=True)
