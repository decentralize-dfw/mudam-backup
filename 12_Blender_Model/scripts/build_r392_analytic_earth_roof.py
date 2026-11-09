import bpy,bmesh,json,ast,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R389_KALE_KADEMELI_CATI_ADAY_v001.blend'));d=json.loads((R/'reports/R392_ANALYTIC_EARTH_ROOF.json').read_text());assert d['check']['valid'];records=[];regions=[[(-150,50),(50,50),(50,-150)]]
src=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(a for a in src.body if isinstance(a,ast.FunctionDef) and a.name=='clip');loop=next(a for a in src.body if isinstance(a,ast.For) and isinstance(a.target,ast.Name) and a.target.id=='ob');code=ast.unparse(loop).replace("['R152_CLASS2_TERRAIN']","['R154_FORT_ROUNDED_EARTH_ROOF']");exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));exec(compile(code,'<earth replacement domain>','exec'))
vs=d['vertices'];fs=d['faces'];n=len(vs);edges={}
for f in fs:
 for a,b in zip(f,f[1:]+f[:1]):
  key=tuple(sorted((a,b)));edges.setdefault(key,[]).append((a,b))
allvs=vs+[(x,y,z-.25) for x,y,z in vs];allfs=fs+[[i+n for i in reversed(f)] for f in fs]
for seen in edges.values():
 if len(seen)==1:a,b=seen[0];allfs.append([a,a+n,b+n,b])
me=bpy.data.meshes.new('R392_FORT_ARCHITECTURAL_EARTH_COVER');me.from_pydata(allvs,[],allfs);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);mat=bpy.data.objects['R154_FORT_ROUNDED_EARTH_ROOF'].data.materials[0].copy();mat.name='R392_FORT_DRY_EARTH_COVER';p=mat.node_tree.nodes.get('Principled BSDF')
# Existing normal/roughness assets remain; the visible source shows mineral
# brown earth on the cover, rather than the previous saturated lawn colour.
for link in list(p.inputs['Base Color'].links):mat.node_tree.links.remove(link)
p.inputs['Base Color'].default_value=(.24,.205,.14,1);p.inputs['Roughness'].default_value=.94;me.materials.append(mat)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
for loop in me.loops:
 v=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x/4,v.y/4)
for f in me.polygons:f.use_smooth=True
o['level_id']='SITE';o['source']=d['method'];o['heldoutRMS_m']=d['check']['rms'];o['accepted']=False
def distance(x,y,outline):
 best=1e9
 for (a,b),(c,e) in zip(outline,outline[1:]+outline[:1]):
  den=(c-a)**2+(e-b)**2;t=max(0,min(1,((x-a)*(c-a)+(y-b)*(e-b))/den)) if den else 0;best=min(best,math.hypot(x-a-t*(c-a),y-b-t*(e-b)))
 return best
raw=json.loads((R/'reports/R388_EARTH_PROFILE.json').read_text());arms=d['profiles']['arms'];heads=d['profiles']['heads']
def smooth(v):v=max(0,min(1,v));return v*v*(3-2*v)
def zfun(x,y):
 di=distance(x,y,raw['inner']);do=distance(x,y,raw['outline'])
 def arm(k):c=arms[k]['coef'];return c[0]+c[1]*di-c[2]*math.exp(-do/c[3])
 def head(k):c=heads[k]['coef'];return max(c[5],c[0]+c[1]*di-c[2]*math.exp(-max(0,do-c[4])/c[3]))
 w=smooth(y-x-5.5);z=arm('east_arm')*(1-w)+arm('west_arm')*w;w=smooth(x+22.5);z=z*(1-w)+head('east_head')*w;w=smooth(y+14.5);return z*(1-w)+head('north_head')*w
body=bpy.data.objects['R154_FORT_MASONRY_BODY'];changed=0
for v in body.data.vertices:
 x,y,z=v.co
 if abs(z-2.9)<.001 and x+y>=-100:
  v.co.z=zfun(x,y);changed+=1
body.data.update();out=R/'scenes/MUDAM_R392_KALE_BAGIMSIZ_TOPRAK_ORTU_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));ob=bpy.data.objects['R392_FORT_ARCHITECTURAL_EARTH_COVER'];bm=bmesh.new();bm.from_mesh(ob.data);check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();assert not check['nonManifold'] and not check['zeroArea'],check
bpy.ops.object.select_all(action='DESELECT')
for name in ['R392_FORT_ARCHITECTURAL_EARTH_COVER','R154_FORT_MASONRY_BODY','R154_FORT_ROUNDED_EARTH_ROOF']:
 bpy.data.objects[name].select_set(True)
for ob in bpy.context.scene.objects:
 if ob.name.startswith('R389_'):ob.select_set(True)
glb=R/'exports/r152_clean/r392_fort_roof_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
report=dict(scene=out.name,accepted=False,published=False,meshCheck=check,heldout=d['check'],bodyEaveVerticesChanged=changed,clipped=records,limits=d['limits']+['Whole museum ring remains unaccepted. Exterior wall windows and tower-end junction still require matching.']);(R/'reports/R392_FORT_ROOF.json').write_text(json.dumps(report,indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-42,-34,100));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-42,-34,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=65;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R392_fort_roof_candidate.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));errors=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':
  bad=sum(not all(math.isfinite(x) for x in v.co) for v in ob.data.vertices);zero=sum(p.area<1e-10 for p in ob.data.polygons)
  if bad or zero:errors.append(dict(name=ob.name,nonFinite=bad,zeroArea=zero))
report['glbErrors']=errors;(R/'reports/R392_FORT_ROOF.json').write_text(json.dumps(report,indent=2));print('R392_READY',check,errors)

