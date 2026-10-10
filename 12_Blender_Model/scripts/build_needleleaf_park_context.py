"""R130: archived needleleaf tags replace seven generic broadleaf crowns."""
from pathlib import Path
import bpy,bmesh,json,math,random,hashlib,xml.etree.ElementTree as ET
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent
P=json.loads((B/'config/park_landings.json').read_text());old=json.loads((B/'reports/R56_build_report.json').read_text());base='MUDAM_R129_TARIHI_TAS_VE_HENDEK_MALZEME_v002.blend';out=B/'scenes/MUDAM_R130_PARK_IGNE_YAPRAKLI_AGACLAR_v002.blend';assert not out.exists()
osm=R/P['osm_file'];assert hashlib.sha256(osm.read_bytes()).hexdigest()==P['osm_sha256'];nodes={n.attrib['id']:{t.attrib['k']:t.attrib['v'] for t in n.findall('tag')} for n in ET.parse(osm).getroot().findall('node')}
targets=[t for t in P['trees'] if t['tags'].get('leaf_type')=='needleleaved'];assert len(targets)==7
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));root=bpy.data.collections.new('R130_SOURCE_TAGGED_NEEDLELEAF_CONTEXT');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
bark=bpy.data.materials['R56_BARK_APPEARANCE_CANDIDATE'];tones=[]
for i,c in enumerate([(.029,.061,.032),(.044,.087,.043),(.063,.104,.053),(.036,.073,.052)]):
 m=bpy.data.materials.new(f'R130_NEEDLE_TONE_{i}_CANDIDATE');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=.85;tones.append(m)
made=[];changed=[];rows=[]
def mesh(name,vs,fs,mats,slots,tree,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o)
 for m in mats:me.materials.append(m)
 for f,s in zip(me.polygons,slots):f.material_index=s;f.use_smooth=True
 for k,v in dict(element_id=name,element_type=kind,zone_id='ENTRANCE_PARK',level_id='SITE',source_ids='OSMnode'+tree['id']+',063',status='representative_needleleaf_context',confidence_xy='C archived OSM',confidence_z='D inherited 8m envelope',confidence_detail='D generic needleleaf branching; species unknown',assumption_note='Needleleaf class read from archived OSM. Existing trunk XY and size envelope preserved. Shape, needles, density, colours and species are not a tree survey.').items():o[k]=v
 made.append(name);return o
for t in targets:
 assert nodes[t['id']]['leaf_type']=='needleleaved'
 previous=next(q for q in old['trees'] if q['id']==t['id']);rnd=random.Random(int(t['id'])+130);x,y=t['xy'];z=P['ground_z'];h=P['tree_height_m'];radius=P['tree_radius_m'];origin=Vector((x,y,z));bv=[];bf=[];nv=[];nf=[];slots=[]
 def branch(a,b,r0,r1):
  d=(b-a).normalized();u=d.cross(Vector((0,0,1))).normalized() if abs(d.z)<.95 else Vector((1,0,0));v=d.cross(u);k=len(bv);n=6
  bv.extend(tuple(c+rr*(math.cos(i*math.tau/n)*u+math.sin(i*math.tau/n)*v)) for c,rr in [(a,r0),(b,r1)] for i in range(n));bf.extend([tuple(k+i for i in range(n-1,-1,-1)),tuple(k+n+i for i in range(n))]+[(k+i,k+(i+1)%n,k+(i+1)%n+n,k+i+n) for i in range(n)])
 def needle(c,d):
  d=d.normalized();u=d.cross(Vector((0,0,1))).normalized() if abs(d.z)<.95 else Vector((1,0,0));v=d.cross(u);length=rnd.uniform(.13,.23);width=rnd.uniform(.014,.022);k=len(nv);vs=[c-d*length/2,c+d*length/2,c+u*width/2,c+v*width/3,c-u*width/2,c-v*width/3]
  if any(math.hypot(q.x-x,q.y-y)>radius or q.z<z+2.5 or q.z>z+h for q in vs):return
  nv.extend(tuple(q) for q in vs);nf.extend([(k,k+2+i,k+2+(i+1)%4) for i in range(4)]+[(k+1,k+2+(i+1)%4,k+2+i) for i in range(4)]);slots.extend([rnd.randrange(4)]*8)
 branch(origin+Vector((0,0,3.0)),origin+Vector((0,0,h-.08)),.09,.008)
 for tier in range(16):
  f=tier/15;zz=2.85+f*(h-3.08);reach=(radius-.22)*(1-f*.89)
  for arm in range(7):
   angle=arm*math.tau/7+tier*.67+rnd.uniform(-.35,.35);d=Vector((math.cos(angle),math.sin(angle),0));side=Vector((-d.y,d.x,0));a=origin+Vector((0,0,zz+rnd.uniform(-.22,.22)));b=a+d*reach*rnd.uniform(.76,1.0)+Vector((0,0,rnd.uniform(-.18,.32)));branch(a,b,.035*(1-f*.8),.004)
   for j in range(1,7):
    anchor=a.lerp(b,j/7);end=anchor+d*.11+side*((-1 if j%2 else 1)*(.15+.15*(1-f)))+Vector((0,0,rnd.uniform(-.15,.32)));branch(anchor,end,.009,.002)
    for cluster in range(5):
     c=anchor.lerp(end,(cluster+.5)/5)
     for k in range(9):
      theta=k*math.tau/9+rnd.uniform(-.25,.25);direction=(end-anchor).normalized()*.3+Vector((math.cos(theta),math.sin(theta),rnd.uniform(-.4,.5)));needle(c+Vector((rnd.gauss(0,.065),rnd.gauss(0,.065),rnd.gauss(0,.12))),direction)
 bo=mesh('R130_TREE_'+t['id']+'_BRANCHES',bv,bf,[bark],[0]*len(bf),t,'representative_needleleaf_branches');no=mesh('R130_TREE_'+t['id']+'_NEEDLES',nv,nf,tones,slots,t,'representative_needleleaf_foliage')
 for name in [previous['branches'],previous['foliage']]:bpy.data.objects[name].hide_render=True;bpy.data.objects[name].hide_set(True);changed.append(name)
 rows.append(dict(id=t['id'],xy=t['xy'],height=h,radius=radius,source_leaf_type=nodes[t['id']]['leaf_type'],trunk=previous['trunk'],hidden=[previous['branches'],previous['foliage']],branches=bo.name,foliage=no.name,needle_solids=len(nf)//8))
bpy.context.scene['stage']='R130 source-tagged needleleaf park context';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R130_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=changed,trees=rows,osm_sha256=P['osm_sha256'],construction_acceptance=False),indent=2),encoding='utf8');print('R130',len(rows),'trees',len(made),'objects')
