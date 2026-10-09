"""R56: replace schematic cones at archived OSM positions with editable canopy studies."""
from pathlib import Path
import bpy,bmesh,json,sys,math,random,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R55_TARIHI_DUVAR_YUZEY_v002.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R56_PARK_AGAC_TACI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));old=json.loads((B/'reports/R38_build_report.json').read_text());P=json.loads((B/'config/park_landings.json').read_text());root=bpy.data.collections.new('R56_REPRESENTATIVE_PARK_CANOPIES');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];rows=[]
def mat(name,c):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=.82;return m
bark=mat('R56_BARK_APPEARANCE_CANDIDATE',(.085,.059,.033));leaves=[mat(f'R56_LEAF_TONE_{i}_CANDIDATE',c) for i,c in enumerate([(.038,.073,.014),(.065,.112,.022),(.087,.133,.027),(.045,.086,.038)])]
def mesh(name,vs,fs,mats,slots,tree,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o)
 for m in mats:me.materials.append(m)
 for f,slot in zip(me.polygons,slots):f.material_index=slot;f.use_smooth=True
 for k,v in dict(element_id=name,element_type=kind,level_id='SITE',zone_id='ENTRANCE_PARK',source_ids='OSMnode'+tree['id']+',063,065',status='representative_context',confidence_xy='C archived OSM',confidence_z='D inherited candidate',confidence_detail='D generic branching and foliage',assumption_note='OSM trunk positions preserved. Source photos establish leafy branching only; no species, individual-tree identity, botanical dimensions or seasonal survey.').items():o[k]=v
 made.append(name);return o
for tree in old['trees']:
 rnd=random.Random(int(tree['id'])+5609);x,y=tree['xy'];h=tree['height'];z=P['ground_z'];rad=P['tree_radius_m'];bv=[];bf=[];lv=[];lf=[];ls=[];segments=0;leaf_count=0
 def branch(a,b,r0,r1):
  global segments
  d=(b-a).normalized();u=d.cross(Vector((0,0,1))).normalized() if abs(d.z)<.95 else Vector((1,0,0));v=d.cross(u).normalized();n=8;k=len(bv)
  bv.extend(tuple(c+rr*(math.cos(i*math.tau/n)*u+math.sin(i*math.tau/n)*v)) for c,rr in [(a,r0),(b,r1)] for i in range(n));bf.extend([tuple(k+i for i in range(n-1,-1,-1)),tuple(k+n+i for i in range(n))]+[(k+i,k+(i+1)%n,k+(i+1)%n+n,k+i+n) for i in range(n)]);segments+=1
 def leaf(c):
  global leaf_count
  angle=rnd.uniform(0,math.tau);tilt=rnd.uniform(-.7,.7);u=Vector((math.cos(angle),math.sin(angle),tilt)).normalized();v=Vector((-math.sin(angle),math.cos(angle),rnd.uniform(-.3,.3))).normalized();v=(v-u*v.dot(u)).normalized();n=u.cross(v);length=rnd.uniform(.16,.24);width=length*rnd.uniform(.30,.48);k=len(lv);lv.extend(tuple(p) for p in [c+u*length/2,c+v*width/2,c-u*length/2,c-v*width/2,c+n*.002,c-n*.002]);lf.extend([(k+4,k+i,k+(i+1)%4) for i in range(4)]+[(k+5,k+(i+1)%4,k+i) for i in range(4)]);ls.extend([rnd.randrange(len(leaves))]*8);leaf_count+=1
 # A tapered leader continues the preserved R38 trunk within its old crown envelope.
 origin=Vector((x,y,z));branch(origin+Vector((0,0,h*.56)),origin+Vector((0,0,h*.97)),.10,.018)
 for layer in range(8):
  frac=.36+layer*.078;reach=rad*(.86 if layer<4 else 1-(layer-3)*.16)
  for arm in range(5):
   angle=arm*math.tau/5+layer*.61+rnd.uniform(-.15,.15);direction=Vector((math.cos(angle),math.sin(angle),0));start=origin+Vector((0,0,h*frac));tip=start+direction*reach+Vector((0,0,.30+rnd.random()*.25));branch(start,tip,.044*(1-layer*.07),.012)
   for fork in range(3):
    t=.42+fork*.25;anchor=start.lerp(tip,t);side=Vector((-direction.y,direction.x,0))*(.34 if fork%2 else -.34);end=anchor+side+direction*.15+Vector((0,0,.25));branch(anchor,end,.012,.004)
    for j in range(80):
     # Volume around a supported twig, with an explicit inherited radius/height envelope.
     q=end+Vector((rnd.gauss(0,.30),rnd.gauss(0,.30),rnd.gauss(0,.25)));delta=q-origin;rr=math.hypot(delta.x,delta.y)
     if rr>rad-.13:q.x=x+delta.x*(rad-.13)/rr;q.y=y+delta.y*(rad-.13)/rr
     q.z=max(z+h*.33+.13,min(z+h-.13,q.z));leaf(q)
 branch_ob=mesh('R56_TREE_'+tree['id']+'_BRANCHES',bv,bf,[bark],[0]*len(bf),tree,'representative_tree_branches');leaf_ob=mesh('R56_TREE_'+tree['id']+'_LEAVES',lv,lf,leaves,ls,tree,'representative_tree_foliage')
 oldc=bpy.data.objects[tree['crown']];oldc.hide_render=True;oldc.hide_set(True);changed.append(oldc.name);rows.append(dict(id=tree['id'],xy=tree['xy'],height=h,radius=rad,trunk=tree['trunk'],old_crown=oldc.name,branches=branch_ob.name,foliage=leaf_ob.name,branch_segments=segments,leaf_solids=leaf_count))
bpy.context.scene['stage']='R56 OSM-located representative park canopies';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R56_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=changed,trees=rows,geometry_scope='Only old crown visibility changes; new closed branch and leaf components. Existing trunks, paths, terrain and all building geometry preserved.',construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['063','065']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R56_source_receipt.json').write_text(json.dumps(dict(sources=sources,position_source='config/park_landings.json, R38_source_receipt.json archived OSM',limits=['Mixed canopy forms visible in063/065; individual species/identities not assigned.','Height8m/radius2.2m inherited unmeasured candidates. Generic branching, leaf size and count are visualization geometry.','No ground extent, planting bed, paving route or building geometry changed.']),indent=2),encoding='utf8');print('R56',len(rows),'trees',sum(t['leaf_solids'] for t in rows),'closed leaves')
