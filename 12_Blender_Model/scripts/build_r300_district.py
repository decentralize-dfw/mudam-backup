import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R297_DOGU_GUNEY_CATI_MALZEME_ADAY_v001.blend'));d=json.loads((R/'config/r300_district_completion.json').read_text());changed=[];removed=[]
# Replace inherited scan-based lower district envelopes only; retain the upper Rue de la Malterie group.
for o in list(bpy.context.scene.objects):
 if not o.name.startswith(('R167_MEASURED_ENVELOPE','R169_MEASURED_ENVELOPE')):continue
 bm=bmesh.new();bm.from_mesh(o.data);M=o.matrix_world;gone=[]
 for f in bm.faces:
  ys=[(M@v.co).y for v in f.verts]
  if max(ys)<-220:gone.append(f)
  elif min(ys)<-220:raise RuntimeError('Unexpected source component crossing replacement boundary')
 bmesh.ops.delete(bm,geom=gone,context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');removed.append(dict(name=o.name,faces=len(gone)))
 bm.to_mesh(o.data);bm.free();changed.append(o.name)
assert not any(o.name.startswith('ARCH_') for o in bpy.context.scene.objects),'Row already exists; do not duplicate'
before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(R/'exports/r152_clean/r300_preserved_authored_row.glb'));row=[o for o in bpy.context.scene.objects if o not in before];assert sum(o.name.startswith('ARCH_') for o in row)==322
for b in d['buildings']:
 name='R300_DISTRICT_'+str(b['id']);assert name not in bpy.data.objects;p=b['polygon'];n=len(p);v=[Vector((x,y,0)) for x,y in p];tris=tessellate_polygon([v]);faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 for tri in tris:
  ix=[q if isinstance(q,int) else min(range(n),key=lambda j:(v[j]-q).length_squared) for q in tri];faces.extend([tuple(reversed(ix)),tuple(j+n for j in ix)])
 me=bpy.data.meshes.new(name);me.from_pydata([(x,y,z) for z in [b['base'],b['top']] for x,y in p],[],faces);me.materials.append(bpy.data.materials['R171_SIMPLE_NEUTRAL_WALL']);me.materials.append(bpy.data.materials['R171_SIMPLE_NEUTRAL_ROOF']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for f in me.polygons:
  if f.normal.z>.5:f.material_index=1
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob['source']='OSM footprint '+str(b['id']);ob['height_basis']=b['heightBasis'];changed.append(name)
t=d['terrainExtension'];me=bpy.data.meshes.new('R300_DISTRICT_EDGE_GROUND');me.from_pydata(t['vertices'],[],t['faces']);me.materials.append(bpy.data.materials['R154_FAR_GROUND'].material_slots[0].material) if 'R154_FAR_GROUND' in bpy.data.materials else me.materials.append(bpy.data.objects['R182_EXTENSION_GROUND'].data.materials[0]);me.update();uv=me.uv_layers.new()
for l in me.loops:p=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(p.x/8,p.y/8)
for f in me.polygons:f.use_smooth=True
ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob);changed.append(ob.name)
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS','R300_DISTRICT_EDGE_GROUND'] or o.name.startswith(('R182_EXTENSION_','R210_GROUND_CONTINUITY_','R202_ALZETTE_'))):continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True);contacts=[]
for name in [n for n in changed if n.startswith('R300_DISTRICT_') and n!='R300_DISTRICT_EDGE_GROUND']+['R182_DISTRICT_164184549','R182_DISTRICT_930614764','R171_546345955']:
 o=bpy.data.objects[name];world=[o.matrix_world@v.co for v in o.data.vertices];base=min(p.z for p in world);ids=[i for i,p in enumerate(world) if abs(p.z-base)<.001];samples=[];missing=[]
 for e in o.data.edges:
  a,b=e.vertices
  if a not in ids or b not in ids:continue
  p,q=world[a],world[b]
  for j in range(max(2,math.ceil((q-p).length/.5))+1):
   v=p.lerp(q,j/max(2,math.ceil((q-p).length/.5)));h,*_=ground.ray_cast(Vector((v.x,v.y,150)),Vector((0,0,-1)),400)
   if h:samples.append(h.z)
   else:missing.append(tuple(v))
 extension=max(0,base-min(samples)+.12) if samples and not missing else 0
 if extension>.001:
  for i in ids:o.data.vertices[i].co.z-=extension
  if name not in changed:changed.append(name)
 contacts.append(dict(name=name,missing=missing,samples=len(samples),extension=extension,waterIncludedAsMinimumFoundationSupport=True))
path=R/'scenes/MUDAM_R300_ALT_MAHALLE_13_KUTLE_TAMAMLAMA_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;target=Vector((0,-345,-60));s.camera.location=target+Vector((100,-400,320));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=1100;s.render.resolution_x=1600;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R300_lower_district.png');bpy.ops.render.render(write_still=True)
for o in s.objects:o.select_set(o.name in changed and o.type=='MESH' and len(o.data.polygons)>0 or o.name.startswith('ARCH_'))
glb=R/'exports/r152_clean/r300_district_delta_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R300_DISTRICT_COMPLETION.json').write_text(json.dumps(dict(accepted=False,published=False,newBuildings=d['buildings'],preservedAuthoredRowNodes=322,removedInheritedFaces=removed,contacts=contacts,checks=checks,scope='151 mapped lower-district footprint IDs accounted for:134 existing,13 new,4 detailed preserved row; not complete ground or cadastral acceptance',limits=['Unmeasured abstract roof heights remain labeled','Foundation depth not surveyed','Other firstsix regions still incomplete']),indent=2));print('R300_READY',flush=True)
