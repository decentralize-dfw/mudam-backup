from pathlib import Path
import json,bpy,numpy as np
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];root=R.parent
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R173_SERT_ZEMINLER_v001.blend'))
terrain=[o for o in bpy.context.scene.objects if o.type=='MESH' and ('TERRAIN' in o.name.upper() or o.name in ['R154_FAR_GROUND','R154_FAR_ROADS'])]
vs=[];fs=[]
for o in terrain:
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
assert vs,'No terrain found'
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def ground(x,y):
 p,*_=bvh.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),500);return p.z if p else None
points=np.load(R/'.local_source_cache/r171/lower_reference.npz')['xyz']
ways=json.loads((root/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text())
exclude={o.name[5:] for o in bpy.context.scene.objects if o.name.startswith('R171_') and o.name[5:].isdigit()}
for p in (R/'config').glob('r*_building_targets.json'):
 for b in json.loads(p.read_text()).get('buildings',[]):exclude.add(str(b['id']))
col=bpy.data.collections.new('R174_LOWER_DISTRICT_FOOTPRINT_MASSES');bpy.context.scene.collection.children.link(col)
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;return m
wallmat=material('R171_SIMPLE_NEUTRAL_WALL',(.48,.46,.41));roofmat=material('R171_SIMPLE_NEUTRAL_ROOF',(.20,.22,.23))
records=[];skipped=[]
for w in ways:
 if 'building' not in w['tags'] or not w.get('xy') or str(w['id']) in exclude or w['tags'].get('location')=='underground':continue
 ring=np.array(w['xy'],dtype=float)-[293425,5499960];center=ring.mean(0)
 if not(-500<center[0]<600 and -550<center[1]<-230):continue
 if np.linalg.norm(ring[0]-ring[-1])<.001:ring=ring[:-1]
 if len(ring)<3:continue
 lo=ring.min(0);hi=ring.max(0);subset=points[(points[:,0]>=lo[0])&(points[:,0]<=hi[0])&(points[:,1]>=lo[1])&(points[:,1]<=hi[1])]
 inside=np.zeros(len(subset),dtype=bool)
 for a,b in zip(ring,np.roll(ring,-1,axis=0)):
  inside^=((a[1]>subset[:,1])!=(b[1]>subset[:,1]))&(subset[:,0]<(b[0]-a[0])*(subset[:,1]-a[1])/(b[1]-a[1]+1e-15)+a[0])
 sample=subset[inside];bases=[ground(*p) for p in ring]
 if any(v is None for v in bases) or len(sample)<12:skipped.append([w['id'],'insufficient roof or ground samples',len(sample)]);continue
 roof=float(np.quantile(sample[:,2],.85));base=min(bases)-.25
 if roof<max(bases)+2 or roof-base>35:skipped.append([w['id'],'ambiguous roof/terrain separation',roof-base]);continue
 n=len(ring);verts=[(x,y,base) for x,y in ring]+[(x,y,roof) for x,y in ring];faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 vectors=[Vector((x,y,0)) for x,y in ring]
 for tri in tessellate_polygon([vectors]):
  ix=[v if isinstance(v,int) else min(range(n),key=lambda j:(vectors[j]-v).length_squared) for v in tri];faces.extend([tuple(reversed(ix)),tuple(j+n for j in ix)])
 me=bpy.data.meshes.new('R174_'+str(w['id']));me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(me.name,me);col.objects.link(o);me.materials.append(wallmat);me.materials.append(roofmat)
 for face in me.polygons:
  if face.normal.z>.5:face.material_index=1
 o['source']='OSM footprint '+str(w['id'])+'; ACT roof scalar percentile85';o['scope']='User-authorized abstract mass; no facade detail or exact cadastral parcel claim';o['roof_estimate_samples']=len(sample)
 records.append(dict(id=w['id'],footprint=ring.tolist(),base=base,roof=roof,sourcePoints=len(sample),maxTerrain=max(bases),minTerrain=min(bases)))
scene=R/'scenes/MUDAM_R174_ALT_MAHALLE_EKLER_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene),compress=True)
for o in bpy.context.scene.objects:o.select_set(o.name.startswith('R174_'))
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r174_lower_district_REVIEW.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
(R/'reports/R174_LOWER_DISTRICT_v001.json').write_text(json.dumps(dict(accepted=False,buildings=records,skipped=skipped,limits=['OSM building footprints, not surveyed cadastral parcels','Roof elevations are scalar ACT estimates; trees may contaminate them','Flat abstract roofs explicitly requested for lower district','No hardscape or bridge completion claim','Review addition only, production unchanged']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.render.resolution_x=1400;s.render.resolution_y=900;s.render.resolution_percentage=100;target=Vector((-40,-350,-65));s.camera.location=target+Vector((230,-390,380));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=850;s.render.filepath=str(R/'renders/qa/R174_lower_district_v001.png');bpy.ops.render.render(write_still=True)
print('BUILDINGS',len(records),'SKIPPED',len(skipped))




