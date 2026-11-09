from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
b=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'][0]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_GUNEY_CATILAR_ADAY_v004.blend'))
o=bpy.data.objects['R169_MEASURED_ENVELOPE'];ring=[Vector((x,y,0)) for x,y in b['rings'][0][:-1]];a=ring[3];t=(ring[0]-a).normalized();inside=Vector((t.y,-t.x,0));out=-inside;center=(a+ring[0])*.5+inside*(-.45);base=b['base'];scale=26/1600
# Camera's horizontal axis equals the edge tangent for this clockwise footprint.
right=Vector((-out.y,out.x,0));origin=center+Vector((0,0,base+7.5))
def pixel(x,y):return ((x-800)*scale,(500-y)*scale+base+7.5)
rects=[(565,482,635,604),(714,481,784,603),(857,483,929,604),(564,646,636,780),(714,647,784,782),(857,647,930,782)]
windows=[]
for x0,y0,x1,y1 in rects:
 u0,z1=pixel(x0,y0);u1,z0=pixel(x1,y1);windows.append((u0,u1,z0,z1))
def mat(name,color,rough=.7,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
stone=mat('R169_33_IVORY_RENDER',( .68,.69,.63));trim=mat('R169_33_PALE_WINDOW_REVEALS',(.76,.77,.71));glass=mat('R169_33_DARK_GLAZING',(.115,.19,.205),.23,.2);rail=mat('R169_33_BALCONY_DARK_INFILL',(.18,.23,.23),.5)
verts=[];faces=[];mids=[]
def pos(u,z,d=0):return tuple(center+right*u+Vector((0,0,z))+out*d)
def quad(points,mi):
 i=len(verts);verts.extend(points);faces.append([i,i+1,i+2,i+3]);mids.append(mi)
def panel(u0,u1,z0,z1,d,mi):quad([pos(u0,z0,d),pos(u1,z0,d),pos(u1,z1,d),pos(u0,z1,d)],mi)
# Replace only this facade's low wall, keeping all other buildings and sampled roofs.
bm=bmesh.new();bm.from_mesh(o.data);removed=[]
for f in bm.faces:
 q=f.calc_center_median();u=(q-center).dot(right);dep=(q-center).dot(out)
 if abs(dep)<.03 and abs(u)<10.7 and abs(f.normal.z)<.1:removed.append(f)
bmesh.ops.delete(bm,geom=removed,context='FACES');bm.to_mesh(o.data);bm.free()
lo=-10.54;hi=10.54;bottom=base-.08;top=base+8.5
xs=sorted(set([lo,hi]+[v for w in windows for v in w[:2]]));zs=sorted(set([bottom,top]+[v for w in windows for v in w[2:]]))
for u0,u1 in zip(xs,xs[1:]):
 for z0,z1 in zip(zs,zs[1:]):
  u=(u0+u1)/2;z=(z0+z1)/2
  if not any(w[0]<u<w[1] and w[2]<z<w[3] for w in windows):panel(u0,u1,z0,z1,0,0)
for u0,u1,z0,z1 in windows:
 # Source establishes projected opening dimensions; 0.12m recess and 0.055m frame are explicit modeling assumptions.
 panel(u0,u1,z0,z1,-.12,2)
 for points in [[pos(u0,z0),pos(u0,z1),pos(u0,z1,-.12),pos(u0,z0,-.12)],[pos(u1,z0),pos(u1,z0,-.12),pos(u1,z1,-.12),pos(u1,z1)],[pos(u0,z0),pos(u0,z0,-.12),pos(u1,z0,-.12),pos(u1,z0)],[pos(u0,z1),pos(u1,z1),pos(u1,z1,-.12),pos(u0,z1,-.12)]]:quad(points,1)
 panel(u0,u0+.055,z0,z1,-.035,1);panel(u1-.055,u1,z0,z1,-.035,1);panel(u0,u1,z0,z0+.055,-.035,1);panel(u0,u1,z1-.055,z1,-.035,1)
 # No invented internal mullions where the source is unreadable.
mesh=bpy.data.meshes.new('R169_33_FRONT_REBUILT');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.scene.collection.objects.link(obj)
for m in [stone,trim,glass,rail]:mesh.materials.append(m)
for f,mi in zip(mesh.polygons,mids):f.material_index=mi
obj['source']='R169_33_facade_3_source.png orthographic 26m/1600px';obj['status']='partial candidate: six visible windows only; balcony and side facade work remains'
outfile=R/'scenes/MUDAM_R169_CEPHE_GEOMETRI_ADAY_v006.blend';bpy.ops.wm.save_as_mainfile(filepath=str(outfile),compress=True);bpy.ops.wm.open_mainfile(filepath=str(outfile))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('QA');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.4,-.5,-.3);bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=origin+out*35;s.camera.rotation_euler=(origin-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=26;s.render.filepath=str(R/'renders/qa/R169_33_front_geometry_v006.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_FACADE_GEOMETRY_v006.json').write_text(json.dumps(dict(scene=outfile.name,accepted=False,published=False,removed_facade_faces=len(removed),visible_window_openings=6,source_pixels=rects,source_image='R169_33_facade_3_source.png',reopened=True,assumptions={'recess_m':.12,'frame_width_m':.055,'wall_top_relative_m':8.5},remaining=['Balconies and lower entrances not reconstructed yet','Side and rear facade still need separate reconstruction','Roof-to-wall junction must be verified before acceptance']),indent=2))
print('FRONT_GEOMETRY_SAVED',len(removed))

