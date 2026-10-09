"""R51: four wide roof facets visibly shaded in source028; clear strips retained."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(Path(__file__).parent));from roof_panel_math import clip,inset,area
P=json.loads((B/'config/main_roof_shading.json').read_text());version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R51_ANA_CATI_GOLGELIK_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('R51_MAIN_ROOF_SHADING_CANDIDATE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];rows=[];facets=[]
mat=bpy.data.materials['R42_SHADING_METAL_CANDIDATE'].copy();mat.name='R51_MAIN_ROOF_SHADING_CANDIDATE';mat['source_ids']='028,029';mat['status']='unmeasured_lamella_finish'
for fi in [1,3,5,7]:
 src=bpy.data.objects[f'P06_MAIN_ROOF_FACE_{fi}'];pts=[src.matrix_world@v.co for v in src.data.vertices];origin=pts[0];normal=(pts[1]-origin).cross(pts[2]-origin).normalized()
 if normal.z<0:normal=-normal
 u=Vector((0,0,1)).cross(normal).normalized();v=normal.cross(u).normalized();angle=math.radians(P['slat_angle_deg']);slat_v=v*math.cos(angle)+normal*math.sin(angle);slat_n=u.cross(slat_v).normalized();prefix=f'P10_MAIN_ROOF_FACE_{fi}_GLASS_';parents=[o for o in bpy.context.scene.objects if o.name.startswith(prefix) and not o.hide_render];assert parents;facets.append(dict(index=fi,source=src.name,origin=list(origin),u=list(u),v=list(v),normal=list(normal),panels=len(parents)))
 for parent in parents:
  n=len(parent.data.vertices)//2;world=[parent.matrix_world@p.co for p in list(parent.data.vertices)[:n]];poly=[[(p-origin).dot(u),(p-origin).dot(v)] for p in world];inner=inset(poly,P['perimeter_clearance_m'])
  if len(inner)<3:continue
  ymin=min(p[1] for p in inner);ymax=max(p[1] for p in inner);verts=[];faces=[];slats=[]
  for i in range(math.ceil(ymin/P['pitch_m']),math.floor(ymax/P['pitch_m'])+1):
   cy=i*P['pitch_m'];hw=P['slat_width_m']/2;shape=clip(clip(inner,1,cy-hw,1),1,cy+hw,-1)
   if len(shape)<3 or area(shape)<.0001:continue
   clean=[]
   for p in shape:
    if not clean or math.dist(p,clean[-1])>1e-5:clean.append(p)
   if len(clean)>2 and math.dist(clean[0],clean[-1])<1e-5:clean.pop()
   if len(clean)<3:continue
   top=[origin+u*x+v*cy+slat_v*(y-cy)-normal*P['glass_offset_m'] for x,y in clean];cnt=len(top);start=len(verts);verts += [tuple(p) for p in top]+[tuple(p-slat_n*P['slat_thickness_m']) for p in top];local=[tuple(range(cnt)),tuple(range(2*cnt-1,cnt-1,-1))]+[(j,(j+1)%cnt,(j+1)%cnt+cnt,j+cnt) for j in range(cnt)];faces += [tuple(start+k for k in f) for f in local];slats.append(dict(index=i,vertex_start=start,vertex_count=cnt*2))
  if not verts:continue
  name='R51_SHADE_'+parent.name.removeprefix('P10_MAIN_ROOF_FACE_');me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
  for k,value in dict(element_id=name,element_type='roof_shading_array_candidate',source_ids=','.join(P['source_ids']),parent_glass=parent.name,zone_id='GRAND_HALL_ROOF',level_id='ROOF',status='source_supported_extent_unmeasured_module',confidence_detail='C four shaded broad facets and clear narrow strips; D pitch profile angle mounts',assumption_note='028 shows shading on all four main wide roof facets. Module, thickness, offset and operating angle are candidates; no concealed actuation or fabrication claims.').items():ob[k]=value
  made.append(name);rows.append(dict(name=name,parent_glass=parent.name,facet=fi,slats=slats,slat_count=len(slats)))
S=bpy.context.scene;S['stage']='R51 main roof four shaded facets with clear narrow strips';S['current_file']=out.name;bpy.data.texts.new('R51_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=[],shading_arrays=rows,facets=facets,slat_count=sum(x['slat_count'] for x in rows),construction_acceptance=False);(B/'reports/R51_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');manifest=json.loads((B/'references/source_manifest.json').read_text());sources=[x for x in manifest if x['id'] in P['source_ids']]
for x in sources:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
(B/'reports/R51_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=P['limits']),ensure_ascii=False,indent=2),encoding='utf8');print('R51',len(made),'arrays',report['slat_count'],'slats')
