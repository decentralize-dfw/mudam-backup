import bpy,bmesh,json,ast,math
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R401_KALE_ACIK_TERAS_UCU_ADAY_v001.blend'))
# Trace of low court visible between the three tower footprints and raised
# shoulders. ACT is a boundary reference only; elevations are independently
# checked against classified returns, not a copied/resampled scan surface.
pixels=[(137,760),(180,785),(232,765),(326,847),(307,894),(343,952),(276,978),(128,840)]
xy=[(-74.5+x*65/1100,-1.5-y*65/1100) for x,y in pixels];control=json.loads((R/'reports/R399_FRONT_COURT_PLANES.json').read_text())['tower_forecourt'];assert control['valid'];c=control['plane'];z=lambda x,y:c[0]*x+c[1]*y+c[2]
def solid(name,lo,hi,material=None):
 n=len(xy);vs=[(x,y,fn(x,y)) for fn in [lo,hi] for x,y in xy];fs=[]
 for tr in tessellate_polygon([[Vector((x,y,0)) for x,y in xy]]):
  ids=[i if isinstance(i,int) else min(range(n),key=lambda j:(Vector((*xy[j],0))-i).length) for i in tr];fs.extend([ids[::-1],[i+n for i in ids]])
 fs.extend([(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 if material:me.materials.append(material)
 uv=me.uv_layers.new(name='UVMap')
 for l in me.loops:
  p=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(p.x/5,p.y/5)
 return o
cut=solid('R402_TEMP_COURT_CUT',lambda x,y:z(x,y)-.015,lambda x,y:12)
body=bpy.data.objects['R154_FORT_MASONRY_BODY'];bm=bmesh.new();bm.from_mesh(body.data);baseline_boundary=sum(not e.is_manifold for e in bm.edges);bm.free();bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('R402_measured_low_court','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
regions=[];records=[]
for tr in tessellate_polygon([[Vector((x,y,0)) for x,y in xy]]):regions.append([xy[i] if isinstance(i,int) else (i.x,i.y) for i in tr])
src=ast.parse((R/'scripts/build_r322_west_museum_terrace.py').read_text());clip=next(a for a in src.body if isinstance(a,ast.FunctionDef) and a.name=='clip');loop=next(a for a in src.body if isinstance(a,ast.For) and isinstance(a.target,ast.Name) and a.target.id=='ob');exec(compile(ast.Module(body=[clip],type_ignores=[]),'<clip>','exec'));exec(compile(ast.unparse(loop).replace("['R152_CLASS2_TERRAIN']","['R154_FORT_ROUNDED_EARTH_ROOF']"),'<court roof cut>','exec'))
ma=bpy.data.materials.new('R402_LOW_COURT_GRASS');ma.use_nodes=True;p=ma.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.12,.16,.065,1);p.inputs['Roughness'].default_value=.95
o=solid('R402_FORT_TOWER_LOW_COURT',lambda x,y:z(x,y)-.12,z,ma);o['level_id']='SITE';o['source']='Independent plane R399; R336 traced courtyard boundary; Zinneke rooftop view 1 confirms low grass court.';o['accepted']=False
out=R/'scenes/MUDAM_R402_KALE_ALCAK_KULE_AVLUSU_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in ['R402_FORT_TOWER_LOW_COURT','R154_FORT_MASONRY_BODY']:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
report=dict(scene=out.name,accepted=False,published=False,sourcePixels=pixels,planeCheck=control,meshChecks=checks,inheritedOpenBodyEdges=baseline_boundary,clipped=records,limits=['Court boundary visually traced; edge uncertainty not surveyed. Tower-end shoulder and stairs still incomplete.', 'Inherited masonry body has an intentionally removed top cap (70 boundary edges); separate roof closes the assembly. No new body boundary edges introduced, not claimed as a watertight single mesh.']);(R/'reports/R402_LOW_COURT.json').write_text(json.dumps(report,indent=2));assert checks[0]['nonManifold']==0 and checks[0]['zeroArea']==0 and checks[1]['nonManifold']<=baseline_boundary and checks[1]['zeroArea']==0,checks
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-42,-34,100));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-42,-34,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=65;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R402_fort_roof_candidate.png');bpy.ops.render.render(write_still=True);print('R402_READY')
