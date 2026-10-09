"""R94 correct screenshot-marked legacy leaves and roof interface gaps."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent
base='MUDAM_R93_KUZEY_CAM_PROFIL_HIZALAMA_v001.blend';out=B/'scenes/MUDAM_R94_ISARETLI_KABUK_BIRLESIMLERI_v003.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
C=json.loads((B/'config/foundation.json').read_text())['calibration'];root=bpy.data.collections.new('R94_MARKED_ENVELOPE_CORRECTIONS');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
made=[];changed=[];definitions=[];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R16_EXTERIOR_DARK_COATING_CANDIDATE'];up=Vector((0,0,1))
def point(p,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*p[0]+ox;b=k*p[1]+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def solid(name,ps,n,depth,mat,kind):
 N=len(ps);me=bpy.data.meshes.new(name);me.from_pydata([list(p) for p in ps]+[list(p-n*depth) for p in ps],[],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,source_ids='102,103,101,026,043,093,116',status='conditional_screenshot_junction_correction',assumption_note='Existing source boundaries retained. Roof level, build-up and glazing modules are inherited candidates, not surveyed dimensions.').items():o[k]=v
 made.append(name);return o
def hide(name,why):
 o=bpy.data.objects[name];o.hide_render=True;o.hide_set(True);changed.append(name);definitions.append(dict(name=name,action='superseded',reason=why))
# 103 and 043 distinguish the upper stair approach from the actual gallery enclosure.
# This legacy wall projected from the spiral core into a glazed circulation volume.
o=bpy.data.objects['R10_UPPER_DIAGONAL_WALL'];o.data=o.data.copy();before=[list(o.matrix_world@v.co) for v in o.data.vertices];inv=o.matrix_world.inverted()
for v in o.data.vertices:
 w=o.matrix_world@v.co
 if w.z>9.718577096381804:w.z=9.718577096381804;v.co=inv@w
o.data.update();changed.append(o.name);made.append(o.name);definitions.append(dict(name=o.name,action='trim_top_to_R26_glass_cover',before_world_vertices=before,top_z=9.718577096381804,reason='Retain stair-side enclosure below the adjoining R26 glass cover; remove unsupported blade protruding above that cover. Exact parapet height remains candidate.'))
# Full-height cyan plane contradicts the open passage below the glazed band in026.
hide('P05_MAIN_ATRIUM_BASE_2','Legacy full-height glazing proxy across internal west passage;026 shows open lower passage and glazing above.')
# Internal south proxy is a remnant of the old whole-atrium enclosure, behind the retained roof deck/R90 exterior glazing.
hide('R33_MAIN_PASSAGE_HIGH_REMAINDER','Unverified internal tinted screen removed. Lower passage and R90 exterior glazing retained; exact internal head arrangement remains open.')
# Restore the upper west transition in the established outer roof plane, aligned to band rows.
a=point([688,430],9.718577096381804);b=point([688,464],9.718577096381804);u=(b-a).normalized();n=u.cross(up).normalized();W=(b-a).length;H=13.923118133013933-a.z
if n.dot(a-point([575,447]))<0:n=-n
fw=.075;gap=.012
for i in range(3):
 for j in range(3):
  x0,x1=W*i/3,W*(i+1)/3;z0,z1=H*j/3,H*(j+1)/3
  solid(f'R94_WEST_TRANSITION_GLASS_{i}_{j}',[a+u*x+up*z for x,z in [(x0+gap,z0+gap),(x1-gap,z0+gap),(x1-gap,z1-gap),(x0+gap,z1-gap)]],n,.018,glass,'glazing_panel_candidate')
for i in range(4):
 x=W*i/3;solid(f'R94_WEST_TRANSITION_MULLION_{i}',[a+u*xx+up*z+n*.025 for xx,z in [(x-fw/2,0),(x+fw/2,0),(x+fw/2,H),(x-fw/2,H)]],n,.14,metal,'glazing_frame_candidate')
for j in range(4):
 z=H*j/3;solid(f'R94_WEST_TRANSITION_TRANSOM_{j}',[a+u*x+up*zz+n*.025 for x,zz in [(0,z-fw/2),(W,z-fw/2),(W,z+fw/2),(0,z+fw/2)]],n,.14,metal,'glazing_frame_candidate')
# Exterior roof strip between cafe-back line and gallery front, not a solid full-height wall fill.
poly=[[688,432],[798,322],[798,356],[685.9,468.7]];z=12.723118
solid('R94_WEST_INTERSTITIAL_ROOF',[point(p,z) for p in poly],up,.20,stone,'roof_interface_slab_candidate');definitions.append(dict(name=made[-1],polygon_canonical=poly,top_z=z,reason='Connect established cafe-back boundary to gallery boundary at inherited main roof datum; underside remains open. Exact drainage/cover build-up unmeasured.'))
# Reconcile the two inherited east high-wall planes above the existing portal head only.
poly=[[457.878,467.122],[457.878,555],[462.4,555],[462.4,460.7]]
solid('R94_EAST_HIGH_WALL_JOIN',[point(p,13.923118) for p in poly],up,13.923118-9.718577,stone,'upper_wall_leaf_connection_candidate');definitions.append(dict(name=made[-1],polygon_canonical=poly,z0=9.718577,z1=13.923118,reason='Join existing gallery and atrium-side leaves above portal head without closing lower circulation.'))
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=changed,definitions=definitions,glazing_origin=list(a),glazing_u=list(u),glazing_normal=list(n),glazing_width=W,glazing_height=H,construction_acceptance=False,limits=['Three screenshots now have actual geometry changes, but source-complete building acceptance remains open.','R10 approach wall retained below the adjoining R26 glass cover; two legacy cyan internal screens removed. R23 gallery enclosure and portals retained.','West roof strip inherits12.723118m datum; hidden structure, drainage and waterproofing remain unknown.','West transition glazing3x3 modules and profile sizes are candidates.','No artwork or temporary exhibition elements added.'])
bpy.context.scene['stage']='R94 screenshot-marked envelope corrections';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R94_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R94_build_report.json').write_text(json.dumps(r,indent=2));print('R94 saved',len(made))
