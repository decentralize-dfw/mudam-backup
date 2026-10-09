"""R83 roof support boundary omissions, traced against093/102/026/116."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R82_BATI_MERDIVEN_GIRIS_KABUK_v001.blend';out=B/'scenes/MUDAM_R83_CATI_KENAR_KAPANISLARI_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));C=json.loads((B/'config/foundation.json').read_text())['calibration'];Q=json.loads((B/'config/roof_revision.json').read_text());up=Vector((0,0,1));root=bpy.data.collections.new('R83_ROOF_BOUNDARY_CLOSURES');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];definitions=[];stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R14_DARK_COATED_FRAME_CANDIDATE']
def point(p,z=0):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def solid(name,ps,n,depth,mat,kind):
 N=len(ps);me=bpy.data.meshes.new(name);me.from_pydata([tuple(p) for p in ps]+[tuple(p-n*depth) for p in ps],[],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='ROOF_SUPPORT',level_id='MULTI',source_ids='093,102,026,116,101',status='conditional_source_enclosure',confidence_xy='C established source footprint',confidence_z='D existing section/photo roof heights',assumption_note='Closes omitted envelope faces at existing boundaries; no roof geometry or measured dimensions inferred.').items():ob[k]=v
 made.append(name);return ob
# Straight stone wall behind the curved cafe roof, visible in093. Ground stair opening retained.
a=point([688,432]);b=point([849,271]);c=point([862.5,257.5]);normal=(point([687,431])-a).normalized();H=min(Q['eave_z'])
for name,start,end,z0 in [('R83_CAFE_BACK_WALL',a,b,0),('R83_CAFE_ENTRY_HEAD',b,c,3.2)]:
 solid(name,[start+up*z0,end+up*z0,end+up*H,start+up*H],normal,.30,stone,'cafe_back_stone_wall_candidate');definitions.append(dict(name=name,a=list(start),b=list(end),z0=z0,z1=H))
# Facets2/6 rise between low and high eave. Their vertical triangular transitions were never closed.
triangles=[]
for i in [2,6]:
 j=(i+1)%8;pa=point(Q['outer_canonical'][i],Q['eave_z'][i]);pb=point(Q['outer_canonical'][j],Q['eave_z'][j]);low=min(Q['eave_z']);high=pa if pa.z>pb.z else pb;foot=Vector((high.x,high.y,low));ps=[pa,pb,foot];normal=(pa-point([575,447],pa.z));normal.z=0;normal=normal.normalized();axis=(pb-pa);normal=Vector((axis.y,-axis.x,0)).normalized()
 if normal.dot(pa-point([575,447],pa.z))<0:normal=-normal
 name=f'R83_ATRIUM_TRANSITION_GLASS_{i}';solid(name,ps,normal,.018,glass,'vertical_roof_transition_glass_candidate');triangles.append(dict(name=name,vertices=[list(p) for p in ps],normal=list(normal)))
 # Existing P10 sloping perimeter is retained; only missing bottom and vertical edge closures.
 for k,(aa,bb) in enumerate([(high,foot),(foot,pb if high==pa else pa)]):
  side=normal.cross((bb-aa).normalized())*.06;solid(f'R83_ATRIUM_TRANSITION_EDGE_{i}_{k}',[aa-side,bb-side,bb+side,aa+side],normal,.22,metal,'transition_edge_frame_candidate')
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=[],cafe_walls=definitions,transition_triangles=triangles,construction_acceptance=False,limits=['093 supports straight opaque wall behind cafe roof; registered102 line x+y=1120 retained.','Existing west stair entry remains open below3.2m; no door or hardware modeled.','093/026 show glazed transitions; triangular fills follow current2/6 roof-edge geometry without changing silhouette.','Exact transition subdivisions, wall thickness, roof heights and profile dimensions remain candidate, not measured.'])
bpy.context.scene['stage']='R83 cafe back wall and atrium transition closure';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R83_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R83_build_report.json').write_text(json.dumps(r,indent=2),encoding='utf8');print('R83',len(made),'closures')
