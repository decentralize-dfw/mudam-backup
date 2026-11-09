import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R405_KALE_DOGU_DUVAR_ACIKLIKLARI_ADAY_v001.blend'));d=json.loads((R/'reports/R405_WALL_OPENINGS.json').read_text());outline=json.loads((R/'.local_source_cache/r154/fort.json').read_text())['footprint'];vs=[];fs=[]
ma=bpy.data.materials.new('R406_FORT_DRESSED_SANDSTONE');ma.use_nodes=True;pr=ma.node_tree.nodes.get('Principled BSDF');pr.inputs['Base Color'].default_value=(.42,.365,.275,1);pr.inputs['Roughness'].default_value=.86
def prism(poly,p,t,n):
 k=len(poly);base=len(vs);vs.extend(tuple(p+t*x+n*depth+Vector((0,0,z))) for depth in [-.025,.07] for x,z in poly);fs.extend([[base+i for i in range(k-1,-1,-1)],[base+k+i for i in range(k)]]);fs.extend([(base+i,base+(i+1)%k,base+(i+1)%k+k,base+i+k) for i in range(k)])
for row in d['openings']:
 i=row['wallSegment'];v=Vector(outline[i+1])-Vector(outline[i]);t=Vector((v.x,v.y,0)).normalized();n=Vector((t.y,-t.x,0));p=Vector(row['center'])
 if n.dot(Vector((0,-90,-.5))-p)<0:n=-n
 if row['kind']=='round_opening':
  for j in range(24):
   a=math.tau*j/24;b=math.tau*(j+1)/24;prism([(.34*math.cos(a),.34*math.sin(a)),(.34*math.cos(b),.34*math.sin(b)),(.47*math.cos(b),.47*math.sin(b)),(.47*math.cos(a),.47*math.sin(a))],p,t,n)
 elif row['kind']=='segmental_arch_recess':
  for j in range(12):
   a=math.pi*j/12;b=math.pi*(j+1)/12;prism([(.575*math.cos(a),.4+.30*math.sin(a)),(.575*math.cos(b),.4+.30*math.sin(b)),(.735*math.cos(b),.4+.46*math.sin(b)),(.735*math.cos(a),.4+.46*math.sin(a))],p,t,n)
  for sign in [-1,1]:prism([(sign*.575,-.72),(sign*.735,-.72),(sign*.735,.4),(sign*.575,.4)],p,t,n)
  prism([(-.75,-.84),(.75,-.84),(.75,-.72),(-.75,-.72)],p,t,n)
  # Pale blocked-back faces are visible in photo086. Preserve the true recess,
  # coloring only its back plane rather than covering the opening with a decal.
  body=bpy.data.objects['R154_FORT_MASONRY_BODY']
  if ma.name not in body.data.materials:body.data.materials.append(ma)
  idx=list(body.data.materials).index(ma)
  for face in body.data.polygons:
   v=face.center-p;xx=v.dot(t);zz=v.z;dep=v.dot(n)
   if -.57<dep<-.53 and abs(xx)<.59 and -.73<zz<.72:face.material_index=idx
me=bpy.data.meshes.new('R406_FORT_EAST_OPENING_STONEWORK');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(ma);o['level_id']='SITE';o['source']='Photo086 round stone collars, segmental lintels and sill/jamb dressings; R405 source-located openings. Dressing thickness visual estimate.';bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();assert not check['nonManifold'] and not check['zeroArea'],check
out=R/'scenes/MUDAM_R406_KALE_DOGU_TAS_ACIKLIK_DETAYI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R406_STONEWORK.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,check=check,scope='Five visible circular and segmental openings; 19 recesses preserved. Not whole fort acceptance.'),indent=2))
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and ob.name not in ['R154_FORT_MASONRY_BODY','R406_FORT_EAST_OPENING_STONEWORK']:ob.hide_render=True
s=bpy.context.scene;eye=Vector((0,-90,-.5));bpy.ops.object.camera_add(location=eye);s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-39,-42,-.5))-eye).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=55;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R406_fort_east_wall_candidate.png');bpy.ops.render.render(write_still=True);print('R406_READY')
