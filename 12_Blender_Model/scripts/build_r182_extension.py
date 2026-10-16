from pathlib import Path
import bpy,json,bmesh,numpy as np
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R181_KALE_TERASLARI_v003.blend'))
d=json.loads((R/'config/r182_extension_meshes.json').read_text());records=[]
for row in d['meshes']:
 me=bpy.data.meshes.new('R182_EXTENSION_'+row['name']);me.from_pydata(row['vertices'],[],row['faces']);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
 src=bpy.data.objects['R154_FAR_'+row['name']];me.materials.append(src.data.materials[0]);uv=me.uv_layers.new()
 for p in me.polygons:p.use_smooth=True
 for l in me.loops:v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x/8,v.y/8)
 records.append(dict(name=o.name,triangles=len(row['faces'])))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.name not in ['R154_FAR_GROUND','R154_FAR_ROADS','R182_EXTENSION_GROUND','R182_EXTENSION_ROADS']:continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles)
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True)
exclude=set()
for o in bpy.context.scene.objects:
 if o.name.startswith(('R171_','R174_')) and o.name[5:].isdigit():exclude.add(o.name[5:])
for p in (R/'config').glob('r*_building_targets.json'):
 for b in json.loads(p.read_text()).get('buildings',[]):exclude.add(str(b['id']))
ways=json.loads((R.parent/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text(encoding='utf8'));buildings=[];skipped=[]
wall=bpy.data.materials['R179_BACKGROUND_MINERAL'];roof=bpy.data.materials['R179_BACKGROUND_ROOF']
for w in ways:
 t=w['tags']
 if 'building' not in t or str(w['id']) in exclude or t.get('location')=='underground':continue
 ring=np.array(w['xy'])-[293425,5499960];center=ring.mean(0)
 if not(-600<center[0]<600 and -590<center[1]<-230):continue
 if np.linalg.norm(ring[0]-ring[-1])<1e-5:ring=ring[:-1]
 if len(ring)<3:continue
 bases=[]
 for x,y in ring:
  h,*_=ground.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),400)
  if h:bases.append(h.z)
 if len(bases)!=len(ring):skipped.append(w['id']);continue
 try:height=float(t['height'].replace('m',''));basis='OSM height'
 except:
  try:height=float(t['building:levels'])*3.2;basis='OSM levels x3.2m provisional'
  except:height=8;basis='User-authorized abstract mass; unmeasured neutral8m height'
 base=min(bases)-.2;top=max(bases)+height;n=len(ring);verts=[(x,y,base) for x,y in ring]+[(x,y,top) for x,y in ring];faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 tris=tessellate_polygon([[Vector((x,y,0)) for x,y in ring]])
 faces.extend(tuple(reversed(t)) for t in tris);faces.extend(tuple(i+n for i in t) for t in tris)
 me=bpy.data.meshes.new('R182_DISTRICT_'+str(w['id']));me.from_pydata(verts,[],faces);me.update();me.materials.append(wall);me.materials.append(roof)
 for f in me.polygons:
  if f.normal.z>.5:f.material_index=1
 o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);o['source']='OSM footprint '+str(w['id']);o['height_basis']=basis
 buildings.append(dict(id=w['id'],height=height,height_basis=basis,base=base,top=top))
(R/'reports/R182_EXTENSION_v001.json').write_text(json.dumps(dict(accepted=False,terrain=records,buildings=buildings,skipped=skipped,limits=d['limits']+['8m unknown-height masses are abstract, never surveyed-height acceptance','Terrain boundary seam and district source visual review pending']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R182_GENIS_ARAZI_MAHALLE_v001.blend'),compress=True)
s=bpy.context.scene;t=Vector((20,-350,-55));s.camera.location=t+Vector((200,-450,400));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=1100;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R182_district_extension_v001.png');bpy.ops.render.render(write_still=True)
print('R182_DONE',len(buildings),len(skipped))
