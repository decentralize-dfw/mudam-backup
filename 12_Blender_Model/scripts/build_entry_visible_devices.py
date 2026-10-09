"""R63 source014 visible control faces and exit sign, no device function claim."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R62_BALIKSIRTI_DOSEME_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R63_GIRIS_PANEL_LEVHA_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));Q=json.loads((B/'reports/R57_build_report.json').read_text());O,U,N=map(Vector,[Q['origin'],Q['axis'],Q['outward']]);Z=Vector((0,0,1));root=bpy.data.collections.new('R63_ENTRY_VISIBLE_DEVICES_CANDIDATE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];bounds={}
def material(name,c,metal=0,rough=.5):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m
metal=material('R63_BRUSHED_CONTROL_METAL',(.23,.25,.25),.8,.40);dark=material('R63_DARK_CONTROL_FACE',(.008,.011,.010),.15,.6);square=material('R63_DARK_SQUARE_INSERT',(.055,.060,.045),.2,.4);green=material('R63_SIGN_GREEN',(.012,.14,.065));white=material('R63_SIGN_WHITE',(.8,.81,.73));led=material('R63_INDICATOR_GREEN_APPEARANCE',(.025,.5,.07));red=material('R63_BUTTON_RED_APPEARANCE',(.38,.008,.004))
def prism(name,poly,d0,d1,mat,kind):
 if name.startswith('R63_SIGN_'):poly=[(-x,z) for x,z in poly]
 vs=[tuple(O+U*x+N*d+Z*z) for d in [d0,d1] for x,z in poly];k=len(poly);fs=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for key,val in dict(element_id=name,element_type=kind,zone_id='ENT',level_id='L00',source_ids='014',status='visible_device_appearance_candidate',confidence_xy='C inside-view right-hand post association; D offsets',confidence_z='D photo proportion against existing conditional vestibule',confidence_detail='C visible face arrangement; D dimensions and device identity',assumption_note='Only source014 visible faces. Not a certified safety sign, electrical design, product specification or verified control function. Small lettering and grille perforations unresolved.').items():ob[key]=val
 made.append(name);bounds[name]=dict(x=[min(p[0] for p in poly),max(p[0] for p in poly)],d=[d0,d1],z=[min(p[1] for p in poly),max(p[1] for p in poly)]);return ob
def box(name,x0,x1,d0,d1,z0,z1,mat,kind):return prism(name,[(x0,z0),(x1,z0),(x1,z1),(x0,z1)],d0,d1,mat,kind)
def disc(name,x,z,r,d0,d1,mat,kind):return prism(name,[(x+r*math.cos(i*math.tau/32),z+r*math.sin(i*math.tau/32)) for i in range(32)],d0,d1,mat,kind)
# Viewed from inside, right means -U. Both are attached to existing round posts.
box('R63_INNER_PANEL_BODY',-1.27,-1.05,-.10,-.02,1.35,1.81,metal,'visible_rectangular_control_housing')
box('R63_INNER_PANEL_FACE',-1.253,-1.067,-.103,-.099,1.367,1.793,dark,'dark_control_face')
box('R63_INNER_SPEAKER_REGION',-1.23,-1.09,-.105,-.102,1.62,1.765,dark,'unresolved_speaker_grille_region')
box('R63_INNER_SQUARE_INSERT',-1.214,-1.106,-.107,-.102,1.485,1.593,square,'visible_square_insert_unknown_function')
box('R63_OUTER_PANEL_BODY',-1.225,-1.075,2.12,2.18,1.28,1.66,metal,'visible_narrow_control_housing')
box('R63_OUTER_PANEL_FACE',-1.197,-1.103,2.116,2.121,1.295,1.645,dark,'narrow_dark_control_face')
disc('R63_OUTER_BUTTON_RING',-1.15,1.345,.030,2.112,2.117,metal,'visible_round_button_surround')
disc('R63_OUTER_BUTTON_CENTER',-1.15,1.345,.011,2.109,2.113,red,'red_button_appearance')
for i in range(8):
 a=i*math.tau/8;disc(f'R63_OUTER_INDICATOR_{i}',-1.15+.022*math.cos(a),1.345+.022*math.sin(a),.003,2.108,2.113,led,'green_indicator_candidate_count')
# Sign body top reaches the retained vestibule glass roof through two small candidate clips.
box('R63_EXIT_SIGN_BODY',-.15,.15,-.07,-.015,3.88,4.06,metal,'exit_sign_housing_candidate')
box('R63_EXIT_SIGN_FACE',-.139,.139,-.073,-.069,3.892,4.048,green,'green_exit_sign_face_candidate')
for i,x in enumerate([-.09,.09]):box(f'R63_EXIT_SIGN_CLIP_{i}',x-.012,x+.012,-.04,.02,4.057,4.112,metal,'sign_roof_clip_candidate')
# Source014 shows a downward arrow and right-hand running figure; simplified geometric artwork.
prism('R63_SIGN_ARROW',[(-.104,4.025),(-.083,4.025),(-.083,3.950),(-.055,3.974),(-.055,3.946),(-.094,3.908),(-.133,3.946),(-.133,3.974),(-.104,3.950)],-.075,-.072,white,'downward_arrow_candidate')
box('R63_SIGN_DOOR_TOP',.02,.118,-.075,-.072,4.026,4.038,white,'pictogram_door_top')
box('R63_SIGN_DOOR_RIGHT',.106,.118,-.075,-.072,3.902,4.038,white,'pictogram_door_jamb')
disc('R63_SIGN_HEAD',.057,4.011,.011,-.075,-.072,white,'pictogram_head')
prism('R63_SIGN_TORSO',[(.042,3.996),(.062,4.000),(.077,3.965),(.059,3.955),(.037,3.975)],-.075,-.072,white,'pictogram_torso')
prism('R63_SIGN_ARM',[(.045,3.994),(.038,3.985),(.006,3.997),(.010,4.008)],-.075,-.072,white,'pictogram_arm')
prism('R63_SIGN_LEG_LEFT',[(.055,3.966),(.068,3.958),(.037,3.920),(.020,3.920)],-.075,-.072,white,'pictogram_leg')
prism('R63_SIGN_LEG_RIGHT',[(.064,3.965),(.077,3.970),(.102,3.920),(.087,3.914)],-.075,-.072,white,'pictogram_leg')
bpy.context.scene['stage']='R63 entry visible control faces and exit sign';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R63_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=[],origin=list(O),axis=list(U),outward=list(N),local_bounds=bounds,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id']=='014']
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R63_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=['014 inside view: large panel on near right post; narrow button panel on far right post; overhead green downward exit sign.','All dimensions, post offsets, indicator count and artwork are candidates. Function, products, wiring and exact perforations unresolved.','013 outer-facing panel is separate and not inferred as the same inner-facing device.']),indent=2),encoding='utf8');print('R63',len(made),'closed parts')
