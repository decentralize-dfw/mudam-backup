from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];data=json.loads((R/'.local_source_cache/r152/philharmonie_clean.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R152_TEMIZ_YAKIN_CEVRE_v009.blend'))
s=bpy.context.scene;col=bpy.data.collections.new('R153_PHILHARMONIE_CLEAN');s.collection.children.link(col)
def mat(name,c,rough=.6,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
white=mat('R153_WHITE_COLUMNS',(.77,.78,.76));roofmat=mat('R153_LIGHT_METAL_ROOF',(.64,.69,.70),.42,.45);glass=mat('R153_BLUE_GREY_GLAZING',(.08,.17,.20),.18,.5);coremat=mat('R153_AUDITORIUM_CORE',(.36,.32,.28));paving=mat('R153_PAVING',(.47,.46,.43),.85)
def mesh(name,vs,fs,m,smooth=False):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(m);o['source']='Architect N3 plan + registered ACT2020 reference';o['status']='context_reconstruction_candidate';o['level_id']='SITE_PHILHARMONIE'
 if smooth:
  for f in me.polygons:f.use_smooth=True
 return o
z=data['roof_z'];base=data['base']
def cap(name,tris,height,m):
 vs=[(x,y,height) for t in tris for x,y in t];return mesh(name,vs,[list(range(i,i+3)) for i in range(0,len(vs),3)],m)
def wall(name,path,lo,hi,m):
 n=len(path);return mesh(name,[(x,y,h) for h in (lo,hi) for x,y in path],[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],m,True)
cap('R153_MAIN_ROOF',data['roof_triangles'],z,roofmat);cap('R153_SKYLIGHT',data['skylight_triangles'],z-.15,glass);cap('R153_CORE_ROOF',data['core_triangles'],z-.6,roofmat)
wall('R153_ROOF_FASCIA',data['roof'],z-.45,z,white)
# Cylinders are batched into a single mesh. Only detected plan marks are modeled.
vs=[];fs=[]
for x,y in data['columns']:
 o=len(vs);n=12;r=.1615
 vs.extend([(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),h) for h in (base-.15,z-.45) for i in range(n)])
 fs.extend([[o+i,o+(i+1)%n,o+(i+1)%n+n,o+i+n] for i in range(n)]);fs.extend([list(range(o+n-1,o-1,-1)),list(range(o+n,o+2*n))])
mesh('R153_COLUMNS_FROM_PLAN',vs,fs,white,True)
center=Vector((sum(x for x,y in data['roof'])/len(data['roof']),sum(y for x,y in data['roof'])/len(data['roof'])))
curtain=[tuple(center+(Vector(q)-center)*.89) for q in data['roof']]
wall('R153_INNER_GLAZED_ENVELOPE',curtain,base,z-.45,glass);wall('R153_AUDITORIUM_CORE',data['core'],base,z-.6,coremat)
# Roof lantern ribs follow the traced inner oval; peripheral bands are modeled.
vs=[];fs=[]
def beam(a,b,width=.07):
 a=Vector(a);b=Vector(b);delta=b-a;u=delta.normalized().cross(Vector((0,0,1)))
 if u.length<.01:u=Vector((1,0,0))
 u.normalize();v=delta.normalized().cross(u).normalized();off=len(vs)
 vs.extend([tuple(c+u*i*width/2+v*j*width/2) for c in (a,b) for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]])
 fs.extend([[off+i,off+(i+1)%4,off+(i+1)%4+4,off+i+4] for i in range(4)])
for i in range(0,len(data['skylight']),4):
 a=data['skylight'][i];b=data['core'][i];beam((*a,z+.03),(*b,z+.03),.10)
for frac in (0,.33,.66,1):
 ring=[(a[0]*(1-frac)+b[0]*frac,a[1]*(1-frac)+b[1]*frac,z+.03) for a,b in zip(data['skylight'],data['core'])]
 for a,b in zip(ring,ring[1:]+ring[:1]):beam(a,b,.08)
# Glazing mullions at sampled points; approximate visible context rhythm.
for a,b in zip(curtain,curtain[1:]+curtain[:1]):
 a=Vector(a);b=Vector(b);n=max(1,round((b-a).length/2))
 for j in range(n):
  p=a.lerp(b,j/n);beam((*p,base),(*p,z-.45),.065)
for h in (base+5,base+10,base+15):
 for a,b in zip(curtain,curtain[1:]+curtain[:1]):beam((*a,h),(*b,h),.07)
mesh('R153_GLAZING_FRAMES',vs,fs,white)
for petal in data['petals']:
 mesh('R153_SHELL_'+petal['name'],petal['vertices'],petal['faces'],white,True)
 border=petal['vertices'][-128:];vs=[(x,y,base-.2) for x,y,h in border]+border;n=len(border);mesh('R153_SHELL_EDGE_'+petal['name'],vs,[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)],white,True)
cap('R153_PLAZA_SOURCE_OUTLINE',data['plaza_triangles'],base-.04,paving)
wall('R153_PLAZA_RETAINING_EDGE',data['plaza'],7.5,base-.04,paving)
s['stage']='R153 Philharmonie context candidate, R152 grounding retained';s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
cam=s.camera
for label,eye,target in [('oblique',(310,55,110),(182,175,20)),('facade',(268,87,30),(180,175,20))]:
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48;s.render.filepath=str(R/f'renders/qa/R153_philharmonie_{label}.png');bpy.ops.render.render(write_still=True)
out=R/'scenes/MUDAM_R153_PHILHARMONIE_CEVRE_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/philharmonie.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
report=dict(scene=str(out),new_objects=len(col.objects),detected_columns=data['detected_columns'],limits=data['limits']+['738 detected columns; complete 823-column audit not claimed.','Inner curtain wall offset and frame rhythm are context approximations.','Plaza outline traced from ACT; flat top candidate, entrance stair profiles remain pending.'],accepted=False)
(R/'reports/R153_PHILHARMONIE_BUILD.json').write_text(json.dumps(report,indent=2));print('R153_SAVED',len(col.objects),flush=True)
