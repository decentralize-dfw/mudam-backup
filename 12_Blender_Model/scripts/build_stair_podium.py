"""P09 partial: three source-contoured podium treads and corrected upward path."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_P09_MERDIVEN_{version}.blend'
if out.exists():raise RuntimeError('Version exists; choose a new version.')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_P07_GIRIS_v002.blend'))
S=bpy.context.scene;P=json.loads((B/'config/stair_podium.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];D=json.loads((B/'config/vertical_study.json').read_text());Z={p['id']:p['draft_value'] for p in D['parameters']};k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix']
def xy(p):
 u=k*p[0]+off[0];v=k*p[1]+off[1]
 return (M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960)
def pt(p,z):return (*xy(p),z)
c=bpy.data.collections.new('P09_GH_UP_PODIUM_STUDY');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(c);mat=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];names=[]
for i,item in enumerate(P['contours']):
 points=[xy(p) for p in item['footprint_canonical']];n=len(points);poly=[Vector((*p,0)) for p in points];lookup={tuple(p):j for j,p in enumerate(poly)}
 def idx(v):return v if isinstance(v,int) else lookup[tuple(v)]
 tris=tessellate_polygon([poly]);faces=[tuple(idx(v) for v in reversed(t)) for t in tris]+[tuple(idx(v)+n for v in t) for t in tris]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
 bottom=i*P['draft_riser_m'];top=(i+1)*P['draft_riser_m'];verts=[(x,y,bottom) for x,y in points]+[(x,y,top) for x,y in points]
 me=bpy.data.meshes.new('P09_PODIUM_'+str(i+1));me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(me.name,me);c.objects.link(ob);me.materials.append(mat);names.append(ob.name)
 for key,value in dict(element_id=ob.name,element_type='observed_podium_tread',zone_id='GH_UP',level_id='L00',source_ids='PDF2016,102,021,022,023',source_path_index=item['source_path_index'],confidence_xy='C source contour; closure D',confidence_z='D riser height assumption',status='partial_stair_study',assumption_note='Three observed steps only. No full flight riser count inferred from schematic diagram.',export_group='P09_STUDY_ONLY').items():ob[key]=value
# Replace the reversed P05 direction guide, without pretending a guide is a stair.
old=bpy.data.objects['P05_PATH_GH_UP'];old.hide_render=True;old.hide_set(True);old['status']='superseded_reversed_direction'
points=[pt(P['direction']['bottom_canonical'],0),pt(P['direction']['podium_canonical'],P['draft_podium_top_z']),pt(P['direction']['upper_landing_canonical'],Z['Z_LP1_FINISH'])]
cu=bpy.data.curves.new('P09_GH_UP_CORRECTED_PATH','CURVE');cu.dimensions='3D';cu.bevel_depth=.04;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
for p,v in zip(sp.points,points):p.co=(*v,1)
guide=bpy.data.objects.new(cu.name,cu);c.objects.link(guide);cu.materials.append(bpy.data.materials['P05_UP_PATH']);guide['status']='direction_guide_not_stair';guide['assumption_note']='Low bulbous podium toward narrow upper landing. Full flight not modeled.'
# Dedicated close review, with surrounding candidate geometry hidden only during render.
cd=bpy.data.cameras.new('P09_PODIUM_REVIEW');cam=bpy.data.objects.new(cd.name,cd);bpy.data.collections['99_QA'].objects.link(cam);cam.location=pt((563,425),9);target=Vector(pt((494,489),.3));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=12
S['stage']='P09 partial: three podium risers and corrected GH_UP direction; entry pilot retained';S['current_file']=out.name
for key in ['008','011','013','022','023']:
 path=next(R.glob('0[457]*/*/'+key+'_*'),None)
 if path is None:path=next(p for p in R.rglob(key+'_*') if p.suffix.lower() in ['.jpg','.jpeg','.png','.webp'] and 'references' not in p.parts)
 im=bpy.data.images.load(str(path),check_existing=True);im.pack();ref=bpy.data.objects.new('REF_P09_'+key,None);bpy.data.collections['00_REFERENCE_LOCKED'].objects.link(ref);ref.empty_display_type='IMAGE';ref.data=im;ref.location=(180,int(key)*5,0);ref.empty_display_size=10;ref.hide_render=True;ref.hide_set(True);ref.hide_select=True;ref['source_ids']=key
txt=bpy.data.texts.new('P09_READ_ME');txt.write('P09 PARTIAL STAIR STUDY\nThree curved podium steps from PDF2016 paths 138/137/136, verified in photos 021/022.\nDraft rise 0.16 m, not measured. PDF ink outlines are NOT physical tread thickness.\nGH_UP old P05 path direction was reversed and is superseded. Correct low end is curved podium; +1 end is the narrow bridge-side end.\nFull flight, riser count, landing closure, rails and GH_DOWN geometry remain pending.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
visibility={ob.name:ob.hide_render for ob in S.objects}
keep=set(names+[guide.name,'P05_FLOOR_L00_GH'])
for ob in S.objects:
 if ob.type not in ['LIGHT','CAMERA'] and ob.name not in keep:ob.hide_render=True
S.camera=cam;S.render.resolution_x=1500;S.render.resolution_y=1200;S.render.resolution_percentage=100;S.render.filepath=str(B/'renders/qa/P09_podium.png');bpy.ops.render.render(write_still=True)
for name,value in visibility.items():bpy.data.objects[name].hide_render=value
report=dict(file=out.relative_to(R).as_posix(),podium_meshes=names,observed_risers=3,draft_rise_m=P['draft_riser_m'],top_z=P['draft_podium_top_z'],corrected_path=points,full_flight_modeled=False,gh_down_unchanged=True,sources=['PDF2016_page5','021','022','023'])
(B/'reports/P09_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('P09_SAVED',out)
