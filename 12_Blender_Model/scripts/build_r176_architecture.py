from pathlib import Path
import bpy,bmesh,json,math,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R175_DEMIRYOLU_VIYADUK_v001.blend'));rows=json.loads((R/'config/r176_authored_parts.json').read_text());col=bpy.data.collections.new('R176_INDEPENDENT_ARCHITECTURE');bpy.context.scene.collection.children.link(col)
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
 base=min(samples)-.2;top=row['top'];bottom=float(np.median(samples))+10 if row['name']=='ANNEAU' else base;verts=[];faces=[];indices=[]
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
     margin=.65 if row['facade']=='white' else .07;sill=.75 if row['facade']=='white' else .18;head=.55 if row['facade']=='white' else .18
     if pitch<=2*margin or story<=sill+head+.3:
      quad([point(x0,z0),point(x1,z0),point(x1,z1),point(x0,z1)],0);continue
     lx=x0+margin;rx=x1-margin;lo=z0+sill;hi=z1-head
     quad([point(x0,z0),point(x1,z0),point(x1,lo),point(x0,lo)],0);quad([point(x0,hi),point(x1,hi),point(x1,z1),point(x0,z1)],0)
     quad([point(x0,lo),point(lx,lo),point(lx,hi),point(x0,hi)],0);quad([point(rx,lo),point(x1,lo),point(x1,hi),point(rx,hi)],0)
     corners=[(lx,lo),(rx,lo),(rx,hi),(lx,hi)]
     for c,d in zip(corners,corners[1:]+corners[:1]):quad([point(*c),point(*d),point(*d,.16),point(*c,.16)],2)
     quad([point(lx,lo,.16),point(rx,lo,.16),point(rx,hi,.16),point(lx,hi,.16)],1);window_count+=1
 me=bpy.data.meshes.new('R176_'+row['name']);me.from_pydata(verts,[],faces);me.update()
 for m in [white if row['facade']=='white' else bronze if row['facade']=='bronze' else frame,glass,frame,bronze,roof]:me.materials.append(m)
 for f,i in zip(me.polygons,indices):f.material_index=i
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);col.objects.link(o);o['source']=row['source'];o['acceptance']='Candidate; footprint and roof levels measured, facade modules pending source comparison'
 if row['name']=='ANNEAU':
  path=np.array(row['outer']);ds=np.linalg.norm(np.roll(path,-1,axis=0)-path,axis=1);cum=np.r_[0,np.cumsum(ds)]
  for i,s in enumerate(np.linspace(0,cum[-1],116,endpoint=False)):
   k=min(len(path)-1,np.searchsorted(cum,s,side='right')-1);t=(s-cum[k])/ds[k];p=path[k]*(1-t)+path[(k+1)%len(path)]*t;z=zground(*p);z=(z-.15) if z is not None else base
   bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.24,depth=bottom-z,location=(*p,(bottom+z)/2));pillar=bpy.context.object;pillar.name='R176_ANNEAU_COLUMN_%03d'%i
   for old in list(pillar.users_collection):old.objects.unlink(pillar)
   col.objects.link(pillar);pillar.data.materials.append(bronze)
 records.append({'name':row['name'],'base':base,'wall_bottom':bottom,'roof':top,'glazed_panels':window_count,'source':row['source'],'accepted':False})
s=bpy.context.scene;t=Vector((125,470,15));s.camera.location=t+Vector((180,-320,250));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=580;s.render.resolution_x=1500;s.render.resolution_y=1100;s.cycles.samples=16
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R176_KUZEY_EKSIK_BINALAR_v001.blend'),compress=True)
for o in s.objects:o.select_set(o.name.startswith('R176_'))
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r176_buildings_REVIEW.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
(R/'reports/R176_ARCHITECTURAL_v001.json').write_text(json.dumps({'accepted':False,'buildings':records,'limitations':['Only source roof modes and mapped footprint constraints established','Opening rhythm is candidate, not measured module acceptance','Ring116columns and10m clearance supported by Curia; exact column placement not established','Partial source coverage; no whole11region acceptance'],'sources':['https://curia.europa.eu/site/jcms/qua3_6433/es/el-anillo','https://curia.europa.eu/site/upload/docs/application/pdf/2022-06/qd-ar-22-001-en-n.pdf']},indent=2))
s.render.filepath=str(R/'renders/qa/R176_authored_north.png');bpy.ops.render.render(write_still=True);print('R176_DONE',records)
