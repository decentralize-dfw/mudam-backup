"""R42 photo026/049 lamellae, only at the identified down-stair roof facet."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(Path(__file__).parent));from roof_panel_math import clip,inset,area
P=json.loads((B/'config/roof_shading.json').read_text());version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R42_CATI_GUNES_KIRICI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P10_GH_DOWN_STAIR_SHADING_CANDIDATE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);src=bpy.data.objects[P['source_roof']];pts=[src.matrix_world@v.co for v in src.data.vertices];origin=pts[0];normal=(pts[1]-origin).cross(pts[2]-origin).normalized()
if normal.z<0:normal=-normal
u=Vector((0,0,1)).cross(normal).normalized();v=normal.cross(u).normalized();angle=math.radians(P['slat_angle_deg']);slat_v=v*math.cos(angle)+normal*math.sin(angle);slat_n=u.cross(slat_v).normalized();made=[];rows=[]
mat=bpy.data.materials.new('R42_SHADING_METAL_CANDIDATE');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.23,.25,.24,1);bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.38;mat['source_ids']='026,049';mat['status']='uncalibrated_shading_appearance'
parents=[o for o in bpy.context.scene.objects if o.name.startswith(P['panel_prefix']) and o.get('element_type')=='glass_panel' and not o.hide_render]
for parent in parents:
 n=len(parent.data.vertices)//2;world=[parent.matrix_world@p.co for p in list(parent.data.vertices)[:n]];poly=[[(p-origin).dot(u),(p-origin).dot(v)] for p in world];inner=inset(poly,P['perimeter_clearance_m'])
 if len(inner)<3:continue
 ymin=min(p[1] for p in inner);ymax=max(p[1] for p in inner);verts=[];faces=[];slats=[]
 for i in range(math.ceil(ymin/P['pitch_m']),math.floor(ymax/P['pitch_m'])+1):
  cy=i*P['pitch_m'];hw=P['slat_width_m']/2;shape=clip(clip(inner,1,cy-hw,1),1,cy+hw,-1)
  # Remove tiny clipped end slivers before float32 mesh storage.
  if len(shape)<3 or area(shape)<.0001:continue
  clean=[]
  for p in shape:
   if not clean or math.dist(p,clean[-1])>1e-5:clean.append(p)
  if len(clean)>2 and math.dist(clean[0],clean[-1])<1e-5:clean.pop()
  if len(clean)<3:continue
  shape=clean;top=[origin+u*x+v*cy+slat_v*(y-cy)-normal*P['glass_offset_m'] for x,y in shape];cnt=len(top);start=len(verts);verts += [tuple(p) for p in top]+[tuple(p-slat_n*P['slat_thickness_m']) for p in top];local=[tuple(range(cnt)),tuple(range(2*cnt-1,cnt-1,-1))]+[(j,(j+1)%cnt,(j+1)%cnt+cnt,j+cnt) for j in range(cnt)];faces += [tuple(start+k for k in f) for f in local];slats.append(dict(index=i,vertex_start=start,vertex_count=cnt*2))
 if not verts:continue
 name='R42_SHADE_'+parent.name.removeprefix(P['panel_prefix']);me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,value in dict(element_id=name,element_type='shading_slat_array_candidate',source_ids=','.join(P['source_ids']),parent_glass=parent.name,zone_id='GH_DOWN_STAIR_ROOF',level_id='ROOF',status='conditional_shading_family',confidence_xy='C existing roof / D slat layout',confidence_detail='D unmeasured',assumption_note='026/049 support lamellae; pitch/angle/count/offset candidates. Hidden mounting and operation not inferred.').items():ob[k]=value
 made.append(name);rows.append(dict(name=name,parent_glass=parent.name,slats=slats,slat_count=len(slats)))
assert len(made)>10
bpy.context.scene['stage']='R42 down-stair roof shading study';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R42_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R42_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=[],shading_arrays=rows,slat_count=sum(q['slat_count'] for q in rows),roof_origin=list(origin),u=list(u),v=list(v),normal=list(normal),construction_acceptance=False),indent=2),encoding='utf8');print('R42',len(made),sum(q['slat_count'] for q in rows))
