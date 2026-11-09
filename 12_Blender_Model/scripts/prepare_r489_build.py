from pathlib import Path
R=Path('12_Blender_Model');s=(R/'scripts/build_r487_passage.py').read_text();clip=s[s.index('def clip('):s.index("c=D['coefficients']")]
header='''import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R488_AVLU_SUR_MALZEME_BAGLANTI_ADAY_v001.blend'));D=json.loads((R/'reports/R489_DARK_INSET_PLANE.json').read_text());poly=D['outline'];tris=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]]);regions=[[poly[i] if isinstance(i,int) else (i.x,i.y) for i in f] for f in tris];records=[]
'''
tail='''
def solid(name,xy,zfn,depth,mat):
 n=len(xy);vs=[(x,y,zfn(x,y)+dz) for dz in [0,-depth] for x,y in xy];fs=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);ob['level_id']='SITE';me.materials.append(mat);return ob
c=D['coefficients'];height=lambda x,y:c[0]*x+c[1]*y+c[2];mat=bpy.data.materials.new('R489_SOURCE_DARK_INSET');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.035,.065,.075,1);bs.inputs['Roughness'].default_value=.36
# Independent flat inset; unknown function is explicitly retained in metadata.
ob=solid('R489_NW_DARK_HORIZONTAL_INSET',poly,height,.2,mat);ob['source']=D['interpretation'];ob['heightFitHeldoutMaxM']=D['max'];ob['heightFitHeldoutRmsM']=D['rms']
# Cut inherited court only where the visible inset occupies its footprint.
cutter=solid('TEMP_INSET_CUT',poly,lambda x,y:10,22,mat);body=bpy.data.objects['R457_NORTH_LOADING_COURT'];bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('DarkInsetOpening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
stone=bpy.data.objects['R457_NORTH_LOADING_COURT'].data.materials[0];names=[ob.name]
for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
 a=Vector(a);b=Vector(b);direction=(b-a).normalized();normal=Vector((-direction.y,direction.x))*.07;xy=[a-normal,b-normal,b+normal,a+normal];o=solid('R489_INSET_STONE_BORDER_%d'%i,xy,lambda x,y:height(x,y)+.035,.4,stone);o['source']='Visible inset stone perimeter; 0.14m width visual estimate, not surveyed.';names.append(o.name)
checks={}
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks[name]={'nonManifold':sum(not e.is_manifold for e in bm.edges),'zeroArea':sum(f.calc_area()<1e-10 for f in bm.faces)};bm.free();assert not any(checks[name].values())
out=R/'scenes/MUDAM_R489_AVLU_KOYU_YATAY_BANT_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R489_BUILD.json').write_text(json.dumps(dict(checks=checks,cuts=records,reopened=True,accepted=False,published=False,uncertainty=D['interpretation']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-80,0,35));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-48,37,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=43;s.render.filepath=str(R/'renders/qa/R489_northwest_oblique.png');bpy.ops.render.render(write_still=True)
'''
(R/'scripts/build_r489_inset.py').write_text(header+clip+tail)
