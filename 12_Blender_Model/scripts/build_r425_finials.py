import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R424_UC_KULE_FOTOGRAF_CEPHELERI_ADAY_v001.blend'));raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());fits=json.loads((R/'reports/R418_TOWER_CAP_PLANES.json').read_text());gold=bpy.data.materials.new('R425_WEATHERED_GILT_BRONZE');gold.use_nodes=True;p=gold.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.40,.275,.075,1);p.inputs['Metallic'].default_value=.78;p.inputs['Roughness'].default_value=.42;names=[];records=[]
for t in raw['towers']:
 label=t['name'];cx,cy=t['center'];a,b=fits[label]['coef'];base=a+b*.23-.015;width,height={'WEST':(.24,1.15),'SOUTH':(.28,1.35),'CENTRE':(.20,1.15)}[label];old=bpy.data.objects['R154_ACORN_'+label];old.hide_render=True;old.hide_viewport=True;old.hide_set(True)
 # Rotational architectural profile. Stem, cup lip and rounded elongated nut.
 profile=[(.245,0),(.245,.025),(.13,.065),(.095,.10),(.095,.18),(.14,.20),(width*.78,.24),(width,.32),(width,.40),(width*.94,.43),(width*.96,.57),(width*.95,.72),(width*.89,.84),(width*.74,.94),(width*.50,1.015),(width*.22,1.055),(.008,1.07)]
 n=96;vs=[(cx+rr*math.cos(i*math.tau/n),cy+rr*math.sin(i*math.tau/n),base+z*height/1.07) for rr,z in profile for i in range(n)];fs=[list(range(n-1,-1,-1)),list(range((len(profile)-1)*n,len(profile)*n))]
 for j in range(len(profile)-1):
  for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 name='R425_'+label+'_ACORN_FINIAL';me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(gold);o['level_id']='SITE';o['source']='Independent turned silhouette proportioned from R423 original photographs; dimensions visual estimates using known tower radius, not survey.'
 for f in me.polygons:f.use_smooth=len(f.vertices)==4
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();names.append(name);records.append(dict(tower=label,base=base,heightEstimate=height,radiusEstimate=width))
out=R/'scenes/MUDAM_R425_KULE_FOTOGRAF_TEPelikleri_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert all(not x['nonManifold'] and not x['zeroArea'] for x in checks)
(R/'reports/R425_FINIALS.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,records=records,checks=checks,limits=['Photo-proportioned silhouette, not exact decoration or surveyed dimensions. Ring remains incomplete.']),indent=2));print('R425_SAVED',flush=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-107,-92,6));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-63,-54,1.7))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=50;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R425_front_candidate.png');bpy.ops.render.render(write_still=True)
