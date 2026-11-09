exec(open('12_Blender_Model/scripts/build_r255_tower_a.py',encoding='utf-8-sig').read().split('M={};ring=')[0].replace('MUDAM_R254_OVAL_BUTUNLESIK_ADAY_v001.blend','MUDAM_R255_KUZEY_KULE_A_MIMARI_ADAY_v001.blend'))
M={};ring=[Vector(p) for p in [(246,382),(269,400),(241,435),(223,421)]];top=88.35;bottom=6.0
pixels=[1054,1016,976,936,896,856,816,776,736,696,656,616,576,536,496,456,416,376,336,296,256];levels=[7+(1146.991810-y)/11.007373 for y in pixels]
for edge,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
 u=(b-a).normalized();normal=Vector((u.y,-u.x));n=[18,26,14,26][edge]
 box('R256_B_BASE',a,b,bottom,levels[0]-.2,.4,dark)
 for z in levels:box('R256_B_FLOOR_BANDS',a,b,z-.22,z+.22,.44,metal)
 for lo,hi in zip(levels,levels[1:]+[top]):
  if hi-lo<.5:continue
  for j in range(n):box('R256_B_RECESSED_GLAZING',a.lerp(b,j/n)+u*.045-normal*.12,a.lerp(b,(j+1)/n)-u*.045-normal*.12,lo+.22,hi-.22,.07,glass)
 for j in range(n+1):
  p=a.lerp(b,j/n);major=j%6==0;w=.16 if major else .045;box('R256_B_MULLIONS',p-u*w,p+u*w,levels[0]-.22,top,.4 if major else .24,metal)
 box('R256_B_COPING',a,b,top-.2,top,.4,metal)
def poly(name,ps,ma):
 V[name]=[tuple(p) for p in ps];F[name]=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];M[name]=ma
poly('R256_B_ROOF_DECK',[(p.x,p.y,z) for z in [top-.3,top] for p in ring],roof);poly('R256_B_FLOOR',[(p.x,p.y,z) for z in [bottom,bottom+.3] for p in ring],roof)
patches=json.loads((R/'config/r256_tower_roof_planes.json').read_text())
for i,p in enumerate(patches):
 c=p['plane'];q=[Vector((x,y,c[0]*x+c[1]*y+c[2])) for x,y in p['ring']]
 # Separate closed glazed roof plates and closed vertical skirts connect to main roof.
 poly('R256_B_SLOPED_GLASS_'+str(i),[v-Vector((0,0,.10)) for v in q]+q,glass)
 for j,(a,b) in enumerate(zip(q,q[1:]+q[:1])):
  d=(b-a);u=Vector((d.x,d.y,0)).normalized();n=Vector((-u.y,u.x,0))*.07
  poly('R256_B_ROOF_UPSTAND_'+str(i)+'_'+str(j),[Vector((v.x,v.y,top-.05)) for v in [a-n,b-n,b+n,a+n]]+[a-n,b-n,b+n,a+n],dark)
 # Planar rail grids; spacing measured approximately from visible roof raster.
 for along,count in [(True,18),(False,12)]:
  for j in range(count+1):
   t=j/count;a=q[0].lerp(q[1] if along else q[3],t);b=q[3].lerp(q[2],t) if along else q[1].lerp(q[2],t);u=(b-a).normalized();v=u.cross(Vector((0,0,1))).normalized()*.045;w=u.cross(v).normalized()*.045
   poly('R256_B_ROOF_BAR_'+str(i)+'_'+str(along)+'_'+str(j),[p+x*v+y*w for p in [a,b] for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]],metal)
for name,v in V.items():
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],F[name]);me.materials.append(M[name]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
o=bpy.data.objects.get('R165_MEASURED_ENVELOPE')
if o:bpy.data.objects.remove(o,do_unlink=True)
p=R/'scenes/MUDAM_R256_IKI_KULE_MIMARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True);bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.camera.location=(390,180,65);s.camera.rotation_euler=(Vector((240,370,48))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=145;s.render.resolution_x=1600;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R256_towers_authored.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name.startswith('R256_'))
glb=R/'exports/r152_clean/r256_tower_b_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R256_TOWER_B.json').write_text(json.dumps(dict(accepted=False,published=False,levels=levels,checks=checks,limits=['Four measured planar roof plates; service gap detail unresolved','Rear facade divisions provisional','Main footprint simplification and base contacts require verification','Not a completed region6']),indent=2));assert checks and all(not c['boundary'] and not c['zero'] for c in checks);print('R256_READY',flush=True)
