import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R460_KUZEY_AVLU_GECIS_ADAY_v001.blend'));d=json.loads((R/'reports/R462_NW_GLAZING_PLANE.json').read_text());assert d['valid'];poly=d['outline'];a,b,c=d['plane'];created=[]
def material(n,col,metal=0,rough=.5):
 m=bpy.data.materials.new(n);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
glass=material('R463_NW_COURT_GLASS',(.065,.13,.14),.35,.16);metal=material('R463_NW_COURT_FRAME',(.12,.15,.145),.7,.36);stone=material('R463_NW_COURT_BORDER',(.40,.39,.34),0,.8)
def mesh(n,vs,fs,ma):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(n,me);bpy.context.scene.collection.objects.link(ob)
 if ma:me.materials.append(ma);created.append(n);ob['level_id']='SITE';ob['source']='Independent source-outline courtyard glazing; R462 classified analytical plane, no scan faces or photo texture.'
 return ob
def prism(n,outline,top,bottom,ma):
 vs=[(x,y,fn(x,y)) for fn in [top,bottom] for x,y in outline];N=len(outline);fs=[tuple(range(N)),tuple(reversed(range(N,2*N)))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];return mesh(n,vs,fs,ma)
def level(x,y):return a*x+b*y+c
cut=prism('R463_TEMP_CUT',poly,lambda x,y:1,lambda x,y:-12,None);body=bpy.data.objects['R457_NORTH_LOADING_COURT'];bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('SourceVisibleGlazingOpening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
prism('R463_NW_COURT_GLAZING',poly,level,lambda x,y:level(x,y)-.08,glass)
def bar(n,P,Q,width,height,ma,offset):
 P=Vector(P);Q=Vector(Q);u=(Q-P).normalized();v=Vector((-u.y,u.x))*width/2;out=[P+v,Q+v,Q-v,P-v];return prism(n,out,lambda x,y:level(x,y)+offset,lambda x,y:level(x,y)+offset-height,ma)
for i in range(4):bar('R463_NW_COURT_BORDER_'+str(i),poly[i],poly[(i+1)%4],.16,.23,stone,.10)
P=[Vector(v) for v in poly]
# Grid counts are a photo-scale candidate, not a measured fabrication schedule.
for i in range(1,7):
 t=i/7;bar('R463_NW_COURT_MULLION_A_'+str(i),P[0].lerp(P[1],t),P[3].lerp(P[2],t),.045,.065,metal,.025)
for i in range(1,8):
 t=i/8;bar('R463_NW_COURT_MULLION_B_'+str(i),P[0].lerp(P[3],t),P[1].lerp(P[2],t),.045,.065,metal,.025)
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00005);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()
out=R/'scenes/MUDAM_R463_KUZEYBATI_AVLU_CAM_DUZLEMI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for n in ['R457_NORTH_LOADING_COURT']+created:
 o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);checks.append(dict(name=n,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
(R/'reports/R463_COURT_GLAZING_BUILD.json').write_text(json.dumps(dict(scene=out.name,checks=checks,source=d['check'],accepted=False,published=False,limits=['Source image determines visible main glazing outline. Adjacent narrow glazed strip remains pending.','Frame grid counts and section sizes are photographic candidates; hidden interior is not modeled.','Whole museum-ring grade and roof-edge verification incomplete.']),indent=2));assert not any(q['nonManifold'] or q['zeroArea'] for q in checks),checks
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-48,37,90));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-48,37,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=35;s.render.filepath=str(R/'renders/qa/R463_northwest_glazing.png');bpy.ops.render.render(write_still=True)

