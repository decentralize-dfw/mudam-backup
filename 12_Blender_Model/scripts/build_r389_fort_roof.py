import bpy,bmesh,json,ast,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R378_DOGU_UZUN_HENDEK_ZEMIN_ADAY_v001.blend'))
d=json.loads((R/'reports/R387_ROOF_INPUT.json').read_text());roof=d['roofOutline'];crest=d['crestOutline'];n=len(roof);assert n==len(crest)
regions=[];records=[]
for face in tessellate_polygon([[Vector((x,y,0)) for x,y in crest]]):regions.append([crest[i] if isinstance(i,int) else (i.x,i.y) for i in face])
src=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(a for a in src.body if isinstance(a,ast.FunctionDef) and a.name=='clip');loop=next(a for a in src.body if isinstance(a,ast.For) and isinstance(a.target,ast.Name) and a.target.id=='ob');code=ast.unparse(loop).replace("['R152_CLASS2_TERRAIN']","['R154_FORT_ROUNDED_EARTH_ROOF']")
exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));exec(compile(code,'<earth opening>','exec'))
for name in ['R154_FORT_METAL_ROOF','R154_FORT_METAL_UPSTAND']:
 ob=bpy.data.objects[name];ob.hide_render=True;ob.hide_set(True);ob.hide_viewport=True;ob['R389_replaced']='Independent measured stepped roof, ledge and parapet.'
names=[]
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(bpy.data.materials[mat]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
 for loop in me.loops:
  v=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x,v.y)
 ob['level_id']='SITE';ob['source']='Independent architectural roof components; R336 visual plan, R338 planes, R386 classified edge sections. No scan faces.';names.append(name);return ob
def plane(p,x,y):return p[0]*x+p[1]*y+p[2]
def slab(name,xy,top,bottom,mat):
 k=len(xy);vs=[(x,y,bottom(x,y)) for x,y in xy]+[(x,y,top(x,y)) for x,y in xy];fs=[list(range(k-1,-1,-1)),list(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)];return mesh(name,vs,fs,mat)
low=lambda x,y:plane(d['lowerPlane'],x,y)
slab('R389_FORT_LOWER_METAL_ROOF',roof,low,lambda x,y:low(x,y)-.18,'R154_FORT_ZINC')
slab('R389_FORT_RAISED_METAL_ROOF',d['raisedOutline'],lambda x,y:plane(d['upperPlane'],x,y),lambda x,y:low(x,y)-.02,'R154_FORT_ZINC')
# Ring sections have corresponding measured stations; the stepped ledge is
# separate from the vertical historic parapet. Both are closed solids.
def ring(name,inner,outer,zi,zo,bottom,mat):
 k=len(inner);vs=[(x,y,z) for line,zfunc in [(inner,zi),(outer,zo),(inner,bottom),(outer,bottom)] for x,y in line for z in [zfunc(x,y)]];fs=[]
 for i in range(k):
  j=(i+1)%k;fs.extend([(i,j,k+j,k+i),(2*k+i,3*k+i,3*k+j,2*k+j),(i,2*k+i,2*k+j,j),(k+i,k+j,3*k+j,3*k+i)])
 return mesh(name,vs,fs,mat)
edge=[]
for i,p in enumerate(crest):
 a=Vector(crest[i-1]);b=Vector(crest[(i+1)%n]);t=(b-a).normalized();normal=Vector((t.y,-t.x))
 # Clockwise outline: left normal points outwards.
 area=sum(crest[j][0]*crest[(j+1)%n][1]-crest[(j+1)%n][0]*crest[j][1] for j in range(n))
 if area<0:normal=-normal
 edge.append(tuple(Vector(p)+normal*.24))
ring('R389_FORT_PERIMETER_LEDGE',roof,crest,lambda x,y:2.21,lambda x,y:2.21,lambda x,y:1.75,'R154_FORT_ZINC')
ring('R389_FORT_INNER_PARAPET',crest,edge,lambda x,y:3.49,lambda x,y:3.49,lambda x,y:1.75,'R154_FORT_STONE_PBR')
# A continuous metal coping closes the upper edge; its 6cm construction
# thickness is a modeling choice, not a claimed survey dimension.
ring('R389_FORT_INNER_COPING',crest,edge,lambda x,y:3.55,lambda x,y:3.55,lambda x,y:3.49,'R154_FORT_ZINC')
out=R/'scenes/MUDAM_R389_KALE_KADEMELI_CATI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(x['nonManifold'] or x['zeroArea'] for x in checks),checks
bpy.ops.object.select_all(action='DESELECT')
for name in names:bpy.data.objects[name].select_set(True)
glb=R/'exports/r152_clean/r389_fort_roof_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
(R/'reports/R389_FORT_ROOF.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,meshChecks=checks,clipped=records,limits=['Earth cover outside corrected opening remains inherited and requires reconstruction','End junction and upper roof/ledge transition require visual acceptance','Parapet crest nominal 3.49m from classified sections; local crest variation unresolved','No whole-ring acceptance']),indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-42,-34,100));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-42,-34,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=65;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R389_fort_roof_candidate.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));errors=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':
  bad=sum(not all(math.isfinite(x) for x in v.co) for v in ob.data.vertices);zero=sum(p.area<1e-10 for p in ob.data.polygons)
  if bad or zero:errors.append(dict(name=ob.name,nonFinite=bad,zeroArea=zero))
report=json.loads((R/'reports/R389_FORT_ROOF.json').read_text());report['glbErrors']=errors;(R/'reports/R389_FORT_ROOF.json').write_text(json.dumps(report,indent=2));assert not errors;print('R389_READY',checks)
