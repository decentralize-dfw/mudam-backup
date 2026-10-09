"""R66 longitudinal round link members and observed small cylinder fixture family."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R65_GECIT_CAPRAZ_GERGI_v002.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R66_GECIT_YAN_ARMATUR_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));P=json.loads((B/'reports/R18_build_report.json').read_text())['portals'];Z=Vector((0,0,1));root=bpy.data.collections.new('R66_LINK_SIDE_MEMBERS_AND_LIGHTS');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];fixtures=[];beams=[];metal=bpy.data.materials['P10_FRAME_PREVIEW'];dark=bpy.data.materials.new('R66_UNLIT_LENS_CANDIDATE');dark.use_nodes=True;bs=dark.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.007,.008,.008,1);bs.inputs['Roughness'].default_value=.3
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(p) for p in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='PAV_LINK',level_id='L00',source_ids='067,068',status='visible_link_fixture_family_candidate',confidence_xy='C longitudinal member; D repeated fixture stations',confidence_z='D inherited link head',confidence_detail='C cylinder/stub topology; D all dimensions',assumption_note='068 shows two small downward cylinders in the visible left bay;067 supports rows on both sides.32 fixtures extrapolate this module over eight inherited bays; total count not independently proven.80mm housing and100mm height unmeasured; no photometry or electrical design.').items():ob[k]=v
 made.append(name);return ob
def tube(name,a,b,r,mat,kind):
 axis=(b-a).normalized();ref=Z if abs(axis.z)<.9 else Vector((1,0,0));u=axis.cross(ref).normalized()*r;v=axis.cross(u).normalized()*r;n=32;ring=[u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n) for i in range(n)];ob=mesh(name,[p+t for p in [a,b] for t in ring],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,kind)
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
def housing(name,c):
 profile=[(.04,-.115),(.04,-.015),(.034,-.015),(.034,-.115)];n=48;vs=[c+Vector((r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z)) for r,z in profile for i in range(n)];fs=[(j*n+i,j*n+(i+1)%n,((j+1)%4)*n+(i+1)%n,((j+1)%4)*n+i) for j in range(4) for i in range(n)];ob=mesh(name,vs,fs,metal,'open_cylindrical_light_housing_candidate')
 for f in ob.data.polygons:f.use_smooth=f.index//n in [0,2]
 return ob
across=(Vector(P[0]['right'])-Vector(P[0]['left'])).normalized()
for side in ['left','right']:
 a=Vector(P[0][side])+Z*P[0]['top_z'];b=Vector(P[-1][side])+Z*P[-1]['top_z'];name='R66_LONGITUDINAL_'+side.upper();tube(name,a,b,.06,metal,'round_longitudinal_link_member_candidate');beams.append(name);inside=across if side=='left' else -across
 for i,(pa,pb) in enumerate(zip(P,P[1:])):
  for j,t in enumerate([.25,.75]):
   basepoint=Vector(pa[side]).lerp(Vector(pb[side]),t)+Z*pa['top_z'];c=basepoint+inside*.15;key=f'R66_LIGHT_{side.upper()}_{i:02d}_{j}';body=housing(key+'_BODY',c);lens=tube(key+'_LENS',c-Z*.107,c-Z*.104,.0345,dark,'recessed_unlit_lens_candidate');cap=tube(key+'_CAP',c-Z*.025,c-Z*.015,.035,metal,'housing_back_cap_candidate');stub=tube(key+'_STUB',basepoint+inside*.030-Z*.040,c-inside*.03-Z*.040,.012,metal,'fixture_side_bracket_candidate');fixtures.append(dict(id=key,center=list(c),body=body.name,lens=lens.name,cap=cap.name,stub=stub.name,beam=name,basepoint=list(basepoint),inside=list(inside)))
bpy.context.scene['stage']='R66 link longitudinal members and cylinder fixture candidates';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R66_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=[],beams=beams,fixtures=fixtures,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['067','068']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R66_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=['Round longitudinal side members and small downward cylindrical lights are visible.','Two fixtures per bay and side is an editable extrapolation from068/067;32 total not verified.','80mm diameter,100mm height, bracket and all construction details unmeasured; no light energy or hidden circuit.']),indent=2),encoding='utf8');print('R66',len(made),'parts',len(fixtures),'fixtures')
