from pathlib import Path
import bpy,json,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R211_BUTUN_BINA_KABUKLARI_v002.blend'));changes=[]
for row in json.loads((R/'config/r213_cut_replacements.json').read_text()):
 if not row['replacements']:continue
 o=bpy.data.objects[row['name']];old=o.data;old.calc_loop_triangles();repl={r['index']:r['triangles'] for r in row['replacements']};vs=[];fs=[];mi=[];smooth=[];uvs={u.name:[] for u in old.uv_layers}
 for t in old.loop_triangles:
  points=[o.matrix_world@old.vertices[i].co for i in t.vertices];a,b,c=points;det=(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)
  triangles=repl.get(t.index,[[p[:2] for p in points]])
  if t.index in repl and abs(det)<1e-10:raise RuntimeError('Vertical cut triangle')
  for tri in triangles:
   k=len(vs)
   for j,(x,y) in enumerate(tri):
    if t.index not in repl:w=[float(j==i) for i in range(3)]
    else:
     wb=((x-a.x)*(c.y-a.y)-(y-a.y)*(c.x-a.x))/det;wc=((b.x-a.x)*(y-a.y)-(b.y-a.y)*(x-a.x))/det;w=[1-wb-wc,wb,wc]
    vs.append((x,y,sum(w[i]*points[i].z for i in range(3))))
    for u in old.uv_layers:uvs[u.name].append(tuple(sum(w[i]*u.data[t.loops[i]].uv[k] for i in range(3)) for k in range(2)))
   fs.append((k,k+1,k+2));mi.append(t.material_index);smooth.append(old.polygons[t.polygon_index].use_smooth)
 me=bpy.data.meshes.new(o.name+'_R213');me.from_pydata(vs,[],fs);me.update()
 for m in old.materials:me.materials.append(m)
 for p,m,s in zip(me.polygons,mi,smooth):p.material_index=m;p.use_smooth=s
 for name,values in uvs.items():
  u=me.uv_layers.new(name=name)
  for l in me.loops:u.data[l.index].uv=values[l.vertex_index]
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001)
 for f in bm.faces:
  if f.normal.z<0:f.normal_flip()
 bm.to_mesh(me);bm.free();o.data=me;changes.append(dict(name=o.name,changed_triangles=len(repl)))
raw=json.loads((R/'.local_source_cache/r154/terrain.json').read_text());vs=[];fs=[]
for row in raw['meshes']:
 k=len(vs);vs.extend(row['vertices']);fs.extend([k+i for i in f] for f in row['faces'])
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True);records=[]
for row in json.loads((R/'config/r213_access_surfaces.json').read_text()):
 if row['name'].startswith('SOUTH_CONCRETE'):continue
 def height(x,y):
  ox,oy=row['origin']
  if row['name']!='UPPER_ENTRANCE':a,b,c=row['plane'];return a*(x-ox)+b*(y-oy)+c
  x=(x-ox)/20;y=(y-oy)/20;a,b,c,d,e,f=row['quadratic'];return a*x+b*y+c+d*x*x+e*x*y+f*y*y
 verts=[];faces=[]
 for tri in row['triangles']:
  k=len(verts);verts.extend((x,y,height(x,y)) for x,y in tri);faces.append((k,k+1,k+2))
 me=bpy.data.meshes.new('R213_'+row['name']);me.from_pydata(verts,[],faces);me.materials.append(bpy.data.materials['R157_MATTE_ASPHALT']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001)
 for f in bm.faces:
  if f.normal.z<0:f.normal_flip()
 bm.to_mesh(me);bm.free();me.update();uv=me.uv_layers.new(name='UVMap')
 for l in me.loops:v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x/6,v.y/6)
 o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
 # Join the independently designed road edge to the retained original terrain.
 bm=bmesh.new();bm.from_mesh(me);edgeverts=[];edgefaces=[]
 for e in bm.edges:
  if not e.is_boundary:continue
  a,b=[v.co.copy() for v in e.verts];ha=ground.ray_cast(Vector((a.x,a.y,100)),Vector((0,0,-1)),300)[0];hb=ground.ray_cast(Vector((b.x,b.y,100)),Vector((0,0,-1)),300)[0]
  if ha is None or hb is None:raise RuntimeError('Missing access boundary datum')
  if max(abs(ha.z-a.z),abs(hb.z-b.z))<.01:continue
  k=len(edgeverts);edgeverts.extend([tuple(a),tuple(b),(b.x,b.y,hb.z),(a.x,a.y,ha.z)]);edgefaces.append((k,k+1,k+2,k+3))
 bm.free();edge=bpy.data.meshes.new('R213_EDGE_'+row['name']);edge.from_pydata(edgeverts,[],edgefaces);edge.materials.append(bpy.data.materials['R176_PALE_MINERAL']);edge.update();eo=bpy.data.objects.new(edge.name,edge);bpy.context.collection.objects.link(eo)
 records.append(dict(name=o.name,area=row['area'],sourceSupport=row['quadratic_support'] if row['name']=='UPPER_ENTRANCE' else row['support'],sourceTolerance=.22))
s=bpy.context.scene;s.camera.location=(-10,415,250);s.camera.rotation_euler=(0,0,0);s.camera.data.ortho_scale=150;s.render.resolution_x=1500;s.render.resolution_y=1500;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R213_PALAIS_GIRIS_ZEMINLERI_v002.blend'),compress=True)
(R/'reports/R213_ACCESS_ARCHITECTURE.json').write_text(json.dumps(dict(accepted=False,terrainChanges=changes,surfaces=records,method='Independent traced road domains and fitted low-parameter grades; original source mesh not transferred',remaining=['Southern concrete terrace contains unresolved separate levels and is not fabricated','Edge retaining treatment provisional','Whole11region acceptance outstanding']),indent=2))
s.render.filepath=str(R/'renders/qa/R213_authored_access_v002.png');bpy.ops.render.render(write_still=True)
