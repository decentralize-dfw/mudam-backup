"""R38 mapped approach terrain and OSM tree masses; no botanical precision claim."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(Path(__file__).parent));from plan_union import union,inside
P=json.loads((B/'config/park_landings.json').read_text());Q=json.loads((B/'reports/R34_build_report.json').read_text());version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R38_PARK_YAKLASIM_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P18_PARK_APPROACH_CONTEXT');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];trees=[];skipped=[]
def mat(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=.85;return m
paving=mat('R38_APPROACH_PAVING_CANDIDATE',(.32,.33,.31));bark=mat('R38_TREE_TRUNK_PROXY',(.11,.067,.035));leaf=mat('R38_TREE_CROWN_PROXY',(.09,.16,.055))
def mesh(name,vs,fs,material,source,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(material)
 for k,v in dict(element_id=name,element_type=kind,level_id='SITE',zone_id='ENTRANCE_PARK',source_ids=source,status='representative_context',confidence_xy='C archived OSM',confidence_z='D representative',confidence_detail='D context mass',assumption_note='Flat approach and tree dimensions unmeasured. Tree XY from OSM; no species or botanical detail assertion.').items():o[k]=v
 made.append(name);return o
path_polys=[]
for a,b in zip(P['path_centerline'],P['path_centerline'][1:]):
 a,b=Vector(a),Vector(b);d=(b-a).normalized();n=Vector((-d.y,d.x))*P['path_width_m']/2;path_polys.append([list(a-n),list(b-n),list(b+n),list(a+n)])
loops=union([P['ground_polygon']]+path_polys,subtract_polygons=[Q['union_boundary']]);assert len(loops)==1;poly=loops[0]
# Drop sub-0.01mm split fragments before float32 Blender mesh storage.
while True:
 removed=False
 for i in range(len(poly)):
  a,b,c=Vector(poly[i-1]),Vector(poly[i]),Vector(poly[(i+1)%len(poly)]);ac=c-a
  if (b-a).length<1e-5 or (ac.length>0 and abs((b-a).x*ac.y-(b-a).y*ac.x)/ac.length<1e-5 and (b-a).dot(c-b)>=0):
   poly.pop(i);removed=True;break
 if not removed:break
area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1]))/2;assert area>0;n=len(poly);z=P['ground_z'];vs=[(x,y,h) for h in [z-P['ground_thickness_m'],z] for x,y in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh('R38_PARK_APPROACH_GROUND',vs,fs,paving,'OSM49911001,OSM83345393,063,096,116','cropped_flat_approach_candidate')
for row in P['trees']:
 x,y=row['xy'];id=row['id']
 if not inside((x,y),poly):skipped.append(dict(id=id,reason='outside final ground / on bridge'));continue
 h=P['tree_height_m'];rad=P['tree_radius_m'];tr=P['tree_trunk_radius_m'];N=16;vs=[(x+math.cos(i*math.tau/N)*tr,y+math.sin(i*math.tau/N)*tr,z+height) for height in [0,h*.62] for i in range(N)];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];trunk=mesh(f'R38_TREE_{id}_TRUNK',vs,fs,bark,'OSMnode'+id,'mapped_tree_trunk_proxy')
 rings=[(.33,.32),(.40,.85),(.55,1.0),(.72,.82),(.90,.43),(.99,.07)];vs=[]
 for j,(height,radius) in enumerate(rings):
  for i in range(N):
   angle=i*math.tau/N;variation=1+.07*math.sin(i*2.6+j*.7+int(id[-2:]));vs.append((x+math.cos(angle)*radius*rad*variation,y+math.sin(angle)*radius*rad*variation,z+height*h))
 fs=[tuple(range(N-1,-1,-1)),tuple(range((len(rings)-1)*N,len(rings)*N))]+[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(len(rings)-1) for i in range(N)];crown=mesh(f'R38_TREE_{id}_CROWN',vs,fs,leaf,'OSMnode'+id,'mapped_tree_canopy_proxy')
 for face in crown.data.polygons:face.use_smooth=True
 trees.append(dict(id=id,xy=row['xy'],height=h,trunk=trunk.name,crown=crown.name))
bpy.context.scene['stage']='R38 park approach with mapped tree masses';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R38_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R38_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=[],ground_polygon=poly,ground_z=z,ground_area_m2=area,trees=trees,skipped_trees=skipped,routes={'NORTH_EXTENSION':[[29.42,65.7],[29.77,79.32]],'EAST_EXTENSION':[[61.4,32.26],[73.65,31.95]]},construction_acceptance=False),indent=2),encoding='utf8')
