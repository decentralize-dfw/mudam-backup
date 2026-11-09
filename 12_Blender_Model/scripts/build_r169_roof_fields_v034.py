from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';fields=json.loads((D/'row_roof_fields.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_UST_DUVAR_ADAY_v033.blend'));roof=bpy.data.objects['R169_ROW_CONTINUOUS_HIP'];roof.data.calc_loop_triangles();tree=BVHTree.FromPolygons([v.co for v in roof.data.vertices],[list(t.vertices) for t in roof.data.loop_triangles],all_triangles=True);bm=bmesh.new();bm.from_mesh(roof.data);verts=[];faces=[];mids=[];removed=0
for field in fields:
 assert field['p90']<.03
 xy=[Vector((-67+(x-700)/70,-299+(550-y)/70,0)) for x,y in field['pixels']];center=sum(xy,Vector())/4
 for p,q in zip(xy,xy[1:]+xy[:1]):bmesh.ops.bisect_plane(bm,geom=list(bm.faces)+list(bm.edges)+list(bm.verts),dist=1e-6,plane_co=p,plane_no=Vector((q.y-p.y,p.x-q.x,0)))
 def inside(p):
  signs=[(q.x-a.x)*(p.y-a.y)-(q.y-a.y)*(p.x-a.x) for a,q in zip(xy,xy[1:]+xy[:1])];return min(signs)>-1e-5 or max(signs)<1e-5
 drop=[f for f in bm.faces if inside(f.calc_center_median())];removed+=len(drop);bmesh.ops.delete(bm,geom=drop,context='FACES')
 a,b,c=field['plane'];outer=[];inner=[];joins=[]
 for p in xy:
  h,*_=tree.ray_cast(Vector((p.x,p.y,50)),Vector((0,0,-1)),200);assert h is not None;joins.append(h)
  outer.append(Vector((p.x,p.y,a*p.x+b*p.y+c+.015)))
  q=p.lerp(center,.10);inner.append(Vector((q.x,q.y,a*q.x+b*q.y+c)))
 off=len(verts);verts.extend(tuple(v) for v in outer+inner+joins)
 for i in range(4):
  j=(i+1)%4;faces.extend([[off+i,off+j,off+4+j,off+4+i],[off+8+i,off+8+j,off+j,off+i]]);mids.extend([0,0])
 faces.append([off+4+i for i in range(4)]);mids.append(1)
bm.to_mesh(roof.data);bm.free();me=bpy.data.meshes.new('R169_ROW_TRACED_ROOF_FIELDS');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
for name,color,rough in [('FRAME',(.22,.26,.27,1),.7),('PALE_ROOF_FIELD',(.42,.56,.59,1),.35)]:
 mat=bpy.data.materials.new('R169_ROW_'+name);mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=rough;me.materials.append(mat)
for f,i in zip(me.polygons,mids):f.material_index=i
for o in [roof,ob]:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-9]
 if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
 bm.normal_update()
 for f in bm.faces:
  if f.normal.z<0:f.normal_flip()
 bm.to_mesh(o.data);bm.free()
out=R/'scenes/MUDAM_R169_CATI_ALANLARI_ADAY_v034.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R169_ROOF_FIELDS_v034.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,source_samples=72,fields=fields,removed_roof_faces=removed,limits=['Two visible rectangular roof fields; precise component type unconfirmed','Frame inset10percent and lip15mm are modeling assumptions','Remaining raised fragments and lower facade are incomplete']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-50,-307,-43);s.camera.rotation_euler=(Vector((-67,-299,-64))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_roof_fields_v034.png');bpy.ops.render.render(write_still=True)
