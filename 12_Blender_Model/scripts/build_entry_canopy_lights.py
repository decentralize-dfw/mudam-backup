"""R61 six observed canopy fixtures, planar-photo placement candidates only."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R60_GIRIS_TAS_TAVAN_YUZEY_v002.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R61_SACAK_GOMME_ISIK_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));P=json.loads((B/'reports/R61_canopy_light_study.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];H=P['plane_z'];root=bpy.data.collections.new('R61_OBSERVED_CANOPY_FIXTURE_CANDIDATES');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];hidden=[];rows=[];slab=bpy.data.objects['P07_CANOPY_SLAB_ENVELOPE']
def point(p,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*p[0]+ox;b=k*p[1]+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def mat(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
rim=mat('R61_FIXTURE_RIM_CANDIDATE',(.22,.24,.25),.85,.30);reflector=mat('R61_REFLECTOR_CANDIDATE',(.52,.53,.54),.9,.2);dark=mat('R61_UNLIT_LENS_CANDIDATE',(.045,.047,.05),.25,.24)
def lathe(name,c,profile,material,kind):
 N=48;vs=[tuple(c+Vector((r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z))) for r,z in profile for i in range(N)];fs=[(j*N+i,j*N+(i+1)%N,((j+1)%len(profile))*N+(i+1)%N,((j+1)%len(profile))*N+i) for j in range(len(profile)) for i in range(N)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(material)
 for k,v in dict(element_id=name,element_type=kind,zone_id='ENTRY_CANOPY',level_id='MULTI',source_ids='008,011,012,013,102',status='photo_planar_placement_candidate',confidence_xy='D conditional homography; source corners uncertain',confidence_z='D inherited soffit',confidence_detail='C circular fixture topology; D diameter/profile',assumption_note='Six clearly visible centers from008 only. Homography fit8.82px, leave-one-out up to188.9px; placement is not independent metric calibration. No inferred hidden fixtures, product or photometry.').items():ob[k]=v

 for f in me.polygons:f.use_smooth=abs(profile[f.index//N][1]-profile[(f.index//N+1)%len(profile)][1])>1e-6
 made.append(name);return ob
def cylinder(name,c,r,z0,z1,material,kind):
 N=48;vs=[tuple(c+Vector((r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z))) for z in [z0,z1] for i in range(N)];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(material);o['element_id']=name;o['element_type']=kind;o['zone_id']='ENTRY_CANOPY';o['level_id']='MULTI';o['source_ids']='008,011,012,013';o['status']='unmeasured_fixture_detail_candidate';made.append(name);return o
for q in P['lights']:
 c=point(q['canonical'],H);key='R61_'+q['id'];cut=cylinder(key+'_CUTTER',c,.082,-.025,.092,dark,'hidden_recess_tool');cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE';made.remove(cut.name);hidden.append(cut.name);m=slab.modifiers.new(key+'_RECESS','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut
 trim=lathe(key+'_RIM',c,[(.09,-.004),(.09,.014),(.067,.014),(.067,-.004)],rim,'recessed_circular_trim_candidate')
 refl=lathe(key+'_REFLECTOR',c,[(.067,.012),(.025,.064),(.027,.066),(.069,.012)],reflector,'conical_reflector_candidate')
 lens=cylinder(key+'_LENS',c,.026,.064,.068,dark,'unlit_lens_candidate');back=cylinder(key+'_BACK',c,.081,.071,.078,dark,'fixture_back_candidate');rows.append(dict(id=q['id'],canonical=q['canonical'],center=list(c),image_pixel=q['image_pixel'],rim=trim.name,reflector=refl.name,lens=lens.name,back=back.name))
bpy.context.scene['stage']='R61 six source-visible canopy fixture candidates';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R61_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,hidden_tools=hidden,changed_inherited_objects=[slab.name],fixtures=rows,soffit_z=H,diameter_candidate_m=.18,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['008','011','012','013','102']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R61_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=P['limits']+['Fixture diameter180mm and recessed profile are candidates. No light energy, product identity or unseen fixture count inferred.']),indent=2),encoding='utf8');print('R61',len(rows),'fixtures',len(made),'closed parts')
