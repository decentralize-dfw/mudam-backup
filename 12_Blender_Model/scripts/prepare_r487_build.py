from pathlib import Path
import json,sys
R=Path('12_Blender_Model');sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon,box
from shapely.ops import triangulate
D=json.loads((R/'reports/R487_PASSAGE_PLANE.json').read_text());src=json.loads((R/'reports/R487_LOWER_PASSAGE_GRADE.json').read_text());p=Polygon(src['outline']).intersection(Polygon([(-56.6,12),(-37.6,31),(-27,31),(-46,12)]));D['outline']=list(p.exterior.coords)[:-1];vs=[];fs=[];ids={}
for lo,hi in zip([0]+D['knots'],D['knots']+[60]):
 part=p.intersection(box(-80,lo,0,hi))
 for t in triangulate(part):
  if not part.covers(t.representative_point()):continue
  f=[]
  for xy in list(t.exterior.coords)[:3]:
   key=tuple(round(c,8) for c in xy)
   if key not in ids:ids[key]=len(vs);vs.append(key)
   f.append(ids[key])
  fs.append(f)
D.update(vertices=vs,faces=fs);(R/'reports/R487_PASSAGE_PLANE.json').write_text(json.dumps(D,indent=2))
base=(R/'scripts/build_r482_court_path_v002.py').read_text();clip=base[base.index('def clip('):base.index('# Remove inherited court slab')]
header='''import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from collections import Counter
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R486_AVLU_DUSEY_BAGLANTI_ADAY_v002.blend'));D=json.loads((R/'reports/R487_PASSAGE_PLANE.json').read_text());poly=D['outline'];tris=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]]);regions=[[poly[i] if isinstance(i,int) else (i.x,i.y) for i in f] for f in tris];records=[]
'''
tail='''
c=D['coefficients'];knots=D['knots']
def height(x,y):return c[0]+c[1]*(x+45)+c[2]*(y-24)+sum(c[i+3]*max(0,y-k) for i,k in enumerate(knots))
N=len(D['vertices']);vs=[(x,y,height(x,y)+dz) for dz in [0,-.3] for x,y in D['vertices']];fs=[tuple(f) for f in D['faces']]+[tuple(i+N for i in reversed(f)) for f in D['faces']];edges=Counter(tuple(sorted((a,b))) for f in D['faces'] for a,b in zip(f,f[1:]+f[:1]))
for (a,b),n in edges.items():
 if n==1:fs.append((a,b,b+N,a+N))
me=bpy.data.meshes.new('R487_NW_MINERAL_PASSAGE');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.to_mesh(me);bm.free();assert not any(check.values()),check;o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);o['level_id']='SITE';o['source']='Independent three-plane ground/ramp; 89 withheld ground cells RMS0.0419m, max0.2279m. Perimeter visual trace; whole region not accepted.';me.materials.append(bpy.data.objects['R457_NORTH_LOADING_COURT'].data.materials[0]);uv=me.uv_layers.new(name='UVMap')
for l in me.loops:
 v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x*.25,v.y*.25)
out=R/'scenes/MUDAM_R487_KUZEYBATI_ALT_GECIT_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R487_BUILD.json').write_text(json.dumps(dict(check=check,cuts=records,accepted=False,published=False),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-80,0,35));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-48,37,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=43;s.render.filepath=str(R/'renders/qa/R487_northwest_oblique.png');bpy.ops.render.render(write_still=True)
'''
(R/'scripts/build_r487_passage.py').write_text(header+clip+tail)
