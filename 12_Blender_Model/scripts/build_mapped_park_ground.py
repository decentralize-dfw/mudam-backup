"""Replace paving only within archived woodland boundary, preserve existing route corridors."""
from pathlib import Path
import bpy,bmesh,json,sys,hashlib,xml.etree.ElementTree as ET
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;P=json.loads((B/'config/park_landings.json').read_text());osm=R/P['osm_file'];assert hashlib.sha256(osm.read_bytes()).hexdigest()==P['osm_sha256']
ways=json.loads((R/'10_Olcekli_Plan_ve_Fotograf_Analizi/kaynak_veri/osm_ways_utm.json').read_text());w=next(w for w in ways if w['id']=='759811369');xml=next(w for w in ET.parse(osm).getroot().findall('way') if w.attrib['id']=='759811369');assert {t.attrib['k']:t.attrib['v'] for t in xml.findall('tag')}==w['tags'];assert w['tags']['natural']=='wood' and w['tags']['leaf_type']=='mixed'
base=json.loads((B/'reports/R131_build_report.json').read_text())['file'];out=B/'scenes/MUDAM_R132_HARITALI_PARK_ZEMIN_AYRIMI_v003.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/base));ground=bpy.data.objects['R38_PARK_APPROACH_GROUND'];collection=ground.users_collection[0];insert=ground.copy();insert.data=ground.data.copy();insert.name='R132_MAPPED_WOODLAND_GROUND';collection.objects.link(insert)
def prism(name,poly,z0=-1,z1=1):
 poly=[tuple(p) for p in poly];poly=poly[:-1] if poly[0]==poly[-1] else poly;n=len(poly);me=bpy.data.meshes.new(name);me.from_pydata([(x,y,z) for z in [z0,z1] for x,y in poly],[],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);collection.objects.link(o);return o
def boolean(o,cut,operation):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('R132_SPLIT','BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name)
poly=[(p[0]-293425,p[1]-5499960) for p in w['xy']];cut=prism('R132_BOUNDARY_TEMP',poly);boolean(insert,cut,'INTERSECT');bpy.data.objects.remove(cut,do_unlink=True)
routes=[P['path_centerline']]+[[(p[0]-293425,p[1]-5499960) for p in q['xy']] for q in ways if q['id'] in ['49910981','50643005']]
for route in routes:
 for a,b in zip(route,route[1:]):
  a,b=Vector(a),Vector(b);d=(b-a).normalized();n=Vector((-d.y,d.x))*P['path_width_m']/2;cut=prism('R132_ROUTE_TEMP',[a-n,b-n,b+n,a+n]);boolean(insert,cut,'DIFFERENCE');bpy.data.objects.remove(cut,do_unlink=True)
boolean(ground,insert,'DIFFERENCE')

# Point-touching paving islands must have separate topology at their shared vertical edge.
bm=bmesh.new();bm.from_mesh(ground.data);remaining=set(bm.faces);components=[]
while remaining:
 stack=[remaining.pop()];group=[]
 while stack:
  f=stack.pop();group.append(f)
  for e in f.edges:
   if len(e.link_faces)!=2:continue
   for neighbor in e.link_faces:
    if neighbor in remaining:remaining.remove(neighbor);stack.append(neighbor)
 components.append(group)
vs=[];fs=[];slots=[]
for group in components:
 mapping={}
 for f in group:
  ids=[]
  for v in f.verts:
   if v not in mapping:mapping[v]=len(vs);vs.append(tuple(v.co))
   ids.append(mapping[v])
  fs.append(ids);slots.append(f.material_index)
materials=list(ground.data.materials);bm.free();me=bpy.data.meshes.new('R132_PAVING_SEPARATE_ISLANDS');me.from_pydata(vs,[],fs);me.update()
for material in materials:me.materials.append(material)
for f,slot in zip(me.polygons,slots):f.material_index=slot
ground.data=me

mat=bpy.data.materials['R129_MOAT_TURF_APPEARANCE_CANDIDATE'] if 'R129_MOAT_TURF_APPEARANCE_CANDIDATE' in bpy.data.materials else next(m for m in bpy.data.materials if m.name.startswith('R129') and 'TURF' in m.name)
insert.data.materials.clear();insert.data.materials.append(mat);uv=insert.data.uv_layers.get('R55_CONTEXT_METRIC_UV') or insert.data.uv_layers.new(name='R55_CONTEXT_METRIC_UV');insert.data.uv_layers.active=uv
for f in insert.data.polygons:
 f.material_index=0
 for li in f.loop_indices:
  q=insert.matrix_world@insert.data.vertices[insert.data.loops[li].vertex_index].co;uv.data[li].uv=(q.x/4,q.y/3)
for o in [ground,insert]:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[e for e in bm.edges if not e.link_faces],context='EDGES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_edges],context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
insert['source_ids']='OSMway759811369,063,096,122';insert['status']='mapped_woodland_ground_material_candidate';insert['assumption_note']='Archived mixed woodland footprint clipped to existing site crop. Flat inherited level and 4m route widths remain candidates; grass appearance represents understory, not surveyed species or bed limits.'
bpy.context.scene['stage']='R132 mapped woodland ground distinction';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R132_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=Path(base).name,changed_inherited_objects=[ground.name],closed_objects=[insert.name],woodland_way=w['id'],woodland_polygon=poly,retained_routes=routes,route_width_m=P['path_width_m'],osm_sha256=P['osm_sha256'],construction_acceptance=False),indent=2)+'\n')
