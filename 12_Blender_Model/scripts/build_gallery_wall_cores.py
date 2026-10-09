"""R73 combine disconnected inner/outer gallery wall leaves into source-bounded envelopes."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R72_ATRIUM_DUVAR_SUREKLILIGI_v004.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R73_GALERI_DUVAR_GOVDELERI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));root=bpy.data.collections.new('R73_GALLERY_CONTINUOUS_WALLS');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];definitions=[]
def hull(points):
 pts=sorted(set((round(p.x,6),round(p.y,6)) for p in points))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 lower=[];upper=[]
 for p in pts:
  while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=1e-7:lower.pop()
  lower.append(p)
 for p in reversed(pts):
  while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=1e-7:upper.pop()
  upper.append(p)
 return lower[:-1]+upper[:-1]
for side,index in [('E',2),('W',5)]:
 names=[f'R28_{side}_HIGH_GALLERY_WALL',f'R23_{side}_{index}_WALL'];outer,inner=[bpy.data.objects[n] for n in names];world=[[o.matrix_world@v.co for v in o.data.vertices] for o in [outer,inner]];poly=hull(world[0]+world[1]);z0=min(v.z for v in world[0]);z1=max(v.z for v in world[0]);n=len(poly);vs=[(x,y,z) for z in [z0,z1] for x,y in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 name=f'R73_{side}_CONTINUOUS_GALLERY_WALL';me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o)
 for mat in [outer.data.materials[0],inner.data.materials[0]]:me.materials.append(mat)
 # Keep the inherited gallery-facing white surface and the outer stone family.
 a,b=world[1][0],world[1][1];axis=(b-a).normalized();normal=axis.cross(Vector((0,0,1)))
 for f in me.polygons:
  if abs(f.normal.z)<.1 and abs((f.center-a).dot(normal))<.02:f.material_index=1
 for key,value in dict(element_id=name,element_type='continuous_gallery_wall_envelope_candidate',source_ids='102,103,PDF2016,026,032,034,041,116',level_id='MULTI',zone_id='GALLERY_'+side,status='conditional_inner_outer_source_envelope',assumption_note='R73 joins existing room-side and hall-side boundaries; variable core width is model-derived, not surveyed structural thickness. No portal is inferred or closed.').items():o[key]=value
 cut_definition=None
 if side=='E':
  portal=json.loads((B/'reports/R02_build_report.json').read_text());pa,pb=map(Vector,portal['portal_endpoints']);normal=Vector(portal['normal']);cp=[pa-normal*.65,pb-normal*.65,pb+normal*.65,pa+normal*.65];low=-.1;high=portal['upper_head'];cm=bpy.data.meshes.new('R73_SOURCE_PORTAL_CUT');cm.from_pydata([(p.x,p.y,z) for z in [low,high] for p in cp],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);cm.update();bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cm);bm.free();cut=bpy.data.objects.new(cm.name,cm);root.objects.link(cut);cut.hide_render=True;cut.hide_set(True);cut['element_type']='hidden_existing_portal_clearance';mod=o.modifiers.new('R73 retain R02 source passage','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);cut_definition=dict(polygon_world=[[p.x,p.y] for p in cp],z0=low,z1=high)
 for old in [outer,inner]:old.hide_render=True;old.hide_set(True);changed.append(old.name)
 definitions.append(dict(name=name,replaced=names,polygon_world=poly,z0=z0,z1=z1,old_world_vertices={n:[list(v) for v in pts] for n,pts in zip(names,world)},inner_front=[list(a),list(b)],preserved_portal_cut=cut_definition));made.append(name)
report=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=changed,definitions=definitions,construction_acceptance=False,limits=['Existing inner and outer footprint references are retained; the connecting volume is conditional.','Invisible wall build-up, structural composition and fire/acoustic specification are unknown.','Other side-hall wall ends and glazed portal alignment remain separate checks.'])
bpy.context.scene['stage']='R73 continuous upper gallery wall bodies';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R73_SOURCE_AND_LIMITS').write(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R73_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R73',made)
