"""R103 trim three neighboring closures to existing source-facing gallery planes."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];P=json.loads((B/'config/upper_gallery_room.json').read_text());base=json.loads((B/'reports/R102_build_report.json').read_text());out=B/'scenes/MUDAM_R103_UST_GALERI_IC_YUZ_BIRLESIMLERI_v003.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B.parent/base['file']))
def pt(p):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
poly=list(map(pt,P['source_polygons_canonical']['W']));center=sum(poly,Vector())/len(poly);rows=[]
for name,edge in [('R85_RETURN_CEILING_0',0),('R85_RETURN_OUTER_TIP',1),('R96_DOCUMENTATION_GALLERY_JOIN',3)]:
 a=poly[edge];b=poly[(edge+1)%len(poly)];normal=(b-a).normalized().cross(Vector((0,0,1)))
 if normal.dot((a+b)/2-center)<0:normal=-normal
 ob=bpy.data.objects[name];before=[list(ob.matrix_world@v.co) for v in ob.data.vertices];ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world);before_volume=abs(bm.calc_volume(signed=True));before_z=[min(v.co.z for v in bm.verts),max(v.co.z for v in bm.verts)]
 # End inside the existing 250mm wall, avoiding coincident exposed finish faces.
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=a+normal*.005,plane_no=normal,clear_inner=True,clear_outer=False)
 borders=[e for e in bm.edges if e.is_boundary];bmesh.ops.holes_fill(bm,edges=borders,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));after_volume=abs(bm.calc_volume(signed=True));assert 0<after_volume<before_volume
 assert all(e.is_manifold for e in bm.edges);assert min((v.co-a).dot(normal) for v in bm.verts)>-2e-5
 bm.transform(ob.matrix_world.inverted());bm.to_mesh(ob.data);bm.free();ob['R103_note']='Neighboring closure trimmed at registered gallery inner face; gallery source walls and openings unchanged. No measured construction claim.'
 rows.append(dict(name=name,side='W',edge=edge,plane_point=list(a),outward=list(normal),before_world=before,before_z=before_z,volume_before=before_volume,volume_after=after_volume,removed_volume=before_volume-after_volume))
# The second return ceiling crosses two faces at the gallery corner. Subtract
# the actual room polygon, retaining BOTH legitimate outside corridor branches.
name='R85_RETURN_CEILING_1';ob=bpy.data.objects[name];before=[list(ob.matrix_world@v.co) for v in ob.data.vertices];ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world);before_volume=abs(bm.calc_volume(signed=True));before_z=[min(v.co.z for v in bm.verts),max(v.co.z for v in bm.verts)];bm.free()
def cross(a,b):return a.x*b.y-a.y*b.x
expanded=[]
for i,p in enumerate(poly):
 ax1=(p-poly[i-1]).normalized();ax2=(poly[(i+1)%len(poly)]-p).normalized();n1=ax1.cross(Vector((0,0,1)));n2=ax2.cross(Vector((0,0,1)))
 if n1.dot(p-center)<0:n1=-n1
 if n2.dot(p-center)<0:n2=-n2
 a=p+n1*.005;b=p+n2*.005;expanded.append(a+ax1*cross(b-a,ax2)/cross(ax1,ax2))
N=len(poly);verts=[(p.x,p.y,z) for z in [0,20] for p in expanded];faces=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
me=bpy.data.meshes.new('R103_TEMP_GALLERY_INTERIOR');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();cut=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(cut);bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('R103 remove gallery interior overlap','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.transform(ob.matrix_world);after_volume=abs(bm.calc_volume(signed=True));assert 0<after_volume<before_volume;assert all(e.is_manifold for e in bm.edges);bm.free();ob['R103_note']='Return ceiling outside gallery retained; overlap inside source gallery polygon removed.'
rows.append(dict(name=name,side='W',edges=[0,5],gallery_polygon=[list(p) for p in poly],before_world=before,before_z=before_z,volume_before=before_volume,volume_after=after_volume,removed_volume=before_volume-after_volume))
r=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(base['file']).name,closed_objects=[x['name'] for x in rows],changed_inherited_objects=[x['name'] for x in rows],trims=rows,hidden_overlap_offset_m=.005,construction_acceptance=False,limits=['Reconciles earlier approximate closure edges with existing PDF2016-derived gallery inner faces.','Trim endpoints terminate 5mm behind the retained 250mm gallery wall face to avoid duplicate coplanar finish surfaces; no exposed gap is introduced.','Source gallery footprints, door widths, wall heights and circulation retained; dimensions remain candidates.'])
bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R103 upper gallery inner face continuity';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R103_build_report.json').write_text(json.dumps(r,indent=2));print('R103',len(rows),'trimmed closures')
