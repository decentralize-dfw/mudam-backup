import bpy,bmesh,math
from mathutils import Vector
def mesh(name,vs,fs,ma):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(ma);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o['level_id']='SITE';names.append(name)
 uv=me.uv_layers.new(name='UVMap')
 for l in me.loops:
  p=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(math.atan2(p.y-cy,p.x-cx)*r/1.6,p.z/1.6)
 return o
def cut_window(phi,width,lo,hi):
 normal=Vector((math.cos(phi),math.sin(phi),0));tangent=Vector((-normal.y,normal.x,0));p=Vector((cx,cy,0))+normal*r;vs=[tuple(p+tangent*x+normal*depth+Vector((0,0,z))) for depth in [-.5,.2] for x,z in [(-width/2,lo),(width/2,lo),(width/2,hi),(-width/2,hi)]];o=mesh('R419_TEMP_CUT',vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone);bpy.context.view_layer.objects.active=tower;mod=tower.modifiers.new('Photo visible rectangular recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=o;bpy.ops.object.modifier_apply(modifier=mod.name);names.remove(o.name);bpy.data.objects.remove(o,do_unlink=True)
def stonepiece(poly,phi):
 k=len(poly);start=len(vs)
 for dep in [-.01,.045]:
  for x,z in poly:
   a=phi+x/r;vs.append((cx+(r+dep)*math.cos(a),cy+(r+dep)*math.sin(a),z))
 fs.extend([[start+i for i in range(k-1,-1,-1)],[start+k+i for i in range(k)]]);fs.extend([(start+i,start+(i+1)%k,start+(i+1)%k+k,start+i+k) for i in range(k)])
