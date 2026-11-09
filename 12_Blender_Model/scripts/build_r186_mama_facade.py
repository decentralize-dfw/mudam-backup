from pathlib import Path
import bpy,bmesh,json,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R183_KUZEY_MIMARI_v001.blend'));rows=[r for r in json.loads((R/'config/r176_authored_parts.json').read_text()) if r['name']=='MAMA_SHELTER'];bpy.data.objects.remove(bpy.data.objects['R176_MAMA_SHELTER'],do_unlink=True);col=bpy.data.collections.new('R176_INDEPENDENT_ARCHITECTURE');bpy.context.scene.collection.children.link(col)
def material(name,color,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
white=material('R176_PALE_MINERAL',(.7,.69,.64));bronze=material('R176_DARK_BRONZE',(.095,.075,.045),.38,.55);glass=material('R176_RECESSED_GLASS',(.07,.14,.16),.22,.35);frame=material('R176_WINDOW_FRAME',(.28,.3,.29),.35,.55);roof=material('R176_ROOF_GRAVEL',(.26,.25,.23),.95)
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name in ['R154_FAR_GROUND','R154_FAR_ROADS']:
  o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def zground(x,y):
 h,*_=ground.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),300);return h.z if h else None
records=[]
for row in rows:
 samples=[zground(x,y) for x,y in row['outer']];samples=[v for v in samples if v is not None]
 if not samples:continue
 base=min(samples)-.2;top=row['top'];bottom=8.8;verts=[];faces=[];indices=[]
 def quad(ps,mi):
  k=len(verts);verts.extend(ps);faces.append(tuple(range(k,k+len(ps))));indices.append(mi)
 for tri in row['triangles']:
  quad([(x,y,top) for x,y in tri],4);quad([(x,y,bottom) for x,y in reversed(tri)],0)
 rings=[row['outer']]+row['holes'];window_count=0
 for ring in rings:
  for aa,bb in zip(ring,ring[1:]+ring[:1]):
   a=np.array(aa);b=np.array(bb);delta=b-a;length=np.linalg.norm(delta)
   if length<.05:continue
   tangent=delta/length;normal=np.array([tangent[1],-tangent[0]]);bay=3.15 if row['facade']=='white' else 1.55;count=max(1,round(length/bay));pitch=length/count;story=(top-bottom)/row['levels']
   def point(x,z,inset=0):p=a+tangent*x-normal*inset;return (float(p[0]),float(p[1]),z)
   for floor in range(row['levels']):
    z0=bottom+floor*story;z1=z0+story
    for j in range(count):
     x0=j*pitch;x1=(j+1)*pitch
     margin=1.0;sill=1.0;head=1.1
     if pitch<=2*margin or story<=sill+head+.3:
      quad([point(x0,z0),point(x1,z0),point(x1,z1),point(x0,z1)],0);continue
     offset=.38 if floor%2 else -.38;lx=x0+margin+offset;rx=x1-margin+offset;lo=z0+sill;hi=z1-head
     quad([point(x0,z0),point(x1,z0),point(x1,lo),point(x0,lo)],0);quad([point(x0,hi),point(x1,hi),point(x1,z1),point(x0,z1)],0)
     quad([point(x0,lo),point(lx,lo),point(lx,hi),point(x0,hi)],0);quad([point(rx,lo),point(x1,lo),point(x1,hi),point(rx,hi)],0)
     corners=[(lx,lo),(rx,lo),(rx,hi),(lx,hi)]
     for c,d in zip(corners,corners[1:]+corners[:1]):quad([point(*c),point(*d),point(*d,.16),point(*c,.16)],2)
     quad([point(lx,lo,.16),point(rx,lo,.16),point(rx,hi,.16),point(lx,hi,.16)],1);window_count+=1
 me=bpy.data.meshes.new('R176_'+row['name']);me.from_pydata(verts,[],faces);me.update()
 for m in [white if row['facade']=='white' else bronze if row['facade']=='bronze' else frame,glass,frame,bronze,roof]:me.materials.append(m)
 for f,i in zip(me.polygons,indices):f.material_index=i
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);col.objects.link(o);o['source']=row['source'];o['acceptance']='Candidate; footprint and roof levels measured, facade modules pending source comparison'

 # Closed basement between source facade level and local ground prevents a floating shell.
 vs=[];fs=[];ring=row['outer'];n=len(ring)
 for z in [base,bottom]:vs.extend((x,y,z) for x,y in ring)
 fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
 from mathutils.geometry import tessellate_polygon
 for t in tessellate_polygon([[Vector((x,y,0)) for x,y in ring]]):fs.extend([tuple(reversed(t)),tuple(i+n for i in t)])
 me=bpy.data.meshes.new('R186_MAMA_FOUNDATION');me.from_pydata(vs,[],fs);me.update();obj=bpy.data.objects.new(me.name,me);col.objects.link(obj);me.materials.append(white)
s=bpy.context.scene;t=Vector((350,420,15));s.camera.location=t+Vector((50,-180,100));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=210;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R186_KUZEY_CEPHELER_v001.blend'),compress=True)
s.render.filepath=str(R/'renders/qa/R186_north_facades_v001.png');bpy.ops.render.render(write_still=True)
(R/'reports/R186_FACADES_v001.json').write_text(json.dumps(dict(accepted=False,scope='Mama smaller staggered source-visible openings and closed foundation',limits=['Module dimensions approximate from source image; no full facade acceptance','Roof terrace details still pending','Other northern architecture remains incomplete']),indent=2));print('R186_DONE')
