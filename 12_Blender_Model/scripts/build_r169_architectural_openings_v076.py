from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_YENIDEN_KURULUM_v075.blend'))
o=bpy.data.objects['ARCH_WALL_MASS_2'];verts=[v.co.copy() for v in o.data.vertices];a,b=verts[:2];t=(b-a).normalized();n=Vector((t.y,-t.x,0));# polygon front normal checked against known outward
n=Vector((.208791494,-.977960169,0));center=Vector((-78.6563873,-306.0042725,-69));right=Vector((.9779602885,.2087912709,0));scale=36/2048
# Source image displayed at2048x791; explicit traces, not generated/random windows.
rects=[(112,253,205,356),(352,249,465,356),(1095,250,1238,365),(1323,259,1418,365),(1805,247,1930,351),(345,458,466,540),(1280,472,1416,543)]
length=(b-a).length;openings=[]
for x0,y0,x1,y1 in rects:
 p0=center+right*((x0-1024)*scale);p1=center+right*((x1-1024)*scale);u0=(p0-a).dot(t);u1=(p1-a).dot(t);z0=-69+(395.636-y1)*scale;z1=-69+(395.636-y0)*scale;openings.append((min(u0,u1),max(u0,u1),z0,z1))
xs=sorted(set([0,length]+[v for w in openings for v in w[:2]]));zs=sorted(set([-75,max(verts[2].z,verts[3].z)]+[v for w in openings for v in w[2:]]));mv=[];mf=[]
def point(u,z,depth=0):return a+t*u+Vector((0,0,z-a.z))-n*depth
def quad(coords):
 i=len(mv);mv.extend(coords);mf.append((i,i+1,i+2,i+3))
for u0,u1 in zip(xs,xs[1:]):
 for z0,z1 in zip(zs,zs[1:]):
  mid=((u0+u1)/2,(z0+z1)/2)
  if any(l<mid[0]<r and lo<mid[1]<hi for l,r,lo,hi in openings):continue
  top0=verts[3].z+(verts[2].z-verts[3].z)*u0/length;top1=verts[3].z+(verts[2].z-verts[3].z)*u1/length
  if z0>=min(top0,top1):continue
  quad([point(u0,z0),point(u1,z0),point(u1,min(z1,top1)),point(u0,min(z1,top0))])
for l,r,lo,hi in openings:
 for s,e in [((l,lo),(r,lo)),((r,lo),(r,hi)),((r,hi),(l,hi)),((l,hi),(l,lo))]:quad([point(*s),point(*e),point(*e,.16),point(*s,.16)])
me=bpy.data.meshes.new('Architectural wall with traced openings');me.from_pydata(mv,[],mf);me.update();oldmat=o.data.materials[0];o.data=me;o.data.materials.append(oldmat)
def material(name,color,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.3;return m
frame=material('Painted light window frames',(.72,.72,.68));glass=material('Glazing subdued blue grey',(.085,.14,.17),.2)
def box(name,u,z,w,h,depth,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=point(u,z,depth));obj=bpy.context.object;obj.name=name;obj.rotation_euler[2]=__import__('math').atan2(t.y,t.x);obj.dimensions=(w,.07,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat)
for i,(l,r,lo,hi) in enumerate(openings):
 box(f'ARCH_GLASS_{i}',(l+r)/2,(lo+hi)/2,r-l-.10,hi-lo-.10,.17,glass)
 for u in [l+.035,r-.035,l+(r-l)/3,l+2*(r-l)/3]:box(f'ARCH_FRAME_VERTICAL_{i}',u,(lo+hi)/2,.07,hi-lo,.12,frame)
 for z in [lo+.035,hi-.035]:box(f'ARCH_FRAME_HORIZONTAL_{i}',(l+r)/2,z,r-l,.07,.12,frame)
 box(f'ARCH_SILL_{i}',(l+r)/2,lo-.035,r-l+.10,.07,-.015,frame)
s=bpy.context.scene;s['acceptance']='Unaccepted architectural work in progress; seven source-visible window groups traced; recess/frame dimensions provisional; remaining facade/roof details pending.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_ACIKLIKLAR_v076.blend'));s.render.filepath=str(R/'renders/qa/R169_architectural_openings_v076.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_ARCHITECTURAL_OPENINGS_v076.json').write_text(json.dumps(dict(accepted=False,source='R169_arch_front_reference_v075.png',trace_space=[2048,791.2727],rectangles=rects,window_groups=7,method='Actual holes in independent wall mesh, reveals, separate frames, sill and glazing. No scan mesh/texture.',assumptions={'reveal_depth':.16,'frame_width':.07},remaining=['Other visible and obscured openings','Mansard/dormer band','Roof features','Roof overhang/body interface','Ground and GLB validation']),indent=2));print('AUTHORED_OPENINGS_SAVED')
