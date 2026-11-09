from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r154';terrain=json.loads((D/'terrain.json').read_text());fort=json.loads((D/'fort.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R153_PHILHARMONIE_CEVRE_v002.blend'))
s=bpy.context.scene;col=bpy.data.collections.new('R154_TERRAIN_AND_FORT');s.collection.children.link(col)
def pbr(name,base,normal,rough=None,strength=.4):
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.88
 for kind,file in [('Base Color',base),('Normal',normal),('Roughness',rough)]:
  if not file:continue
  tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures'/file),check_existing=True);tex.extension='REPEAT'
  if kind!='Base Color':tex.image.colorspace_settings.name='Non-Color'
  if kind=='Normal':n=nt.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=strength;nt.links.new(tex.outputs['Color'],n.inputs['Color']);nt.links.new(n.outputs['Normal'],p.inputs['Normal'])
  else:nt.links.new(tex.outputs['Color'],p.inputs[kind])
 return m
grass=pbr('R154_TURF_PBR','R129_moat_turf_basecolor.png','R129_moat_turf_normal.png','R129_moat_turf_roughness.png',.10)
stone=pbr('R154_FORT_STONE_PBR','R129_historic_masonry_basecolor.png','R129_historic_masonry_normal.png','R129_historic_masonry_roughness.png',.55)
paving=pbr('R154_PATH_PBR','R59_paving_candidate_basecolor.png','R59_paving_candidate_normal.png',strength=.3)
asphalt=pbr('R154_ROAD_PBR','R154_asphalt_basecolor.png','R154_asphalt_normal.png',strength=.22)
def plain(name,color,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.65;p.inputs['Metallic'].default_value=metal;return m
zinc=plain('R154_FORT_ZINC',(.30,.34,.36),.6);dark=plain('R154_RECESSED_OPENINGS',(.025,.035,.035));frame=plain('R154_CUT_STONE_DRESSINGS',(.52,.48,.37));earth=pbr('R154_FORT_EARTH_ROOF','R129_moat_turf_basecolor.png','R129_moat_turf_normal.png','R129_moat_turf_roughness.png',.4)
def uv(o,scale=4,horizontal=False):
 me=o.data
 for l in list(me.uv_layers):me.uv_layers.remove(l)
 layer=me.uv_layers.new(name='UVMap')
 for f in me.polygons:
  normal=f.normal;u=Vector((0,0,1)).cross(normal).normalized() if abs(normal.z)<.7 else Vector((1,0,0));v=normal.cross(u).normalized()
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(q.x/scale,q.y/scale) if horizontal else (q.dot(u)/scale,q.dot(v)/scale)
def mesh(name,vs,fs,material,smooth=False):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(material);o['level_id']='SITE';o['source']='ACT LiDAR2024 / ACT2020 / OSM';uv(o)
 if smooth:
  for f in me.polygons:f.use_smooth=True
 return o
# Smooth elevations away from locked building and historic-wall contact zones.
for row in terrain['updates']:
 o=s.objects[row['name']]
 assert len(o.data.vertices)==len(row['vertices'])
 for v,q in zip(o.data.vertices,row['vertices']):v.co=q
 o.data.update();o.data.materials.clear();o.data.materials.append(grass if row['name']=='R152_CLASS2_TERRAIN' else paving);uv(o,6,True)
 for f in o.data.polygons:f.use_smooth=True
for row in terrain['meshes']:
 o=mesh(row['name'],row['vertices'],row['faces'],grass if row['material']=='grass' else asphalt,True);uv(o,6,True)
for o in list(s.objects):
 if o.name.startswith('R152_FORT_'):bpy.data.objects.remove(o,do_unlink=True)
# Closed fort mass is used for true recessed portals, then its hidden flat cap
# is removed in favour of the separate source-sampled earth roof.
xy=fort['footprint'];n=len(xy);vs=[(x,y,z) for (x,y),z in zip(xy,fort['bases'])]+[(x,y,fort['body_top']) for x,y in xy];fs=[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
for t in fort['cap_triangles']:
 for z,reverse in [(fort['body_top'],False),(min(fort['bases']),True)]:
  start=len(vs);vs.extend([(x,y,z) for x,y in t]);fs.append(list(range(start,start+3))[::(-1 if reverse else 1)])
# Use a consistent flat buried base for a watertight Boolean operand.
for i in range(n):vs[i]=(vs[i][0],vs[i][1],min(fort['bases']))
body=mesh('R154_FORT_MASONRY_BODY',vs,fs,stone)
entry=Vector((*fort['entry'],0));direction=Vector((*fort['direction'],0));tangent=Vector((*fort['tangent'],0));deck=fort['deck_z']
def arch(name,center,bottom,width,straight,depth,material):
 r=width/2;shape=[(-r,0),(r,0)]+[(r*math.cos(a),straight+r*math.sin(a)) for a in [math.pi*i/20 for i in range(21)]];vs=[]
 for d in depth:
  for x,z in shape:vs.append(tuple(center+tangent*x+direction*d+Vector((0,0,bottom+z))))
 n=len(shape);fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)];return mesh(name,vs,fs,material)
def subtract(target,cutter):
 bpy.context.view_layer.objects.active=target;mod=target.modifiers.new('Source opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
for label,center,bottom,width,straight in [('ENTRANCE',entry,deck-.04,2.3,2.25),('FRONT_WINDOW',entry+tangent*5.0,deck+.8,1.55,1.55)]:
 subtract(body,arch('CUT_'+label,center,bottom,width,straight,[-1.4,2.1],dark));arch('R154_'+label+'_RECESSED',center,bottom,width*.93,straight,[1.8,1.84],dark)
 # Stone voussoirs and jambs frame the real opening rather than a flat decal.
 r=width/2
 for j in range(12):
  a=math.pi*j/12;b=math.pi*(j+1)/12;pts=[(r*math.cos(a),straight+r*math.sin(a)),(r*math.cos(b),straight+r*math.sin(b)),((r+.24)*math.cos(b),straight+(r+.24)*math.sin(b)),((r+.24)*math.cos(a),straight+(r+.24)*math.sin(a))];verts=[tuple(center+tangent*x+direction*d+Vector((0,0,bottom+z))) for d in (-.18,.15) for x,z in pts];mesh('R154_'+label+'_ARCH_%02d'%j,verts,[[0,1,2,3],[7,6,5,4]]+[[k,(k+1)%4,(k+1)%4+4,k+4] for k in range(4)],frame)
 for side in (-1,1):
  a=side*r;b=side*(r+.24);verts=[tuple(center+tangent*x+direction*d+Vector((0,0,z))) for d in (-.18,.15) for x,z in [(a,bottom),(b,bottom),(b,bottom+straight),(a,bottom+straight)]];mesh('R154_'+label+'_JAMB_'+str(side),verts,[[0,1,2,3],[7,6,5,4]]+[[k,(k+1)%4,(k+1)%4+4,k+4] for k in range(4)],frame)
uv(body)
for face in body.data.polygons:
 center=face.center
 if abs(face.normal.z)<.7 and any(math.hypot(center.x-t['center'][0],center.y-t['center'][1])<5.8 for t in fort['towers'] if t['name']!='CENTRE'):face.use_smooth=True
# Remove the coplanar hidden top; the roof is an independently reconstructed surface.
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if all(abs(v.co.z-fort['body_top'])<1e-5 for v in f.verts)],context='FACES');bm.to_mesh(body.data);bm.free()
for q in fort['roof_vertices']:
 distance=min(math.hypot(q[0]-t['center'][0],q[1]-t['center'][1])-t['radius'] for t in fort['towers']);blend=max(0,min(1,(distance-1.5)/2));blend=blend*blend*(3-2*blend);q[2]=2.9*(1-blend)+q[2]*blend
mesh('R154_FORT_ROUNDED_EARTH_ROOF',fort['roof_vertices'],fort['roof_faces'],earth,True)
tris=fort['metal_triangles'];mesh('R154_FORT_METAL_ROOF',[(x,y,3.08) for t in tris for x,y in t],[list(range(i,i+3)) for i in range(0,3*len(tris),3)],zinc)
# Narrow raised border follows the actual inset roof outline.
path=fort['metal_outline'];n=len(path);mesh('R154_FORT_METAL_UPSTAND',[(x,y,z) for z in (3.06,3.34) for x,y in path],[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],zinc)
def ring(name,c,rings,material):
 n=64;vs=[(c[0]+r*math.cos(math.tau*i/n),c[1]+r*math.sin(math.tau*i/n),z) for r,z in rings for i in range(n)];fs=[]
 for k in range(len(rings)-1):fs.extend([[k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i] for i in range(n)])
 fs.extend([list(range(n-1,-1,-1)),list(range((len(rings)-1)*n,len(rings)*n))]);return mesh(name,vs,fs,material,True)
for t in fort['towers']:
 r=t['radius'];z=t['roof'];lo=2.75 if t['name']!='CENTRE' else 2.2
 ring('R154_TOWER_LOWER_COPING_'+t['name'],t['center'],[(r+.65,2.78),(r+.65,2.95),(r-.2,2.95)],stone)
 tower=ring('R154_TOWER_'+t['name'],t['center'],[(r+.25,lo),(r+.18,lo+.25),(r-.18,lo+.65),(r-.18,z-.6),(r+.08,z-.4),(r+.17,z-.25),(r+.17,z)],stone)
 ring('R154_TOWER_CAP_'+t['name'],t['center'],[(r+.2,z),(r*.84,z+.12),(.23,z+.26)],zinc)
 ring('R154_ACORN_'+t['name'],t['center'],[(.2,z+.26),(.3,z+.43),(.35,z+.58),(.25,z+.85),(.10,z+1.02),(.01,z+1.12)],frame)
 angle=math.atan2(-direction.y,-direction.x)
 for j in (-1,0,1):
  a=angle+j*.44;out=Vector((math.cos(a),math.sin(a),0));loc=Vector((*t['center'],z-1.1))+out*(r-.25);bpy.ops.mesh.primitive_cube_add(size=1,location=loc);c=bpy.context.object;c.dimensions=(.32,1.3,.85);c.rotation_euler.z=a-math.pi/2;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);subtract(tower,c)
 uv(tower)
# Source-traced bridge now terminates at the reconstructed entrance.
a=Vector((*fort['deck_start'],deck));b=Vector((*fort['deck_end'],deck));side=Vector((-direction.y,direction.x,0));corners=[a+side*1.2,b+side*1.2,b-side*1.2,a-side*1.2];vs=[tuple(p-Vector((0,0,.3))) for p in corners]+[tuple(p) for p in corners];mesh('R154_FORT_ENTRANCE_BRIDGE',vs,[[0,3,2,1],[4,5,6,7]]+[[i,(i+1)%4,(i+1)%4+4,i+4] for i in range(4)],paving)
# Export grouped layers; no rejected canopy proxies are reintroduced.
for o in s.objects:
 if o.name.startswith('R152_TREE_'):raise RuntimeError('Rejected trees present')
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.view_settings.exposure=-.9
cam=s.camera
for label,eye,target in [('fort',(-140,-135,32),(-48,-40,-2)),('near',(150,-210,155),(0,-5,-2)),('far',(750,-820,750),(60,80,-5))]:
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48;s.render.filepath=str(R/f'renders/qa/R154_{label}.png');bpy.ops.render.render(write_still=True)
out=R/'scenes/MUDAM_R154_GENIS_ARAZI_KALE_v003.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
exp=R/'exports/r152_clean'
for file,choose in [('near_site',lambda o:o.name.startswith(('R152_','R154_')) or o.get('level_id')=='L00_APPROACH'),('philharmonie',lambda o:o.name.startswith('R153_'))]:
 bpy.ops.object.select_all(action='DESELECT')
 for o in s.objects:
  if o.type=='MESH' and not o.hide_render and choose(o):o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(exp/(file+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
report=dict(scene=str(out),terrain_extent=terrain['extent'],terrain_updates=[{k:v for k,v in x.items() if k!='vertices'} for x in terrain['updates']],new_objects=len(col.objects),normal_mapped_materials=[m.name for m in (grass,stone,paving,asphalt,earth)],limits=terrain['limits']+fort['limits'],accepted=False)
(R/'reports/R154_BUILD.json').write_text(json.dumps(report,indent=2));print('R154_SAVED',len(col.objects),flush=True)
