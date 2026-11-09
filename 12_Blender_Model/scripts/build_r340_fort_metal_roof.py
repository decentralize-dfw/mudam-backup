import bpy,bmesh,json,ast,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R334_HENDEK_CAKISMA_TEMIZLIK_ADAY_v001.blend'));data=json.loads((R/'reports/R340_ROOF_BUILD_INPUT.json').read_text());assert data['lower']['valid'] and data['upper']['valid']
# Retain the existing surround geometry outside the corrected metal outline.
# Its grading is deliberately not reported as measured acceptance.
regions=[];records=[];poly=data['roofOutline']
for face in tessellate_polygon([[Vector((x,y,0)) for x,y in poly]]):regions.append([poly[i] if isinstance(i,int) else (i.x,i.y) for i in face])
source=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='clip');loop=next(n for n in source.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='ob');code=ast.unparse(loop).replace("['R152_CLASS2_TERRAIN']","['R154_FORT_METAL_ROOF','R154_FORT_ROUNDED_EARTH_ROOF']")
exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));exec(compile(code,'<roof footprint>','exec'))
old=bpy.data.objects['R154_FORT_METAL_ROOF'];old.data.materials.clear();old.data.materials.append(bpy.data.objects['R154_FORT_ROUNDED_EARTH_ROOF'].data.materials[0]);old['R340_scope']='Existing surround retained outside corrected metal outline; grading remains candidate.'
names=[]
def slab(name,points,plane,bottom):
 a,b,c=plane;n=len(points);vs=[(x,y,bottom(x,y)) for x,y in points]+[(x,y,a*x+b*y+c) for x,y in points];faces=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(bpy.data.materials['R154_FORT_ZINC']);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
 for l in me.loops:
  v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x,v.y)
 ob['level_id']='SITE';ob['source']='Independent closed architectural roof plane, source-traced outline and classified LiDAR held-out validation R338; no source faces.';names.append(name);return ob
a,b,c=data['lower']['plane'];slab('R340_FORT_LOWER_METAL_ROOF',poly,data['lower']['plane'],lambda x,y:a*x+b*y+c-.15)
slab('R340_FORT_RAISED_METAL_ROOF',data['raisedOutline'],data['upper']['plane'],lambda x,y:a*x+b*y+c-.02)
out=R/'scenes/MUDAM_R340_KALE_METAL_CATI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
bpy.ops.object.select_all(action='DESELECT')
for name in names+[r['name'] for r in records]:bpy.data.objects[name].select_set(True)
glb=R/'exports/r152_clean/r340_fort_roof_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-42,-34,100));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-42,-34,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=65;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R340_fort_roof_candidate.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));errors=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':
  bad=sum(not all(math.isfinite(v) for v in x.co) for x in ob.data.vertices);zero=sum(p.area<1e-10 for p in ob.data.polygons)
  if bad or zero:errors.append(dict(name=ob.name,nonFinite=bad,zeroArea=zero))
(R/'reports/R340_FORT_ROOF.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,meshChecks=checks,glbErrors=errors,clipped=records,limits=['Corrected metal planes only; inherited surround grading, old upstand, earth roof and tower interfaces unresolved.','Source outline is visual reconstruction; not survey identity.']),indent=2));print('R340_READY',checks,errors)
