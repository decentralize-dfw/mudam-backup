import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R397_PAVYON_KESIT_KENAR_BAGLANTI_ADAY_v001.blend'));d=json.loads((R/'reports/R393_METAL_SEAMS_INPUT.json').read_text());vs=[];fs=[]
for row in d['seams']:
 a=Vector((*row['a'],0));b=Vector((*row['b'],0));direction=(b-a).normalized();side=Vector((-direction.y,direction.x,0))*.009;xy=[a-side,b-side,b+side,a+side];start=len(vs);c=row['plane']
 for dz in [.001,.018]:vs.extend([(p.x,p.y,c[0]*p.x+c[1]*p.y+c[2]+dz) for p in xy])
 fs.extend([[start+i for i in [0,3,2,1]],[start+i for i in [4,5,6,7]]]+[[start+i,start+(i+1)%4,start+(i+1)%4+4,start+i+4] for i in range(4)])
me=bpy.data.meshes.new('R398_FORT_STANDING_SEAMS');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);mat=bpy.data.materials['R154_FORT_ZINC'].copy();mat.name='R398_FORT_SEAM_ZINC';p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.22,.25,.27,1);p.inputs['Roughness'].default_value=.62;me.materials.append(mat);o['level_id']='SITE';o['source']=d['source'];o['spacingSurveyed']=False
out=R/'scenes/MUDAM_R398_KALE_CATI_VE_PAVYON_BAGLANTI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and ob.name.startswith(('R389_','R392_','R397_','R398_')):
  bm=bmesh.new();bm.from_mesh(ob.data);checks.append(dict(name=ob.name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(c['nonManifold'] or c['zeroArea'] for c in checks),checks
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
 if ob.type=='MESH' and not ob.hide_render and (ob.name.startswith(('R389_','R392_','R397_','R398_')) or ob.name in ['R154_FORT_MASONRY_BODY','R154_FORT_ROUNDED_EARTH_ROOF']):ob.select_set(True)
glb=R/'exports/r152_clean/r398_fort_pavilion_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False)
report=dict(scene=out.name,accepted=False,published=False,seamCount=len(d['seams']),meshChecks=checks,limits=['Metal seam spacing is visual estimate, not surveyed.','Tower-end earth cover remains inherited. Whole marked perimeter remains unaccepted.','Pavilion contact geometry closes artificial cuts without altering adjacent measured floor levels.']);(R/'reports/R398_ROOF_CONTACT.json').write_text(json.dumps(report,indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-42,-34,100));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-42,-34,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=65;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R398_fort_roof_candidate.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));errors=[]
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':
  bad=sum(not all(math.isfinite(x) for x in v.co) for v in ob.data.vertices);zero=sum(p.area<1e-10 for p in ob.data.polygons)
  if bad or zero:errors.append(dict(name=ob.name,nonFinite=bad,zeroArea=zero))
report['glbErrors']=errors;(R/'reports/R398_ROOF_CONTACT.json').write_text(json.dumps(report,indent=2));assert not errors;print('R398_READY',checks)
