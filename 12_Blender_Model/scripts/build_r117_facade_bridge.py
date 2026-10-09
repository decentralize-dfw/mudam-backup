from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
B=Path(__file__).resolve().parents[1];R=B.parent;C=json.loads((B/'config/foundation.json').read_text())['calibration'];base=json.loads((B/'reports/R116_build_report.json').read_text());out=B/'scenes/MUDAM_R117_CEPHE_KOSE_KOPRU_BIRLESIM_v004.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/base['file']))
UP=4.8590748;LOW=-5.3262935;Z=Vector((0,0,1));made=[];changed=set();ops=[];root=bpy.data.collections.new('R117_FACADE_AND_BRIDGE_CONTINUITY');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);stone=bpy.data.materials['P05_NEUTRAL_ENVELOPE'];white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE']
def pt(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def native(x,y):
 s,dx,dy=C['basement_registration']['source_to_canonical'];return [s*x+dx,s*y+dy]
def prism(name,poly,z0,z1,mat=stone,issue=''):
 ps=[pt(*p) for p in poly];n=len(ps);lookup={tuple(p):i for i,p in enumerate(ps)}
 def ix(v):return v if isinstance(v,int) else lookup[tuple(v)]
 tri=tessellate_polygon([ps]);fs=[tuple(ix(v) for v in reversed(t)) for t in tri]+[tuple(ix(v)+n for v in t) for t in tri]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata([p+Z*z for z in [z0,z1] for p in ps],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type='marked_architectural_boundary_repair',issue_id=issue,source_ids='102,103,104,user_20261010_SS1_SS8',status='user_corrected_boundary_candidate_dimensions',assumption_note='User-marked boundary correction on existing registered plan. Existing elevations retained; hidden construction and precise dimensions not surveyed.').items():o[k]=v
 made.append(name);return o
def rect(name,x0,x1,y0,y1,z0,z1,mat=stone,issue=''):return prism(name,[[x0,y0],[x1,y0],[x1,y1],[x0,y1]],z0,z1,mat,issue)
def uvrect(name,u0,u1,v0,v1,z0,z1,mat=stone,issue=''):return prism(name,[[(u+v)/2,(u-v)/2] for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]],z0,z1,mat,issue)
def hide(name,issue):
 o=bpy.data.objects[name];o.hide_render=True;o.hide_set(True);o['R117_issue']=issue;changed.add(name);ops.append(dict(name=name,operation='supersede',issue=issue))
def bake(o):
 deps=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps);o.modifiers.clear();o.data=me

def volume(o):
 bm=bmesh.new();bm.from_mesh(o.data);v=abs(bm.calc_volume());bm.free();return v

def boolean(o,cut,operation,issue):
 bake(o);old=o.data.copy();before=volume(o);bpy.context.view_layer.objects.active=o;m=o.modifiers.new('R117 '+issue,'BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);after=volume(o)
 if abs(before-after)<1e-7:o.data=old;return
 changed.add(o.name);ops.append(dict(name=o.name,operation=operation,issue=issue,before_volume=before,after_volume=after));o['R117_issue']=issue
 if after<1e-8:o.hide_render=True;o.hide_set(True)
def drop(o):
 made.remove(o.name);bpy.data.objects.remove(o,do_unlink=True)

wr=json.loads((B/'reports/R54_build_report.json').read_text());wp=json.loads((B/'config/lower_windows_wall_relative.json').read_text());origin=Vector(wr['origin']);axis=Vector(wr['axis']);inside=Vector(wr['inside'])
corner=bpy.data.objects['R27_BAY_1_END_RETURN'];corner_end=max((corner.matrix_world@v.co-origin).dot(axis) for v in corner.data.vertices);first=corner_end+.12+wp['outer_width_m']/2;delta=first-wp['centers_along_wall_m'][0];oldcenters=wp['centers_along_wall_m'];wp['centers_along_wall_m']=[x+delta for x in oldcenters]
for o in list(bpy.data.objects):
 if o.name.startswith('R54_WINDOW_'):
  o.location+=axis*delta;changed.add(o.name);o['R117_note']='004/116 photo-supported correction: retain five-window rhythm while placing first reveal fully inside modern facade corner. Offset remains a model-derived registration candidate.'
# Restore the pre-window masonry mesh, then cut all relocated reveals.
wall=bpy.data.objects['R35_WALL_51946353_00_0'];mats=list(wall.data.materials);source=json.loads((B/'reports/R35_build_report.json').read_text())['file']
with bpy.data.libraries.load(str(R/source),link=False) as (src,dst):dst.objects=[wall.name]
old=dst.objects[0];wall.data=old.data.copy();wall.modifiers.clear();wall.data.materials.clear()
for m in mats:wall.data.materials.append(m)
mi=next((i for i,m in enumerate(mats) if m.name.startswith('R55_HISTORIC_MASONRY')),0)
for f in wall.data.polygons:f.material_index=mi
bpy.data.objects.remove(old,do_unlink=True);changed.add(wall.name)
for i in range(1,6):boolean(wall,bpy.data.objects[f'R54_WINDOW_{i:02d}_HISTORIC_CUTTER'],'DIFFERENCE','five relocated historic notches')
# Preserve metric masonry UV scale on rebuilt faces.
uv=wall.data.uv_layers.get('R55_CONTEXT_METRIC_UV') or wall.data.uv_layers.new(name='R55_CONTEXT_METRIC_UV');wall.data.uv_layers.active=uv
for f in wall.data.polygons:
 n=f.normal;u=Z.cross(n).normalized() if abs(n.z)<.95 else Vector((1,0,0));u=-u if u.x<-.00001 else u;v=n.cross(u).normalized()
 for li in f.loop_indices:
  q=wall.data.vertices[wall.data.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/4,q.dot(v)/3)
# Rebuild the backing with an exact shared grid; no duplicate window-head faces.
back=bpy.data.objects['R116_LOWER_FACADE_BACKING'];coords=[back.matrix_world@v.co for v in back.data.vertices];t0=min((q-origin).dot(axis) for q in coords);t1=max((q-origin).dot(axis) for q in coords)
ticks=sorted([t0,t1]+[t+v*wp['inner_width_m']/2 for t in wp['centers_along_wall_m'] for v in [-1,1]]);zs=[LOW,wp['inner_sill_z'],wp['glass_head_z'],-.8];cells=set()
for i in range(len(ticks)-1):
 for j in range(3):
  mid=(ticks[i]+ticks[i+1])/2
  if j==1 and any(abs(mid-t)<wp['inner_width_m']/2 for t in wp['centers_along_wall_m']):continue
  cells.add((i,j))
verts=[];faces=[];lookup={}
def vi(t,d,z):
 key=(round(t,8),d,z)
 if key not in lookup:lookup[key]=len(verts);verts.append(origin+axis*t+inside*d+Z*z)
 return lookup[key]
for i,j in cells:
 aa,bb=ticks[i:i+2];lo,hi=zs[j:j+2];q=[vi(t,d,z) for d in [.65,1.0] for t,z in [(aa,lo),(bb,lo),(bb,hi),(aa,hi)]];faces.extend([tuple(q[k] for k in [0,3,2,1]),tuple(q[k] for k in [4,5,6,7])])
 for neighbor,ids in [((i-1,j),[0,4,7,3]),((i+1,j),[1,2,6,5]),((i,j-1),[0,1,5,4]),((i,j+1),[3,7,6,2])]:
  if neighbor not in cells:faces.append(tuple(q[k] for k in ids))
me=bpy.data.meshes.new('R117_LOWER_BACKING_GRID');me.from_pydata(verts,[],faces);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(stone);back.data=me;changed.add(back.name)
# Restore the original full-depth modern corner below the retired R27 lower band.
with bpy.data.libraries.load(str(B/'scenes/MUDAM_R27_GALERI_NIS_REVIZYON_v001.blend'),link=False) as (src,dst):dst.objects=['R27_BAY_1_END_RETURN']
ret=dst.objects[0];ret.name='R117_LOWER_FACADE_CORNER_RETURN';root.objects.link(ret);ret.data=ret.data.copy();ret.data.materials.clear();ret.data.materials.append(stone)
for v in ret.data.vertices:
 q=ret.matrix_world@v.co;q.z=min(q.z,-.8);v.co=ret.matrix_world.inverted()@q
ret['source_ids']='004,116,R27';ret['assumption_note']='Original R27 corner footprint restored below facade band, clipped against historic masonry. Existing candidate dimensions retained.';made.append(ret.name)
boolean(ret,wall,'DIFFERENCE','lower corner joins historic masonry without overlap')
boolean(ret,back,'DIFFERENCE','lower corner backing contact')
changed.discard(ret.name)
# Join the source103 bridge to the actual gallery slab ends. Existing stair opening untouched.
rect('R117_E_BRIDGE_FLOOR_JOIN',457.87825,465,555,598,UP-.2,UP,stone,'SS6 bridge east floor seam')
prism('R117_W_BRIDGE_FLOOR_JOIN',[[689,555],[694.19483,555],[694.19483,595.58261],[696.5778,598],[689,598]],UP-.2,UP,stone,'SS6 bridge west floor seam')
rect('R117_E_BRIDGE_WALL_END',457.87825,465,555.5,558,UP,12.523118,stone,'SS6 wall end contact')
r=dict(file=out.relative_to(R).as_posix(),base_scene=Path(base['file']).name,closed_objects=made,changed_inherited_objects=sorted(changed),operations=ops,old_centers=oldcenters,new_centers=wp['centers_along_wall_m'],window_translation_m=delta,corner_end_m=corner_end,corner_clearance_m=.12,construction_acceptance=False,visual_acceptance=False,limits=['004 and116 support five reveals fully within modern facade. Existing rhythm retained; translation derives from existing corner, not a surveyed absolute location.','Bridge join closes source103 continuous circulation band to existing gallery slabs; inherited level retained.'])
bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R117_build_report.json').write_text(json.dumps(r,indent=2));print('R117',len(changed),len(made),'shift',delta)
