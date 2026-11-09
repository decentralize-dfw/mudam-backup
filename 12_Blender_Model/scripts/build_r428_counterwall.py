import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R425_KULE_FOTOGRAF_TEPelikleri_ADAY_v001.blend'));d=json.loads((R/'reports/R428_FRONT_COUNTERWALL_LEVELS.json').read_text());assert d['valid'];changes=[];baseline={}
for name in sorted(set(x['name'] for x in d['rows'])):
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);baseline[name]=sum(not e.is_manifold for e in bm.edges);bm.free()
for row in d['rows']:
 o=bpy.data.objects[row['name']];inv=o.matrix_world.inverted()
 for i in row['indices']:
  v=o.data.vertices[i];p=o.matrix_world@v.co;before=p.z;p.z=row['proposedCrest'];v.co=inv@p;changes.append(dict(name=o.name,index=i,old=before,new=p.z))
for name in baseline:
 o=bpy.data.objects[name];o.data.update();o['R428_crest_source']='ACT classified returns R428 30 held-out cells RMS 0.02618m max0.07634m; existing independently modeled plan unchanged.'
out=R/'scenes/MUDAM_R428_ON_HENDEK_DIS_DUVAR_KOTLARI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in baseline:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),baselineNonManifold=baseline[name],zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(x['nonManifold']==x['baselineNonManifold'] and x['zeroArea']==0 for x in checks)
(R/'reports/R428_COUNTERWALL_BUILD.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changes=changes,checks=checks,heldout=d['check'],scope='Front counterwall top heights only; plan, bottoms, bridge gap and museum unchanged.',limits=d['limits']),indent=2));print('R428_SAVED',len(changes),flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
for label,eye,target,lens in [('front',(-107,-92,6),(-63,-54,1.7),50),('moat',(-97,-65,-2),(-76,-49,-8),38)]:
 bpy.ops.object.camera_add(location=eye);s.camera=bpy.context.object;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;s.render.filepath=str(R/f'renders/qa/R428_{label}_candidate.png');bpy.ops.render.render(write_still=True)
