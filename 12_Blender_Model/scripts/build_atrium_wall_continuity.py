"""R72: reconcile inherited inner wall and later roof perimeter, and close basement north boundary."""
from pathlib import Path
import bpy,bmesh,json,sys,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';C=json.loads((B/'config/foundation.json').read_text())['calibration'];Q=json.loads((B/'config/roof_revision.json').read_text())
base='MUDAM_R71_GALERI_DUVAR_BIRLESIMLERI_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R72_ATRIUM_DUVAR_SUREKLILIGI_{version}.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));root=bpy.data.collections.new('R72_ATRIUM_WALL_CONTINUITY');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
made=[];changed=[];definitions=[];up=Vector((0,0,1));LOW=json.loads((B/'reports/R05_build_report.json').read_text())['lower_z'];H=min(Q['eave_z']);JOIN=H-1.4
def point(p,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*p[0]+ox;b=k*p[1]+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def prism(name,poly,z0,z1,mat,level):
 tops=[z1]*len(poly)
 if 'HIGH_ATRIUM' in name:
  trees=[]
  for ob in bpy.context.scene.objects:
   if ob.name.startswith('P06_MAIN_ROOF_FACE_'):
    trees.append(BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(f.vertices) for f in ob.data.polygons]))
  for i,p in enumerate(poly):
   hits=[hit[0].z for tree in trees if (hit:=tree.ray_cast(point(p,0),up,40))[0] is not None]
   if hits:tops[i]=min(z1,min(hits))
 pts=[point(p,z0) for p in poly]+[point(p,z) for p,z in zip(poly,tops)];n=len(poly);me=bpy.data.meshes.new(name);me.from_pydata(pts,[],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type='continuous_atrium_wall_candidate',zone_id='GRAND_HALL',level_id=level,source_ids='102,103,104,101,026,087,114,116,119',status='source_boundary_continuity_candidate',confidence_xy='C existing source perimeter; D wall thickness reconciliation',confidence_z='D inherited section heights',assumption_note='R72 closes model discontinuity between existing envelopes. Thickness and height are candidates, not measured construction.').items():o[k]=v
 made.append(name);definitions.append(dict(name=name,polygon_canonical=poly,z0=z0,z1=z1,top_heights=tops));return o
stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE']
# 104 shows a continuous north boundary to the lower foyer. Existing north
# stair wall already covers x592..688. Extend the E base and slot backing down
# to the inherited LM1 datum, meeting the registered east divider footprint.
poly=[[462,335.2626613],[592,335.2626613],[592,331.4746773],[462,331.4746773]]
prism('R72_LOWER_FOYER_NORTH_WALL',poly,LOW,0,stone,'LM1')
# P05 inner diagonal planes are x+y=1145 and y-x=-5. P06 roof wall edges
# moved seven canonical pixels. Model both faces as ONE wall envelope instead
# of leaving two disconnected 120mm strips. Section at JOIN meets roof slab.
old=[(565,334),(585,334),(688,437),(688,457),(585,560),(565,560),(462,457),(462,437)]
for i in [3,5]:
 j=i+1;inner=[list(old[i]),list(old[j])]
 # R44 extruded face 5 inward, whereas face 3 was extruded outward.
 # Include that inherited 120mm back so the lower/upper wall contact has area.
 if i==5:
  d=.12/(C['meters_per_canonical_pixel']*2**.5)
  inner=[[565+2*d,560],[462,457-2*d]]
 poly=inner+[Q['outer_canonical'][j],Q['outer_canonical'][i]]
 prism(f'R72_HIGH_ATRIUM_WALL_{i}',poly,JOIN,Q['eave_z'][i],stone,'MULTI')
 ob=bpy.data.objects[f'P06_HIGH_EAVE_UPSTAND_{i}'];ob.hide_render=True;ob.hide_set(True);changed.append(ob.name)
# Retain all inherited lower openings; trim only the superseded upper strip.
trim=[o for o in bpy.context.scene.objects if o.name=='P05_MAIN_ATRIUM_BASE_3' or o.name.startswith('P05_MAIN_ATRIUM_BASE_5') or o.name=='R33_MAIN_PASSAGE_HIGH_REMAINDER']
trimmed=[]
for o in trim:
 if o.hide_render:continue
 o.data=o.data.copy();inv=o.matrix_world.inverted();count=0
 for v in o.data.vertices:
  w=o.matrix_world@v.co
  if w.z>JOIN+1e-5:w.z=JOIN;v.co=inv@w;count+=1
 if count:o.data.update();o['wall_continuity_revision']='R72 top strip replaced by continuous inner-to-roof envelope';changed.append(o.name);trimmed.append(dict(name=o.name,changed_top_vertices=count,top_z=JOIN))
# Central strip is GLASS in 116, not a stone closure. Continue its existing
# material/plane down to the roof slab; keep its detailed framing for later.
o=bpy.data.objects['P06_HIGH_EAVE_UPSTAND_4'];o.data=o.data.copy();inv=o.matrix_world.inverted()
for v in o.data.vertices:
 w=o.matrix_world@v.co
 if abs(w.z-H)<1e-4:w.z=JOIN;v.co=inv@w
o.data.update();changed.append(o.name)
report=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made+changed,changed_inherited_objects=changed,definitions=definitions,trimmed_lower_walls=trimmed,join_z=JOIN,old_join_z=H,lower_z=LOW,construction_acceptance=False,limits=['North basement wall follows 104 topology; unseen retaining assembly and precise thickness remain unknown.','High wall thickness bridges existing P05/P06 source-envelope discrepancy (about 0.588m); not an independently measured wall section.','Central strip remains glass. Window framing and complete roof-to-wall weathering remain subsequent tasks.','User-marked side-hall junctions and other wall systems remain under audit.'])
bpy.context.scene['stage']='R72 atrium wall continuity candidates';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R72_SOURCE_AND_LIMITS').write(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R72_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['102','103','104','101','026','087','114','116','119']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R72_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=report['limits']),indent=2),encoding='utf8');print('R72',len(made),'new walls;',len(changed),'inherited changes')
