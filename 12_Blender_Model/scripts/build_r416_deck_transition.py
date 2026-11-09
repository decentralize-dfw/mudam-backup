import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R415_DOGU_HENDEK_DEVAMI_ADAY_v001.blend'));d=json.loads((R/'reports/R387_ROOF_INPUT.json').read_text());roof=d['roofOutline'];crest=d['crestOutline'];c=d['lowerPlane'];low=lambda p:c[0]*p[0]+c[1]*p[1]+c[2];edge=[]
for a,b in zip(roof,crest):
 v=Vector(b)-Vector(a);edge.append(tuple(Vector(a)+v.normalized()*min(.34,v.length*.5)))
old=bpy.data.objects['R389_FORT_PERIMETER_LEDGE'];old.hide_render=True;old.hide_viewport=True;old.hide_set(True)
names=[]
def parts(name,inner,outer,zi,zo,thickness,material):
 vs=[];fs=[]
 for i in range(1,len(inner)):
  j=(i+1)%len(inner);k=len(vs);top=[(*inner[i],zi(inner[i])),(*inner[j],zi(inner[j])),(*outer[j],zo(outer[j])),(*outer[i],zo(outer[i]))];vs+=top+[(x,y,z-thickness) for x,y,z in top];fs += [tuple(k+t for t in face) for face in [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials[material]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
 for l in me.loops:
  v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x-v.y)/4.24264,(v.x+v.y)/1.64049)
 o['level_id']='SITE';o['source']='Zinneke rooftop view 2: sloping zinc riser between lower timber deck and upper perimeter timber ledge. Levels from R386; 0.34m horizontal riser projection visually estimated.';names.append(name)
parts('R416_FORT_TIMBER_PERIMETER_LEDGE',edge,crest,lambda p:2.21,lambda p:2.21,.16,'R400_WEATHERED_TIMBER_DECK')
parts('R416_FORT_SLOPED_DECK_RISER',roof,edge,lambda p:low(p)+.008,lambda p:2.218,.025,'R400_ZINC_SLOPING_FASCIA')
out=R/'scenes/MUDAM_R416_KALE_TERAS_KADEME_GECISI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for n in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[n].data);checks.append(dict(name=n,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(v['nonManifold'] or v['zeroArea'] for v in checks)
(R/'reports/R416_DECK_TRANSITION.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,checks=checks,source='references/fort_inpa/rooftop_view_2_Zinneke_CC_BY_SA_3.jpg',limits=['Riser projection visually estimated, not surveyed. Whole ring incomplete.']),indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-46,-37,5.4));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-61.6,-53.15,3.1))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=35;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R416_roof_eye.png');bpy.ops.render.render(write_still=True)
