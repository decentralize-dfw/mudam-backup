"""R65 X ties and visible end fittings on the existing conditional eight-bay link."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R64_GIRIS_ESIK_GECIS_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R65_GECIT_CAPRAZ_GERGI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));P=json.loads((B/'reports/R18_build_report.json').read_text())['portals'];Z=Vector((0,0,1));root=bpy.data.collections.new('R65_LINK_CROSS_TIE_CANDIDATES');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];ties=[];supports=[];mat=bpy.data.materials['P10_FRAME_PREVIEW'].copy();mat.name='R65_TENSION_ROD_METAL_CANDIDATE';bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.36,.38,.37,1);bs.inputs['Metallic'].default_value=.85;bs.inputs['Roughness'].default_value=.27
def mesh(name,vs,fs,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(p) for p in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='PAV_LINK',level_id='L00',source_ids='067,068',status='photo_supported_tie_family_candidate',confidence_xy='C existing link; D inherited eight-bay repetition',confidence_z='D roof clearance candidate',confidence_detail='C cross ties and barrel/fork family; D all sizes',assumption_note='067/068 show X rods and cylindrical end fittings.8 bays inherited;10mm rods,40mm barrels, clevis profiles and18mm crossing separation unmeasured. No structural force, thread or hidden anchorage inferred.').items():ob[k]=v
 made.append(name);return ob
def tube(name,a,b,r,kind):
 axis=(b-a).normalized();ref=Z if abs(axis.z)<.9 else Vector((1,0,0));u=axis.cross(ref).normalized()*r;v=axis.cross(u).normalized()*r;n=32;ring=[u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n) for i in range(n)];ob=mesh(name,[p+t for p in [a,b] for t in ring],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],kind)
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
def box(name,c,axis,x0,x1,y0,y1,z0,z1,kind):
 side=Z.cross(axis);vs=[c+axis*x+side*y+Z*z for z in [z0,z1] for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];return mesh(name,vs,[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)],kind)
for i,(pa,pb) in enumerate(zip(P,P[1:])):
 along=(Vector(pb['left'])-Vector(pa['left'])).normalized();across=(Vector(pa['right'])-Vector(pa['left'])).normalized();top=pa['top_z']
 for j,(ka,kb) in enumerate([('left','right'),('right','left')]):
  a=Vector(pa[ka])+across*(.10 if ka=='left' else -.10)+along*.018+Z*(top+.035+j*.018);b=Vector(pb[kb])+across*(.10 if kb=='left' else -.10)-along*.018+Z*(top+.035+j*.018);d=(b-a).normalized();key=f'R65_BAY_{i:02d}_DIAG_{j}';rod=tube(key+'_ROD',a+d*.18,b-d*.18,.005,'cross_tension_rod_candidate');ends=[]
  for e,c,axis,pi in [('A',a,d,i),('B',b,-d,i+1)]:
   side=Z.cross(axis).normalized();tube(key+'_'+e+'_TONGUE',c+axis*.015,c+axis*.08,.009,'clevis_to_barrel_shank_candidate');tube(key+'_'+e+'_BARREL',c+axis*.065,c+axis*.22,.020,'cylindrical_tension_terminal_candidate');tube(key+'_'+e+'_NECK',c+axis*.20,c+axis*.235,.008,'terminal_neck_candidate')
   for sign in [-1,1]:box(key+'_'+e+f'_FORK_{sign}',c,axis,-.018,.085,sign*.026-.004,sign*.026+.004,-.021,.021,'fork_cheek_candidate')
   tube(key+'_'+e+'_PIN',c+axis*.015-side*.038,c+axis*.015+side*.038,.006,'clevis_pin_candidate');box(key+'_'+e+'_LUG',c,axis,-.023,.039,-.014,.014,-(.055+j*.018),.014,'portal_lug_candidate');ends.append(dict(anchor=list(c),portal=f'R18_LINK_TRANSVERSE_{pi}',terminal_prefix=key+'_'+e));supports.append(dict(origin=list(c+Z*.06),portal=f'R18_LINK_TRANSVERSE_{pi}',max_distance=.13))
  ties.append(dict(id=key,rod=rod.name,start=list(a),end=list(b),ends=ends,crossing_z=top+.035+j*.018))
bpy.context.scene['stage']='R65 link cross ties and visible end fitting candidates';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R65_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=[],ties=ties,support_rays=supports,bays=len(P)-1,rod_radius_m=.005,crossing_separation_m=.018,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['067','068']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R65_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=['067 confirms repeated X rods,068 shows cylindrical barrel and fork-like terminal family.','Eight bays inherited from R18, not a new source count measurement. Rod diameter10mm, barrel40mm and detail/height all candidates.','18mm separation at crossing avoids impossible rod interpenetration; actual crossing detail unresolved.','No structural capacity, tension, thread, hidden weld or manufacturer claimed.']),indent=2),encoding='utf8');print('R65',len(ties),'ties',len(made),'parts')
