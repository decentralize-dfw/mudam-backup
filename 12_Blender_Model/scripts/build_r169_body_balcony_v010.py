from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
b=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'][0]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_CEPHE_CATI_ADAY_v007.blend'))
old=bpy.data.objects.get('R169_33_FRONT_REBUILT')
if old:bpy.data.objects.remove(old,do_unlink=True)
o=bpy.data.objects['R169_MEASURED_ENVELOPE'];ring=[Vector((x,y,0)) for x,y in b['rings'][0][:-1]];a=ring[3];t=(ring[0]-a).normalized();inside=Vector((t.y,-t.x,0));out=-inside;center=(a+ring[0])*.5+inside*(-.45);base=b['base'];scale=26/1600
# Camera's horizontal axis equals the edge tangent for this clockwise footprint.
right=Vector((-out.y,out.x,0));origin=center+Vector((0,0,base+7.5))
def pixel(x,y):return ((x-800)*scale,(500-y)*scale+base+7.5)
rects=[(160,485,395,616),(160,662,395,803),(1070,485,1350,616),(1070,662,1350,803),(565,482,635,604),(714,481,784,603),(857,483,929,604),(564,646,636,780),(714,647,784,782),(857,647,930,782)]
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
bm=bmesh.new();bm.from_mesh(o.data)
selected=[f for f in bm.faces if 25<f.calc_center_median().x<51 and -284<f.calc_center_median().y<-261]
removed=list(selected);geom=set(selected)
for f in selected:
 geom.update(f.edges);geom.update(f.verts)
bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=(0,0,base+8.5),plane_no=(0,0,1),clear_inner=True,clear_outer=False)
bm.to_mesh(o.data);bm.free()
corrected=[Vector((x,y,0)) for x,y in json.loads((R/'.local_source_cache/r169/targets_v004.json').read_text())['buildings'][0]['rings'][0][:-1]];lo,hi=sorted([(corrected[i]-center).dot(right) for i in [3,0]]);bottom=base-.08;top=base+8.5
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
# Rebuild the other low facades, placing only source-visible openings.
front_center=center.copy();front_right=right.copy();front_out=out.copy()
side_pixels={0:[(860,530,907,604),(860,647,908,742)],2:[(700,480,775,620),(858,480,991,620),(700,655,775,786),(852,655,995,786)],1:[]}
for edge in [0,1,2]:
 aa=ring[edge];bb=ring[(edge+1)%4];tt=(bb-aa).normalized();nn=Vector((tt.y,-tt.x,0));out=-nn;right=Vector((-out.y,out.x,0));center=(aa+bb)*.5+nn*({0:-.35,1:0,2:0}[edge]);half=(bb-aa).length/2
 openings=[]
 for x0,y0,x1,y1 in side_pixels[edge]:
  u0,z1=pixel(x0,y0);u1,z0=pixel(x1,y1);openings.append((u0,u1,z0,z1))
 left,right_end=sorted([(corrected[i]-center).dot(right) for i in [edge,(edge+1)%4]]);sx=sorted(set([left,right_end]+[u for w in openings for u in w[:2]]));sz=sorted(set([bottom,top]+[z for w in openings for z in w[2:]]))
 for u0,u1 in zip(sx,sx[1:]):
  for z0,z1 in zip(sz,sz[1:]):
   u=(u0+u1)/2;z=(z0+z1)/2
   if not any(w[0]<u<w[1] and w[2]<z<w[3] for w in openings):panel(u0,u1,z0,z1,0,0)
 for u0,u1,z0,z1 in openings:
  panel(u0,u1,z0,z1,-.12,2)
  for pp in [[pos(u0,z0),pos(u0,z1),pos(u0,z1,-.12),pos(u0,z0,-.12)],[pos(u1,z0),pos(u1,z0,-.12),pos(u1,z1,-.12),pos(u1,z1)],[pos(u0,z0),pos(u0,z0,-.12),pos(u1,z0,-.12),pos(u1,z0)],[pos(u0,z1),pos(u1,z1),pos(u1,z1,-.12),pos(u0,z1,-.12)]]:quad(pp,1)
center=front_center;right=front_right;out=front_out
mesh=bpy.data.meshes.new('R169_33_FRONT_REBUILT');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.scene.collection.objects.link(obj)
for m in [stone,trim,glass,rail]:mesh.materials.append(m)
for f,mi in zip(mesh.polygons,mids):f.material_index=mi
obj['source']='R169_33_facade_3_source.png orthographic 26m/1600px';obj['status']='partial candidate: sixteen source-visible openings; rear facade unresolved; balcony and side facade work remains'
with bpy.data.libraries.load(str(R/'scenes/MUDAM_R169_CEPHE_BALKON_ADAY_v008.blend'),link=False) as (src,dst):dst.objects=['R169_33_LEFT_BALCONIES']
for obj in dst.objects:bpy.context.scene.collection.objects.link(obj)
outfile=R/'scenes/MUDAM_R169_CEPHE_GEOMETRI_ADAY_v010.blend';bpy.ops.wm.save_as_mainfile(filepath=str(outfile),compress=True);bpy.ops.wm.open_mainfile(filepath=str(outfile))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=False;s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('QA');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=1.2
bpy.ops.object.light_add(type='AREA');light=bpy.context.object;light.location=origin+out*20+Vector((0,0,12));light.rotation_euler=(origin-light.location).to_track_quat('-Z','Y').to_euler();light.data.energy=4500;light.data.size=15;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=origin+out*35;s.camera.rotation_euler=(origin-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=26;s.render.filepath=str(R/'renders/qa/R169_33_front_geometry_v010.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_FACADE_GEOMETRY_v010.json').write_text(json.dumps(dict(scene=outfile.name,accepted=False,published=False,removed_facade_faces=len(removed),modeled_facade_fields=16,provisional_balcony_glazing_fields=4,source_pixels=rects,source_image='R169_33_facade_3_source.png',reopened=True,assumptions={'recess_m':.12,'frame_width_m':.055,'wall_top_relative_m':8.5},remaining=['Right balcony and lower entrances remain unresolved; four broad balcony glazing fields provisional','Side and rear facade still need separate reconstruction','Roof-to-wall junction must be verified before acceptance']),indent=2))
print('FRONT_GEOMETRY_SAVED',len(removed))

