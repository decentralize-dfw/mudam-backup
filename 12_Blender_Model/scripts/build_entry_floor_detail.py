"""R57: flush vestibule mat and ribbed side inserts seen in014, dimensions conditional."""
from pathlib import Path
import bpy,bmesh,json,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R56_PARK_AGAC_TACI_v002.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R57_GIRIS_PASPAS_IZGARA_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));Q=json.loads((B/'reports/R57_floor_probe.json').read_text());origin,u,n=map(Vector,[Q['origin'],Q['axis'],Q['outward']]);up=Vector((0,0,1));root=bpy.data.collections.new('R57_ENTRY_FLOOR_DETAIL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];bounds={}
def material(name,col,rough,metallic=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metallic;return m
fibre=material('R57_MAT_FIBRE_CANDIDATE',(.045,.048,.047),.96);metal=material('R57_GRILLE_METAL_CANDIDATE',(.13,.14,.14),.48,.75);dark=material('R57_INSERT_BASE_CANDIDATE',(.009,.011,.011),.88)
def box(name,x0,x1,d0,d1,z0,z1,mat,kind):
 vs=[tuple(origin+u*x+n*d+up*z) for z in [z0,z1] for x,d in [(x0,d0),(x1,d0),(x1,d1),(x0,d1)]];fs=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)];me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='ENT',level_id='L00',source_ids='013,014,102',status='conditional_visible_floor_detail',confidence_xy='C existing vestibule; D insert layout',confidence_z='D flush insert candidate',assumption_note='014 shows central dark mats and ribbed side strips. All insert dimensions, recess depth, rib pitch and material are editable unmeasured candidates; no drain or hidden system inferred.').items():ob[k]=v
 made.append(name);bounds[name]=[x0,x1,d0,d1,z0,z1];return ob
# Candidate footprint stays inside the preserved 2.3x2.2m vestibule.
cut=box('R57_RECESS_CUTTER',-1.05,1.05,.08,2.12,-.022,.025,dark,'hidden_local_recess_tool');made.remove(cut.name);cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE'
for name in ['P05_FLOOR_L00_ENT','R34_APPROACH_CONTINUOUS_DECK']:
 ob=bpy.data.objects[name];m=ob.modifiers.new('R57 flush insert recess','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;changed.append(name)
box('R57_INSERT_BASE',-1.05,1.05,.08,2.12,-.022,-.012,dark,'mat_recess_base_candidate')
for i,(x0,x1,d0,d1) in enumerate([(-1.05,-1.038,.08,2.12),(1.038,1.05,.08,2.12),(-1.038,1.038,.08,.092),(-1.038,1.038,2.108,2.12)]):box(f'R57_OUTER_RIM_{i}',x0,x1,d0,d1,-.012,0,metal,'insert_edge_trim_candidate')
for i in range(3):
 d0=.092+i*(2.016/3);d1=.092+(i+1)*(2.016/3);box(f'R57_MAT_{i}',-.735,.735,d0+.004,d1-.004,-.012,0,fibre,'vestibule_mat_panel_candidate')
 if i<2:box(f'R57_MAT_DIVIDER_{i}',-.735,.735,d1-.004,d1+.004,-.012,-.002,metal,'mat_divider_candidate')
for side in [-1,1]:
 x0,x1=sorted([side*.735,side*1.038]);box(f'R57_GRILLE_INNER_EDGE_{side}',side*.741-.006,side*.741+.006,.092,2.108,-.012,0,metal,'grille_edge_candidate')
 start=x0+.016;end=x1-.01;count=24;pitch=(end-start)/count
 for i in range(count):
  x=start+(i+.5)*pitch;box(f'R57_GRILLE_{side}_{i:02d}',x-.0023,x+.0023,.092,2.108,-.010,0,metal,'longitudinal_grille_bar_candidate')
bpy.context.scene['stage']='R57 flush vestibule mat and side grille candidates';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R57_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=changed,origin=list(origin),axis=list(u),outward=list(n),local_bounds=bounds,hidden_tools=[cut.name],recess_depth_m=.022,flush_top_z=0.,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['013','014','102']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R57_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=['Mat and ribbed strips visible in014; layout proportions and all details unmeasured.','Floor top retained at0; 22mm recess only a visualization assembly, no hidden drainage system or product inferred.','Door poses/hinges unchanged; actual mechanism unresolved.']),indent=2),encoding='utf8');print('R57',len(made),'closed objects')
