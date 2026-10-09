from pathlib import Path
import bpy,bmesh,json,sys,hashlib,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(Path(__file__).parent));from roof_panel_math import inset
P=json.loads((B/'config/reading_lantern_finish.json').read_text());version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R47_OKUMA_ISIKLIGI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));col=bpy.data.collections.new('R47_READING_LANTERN_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(col);glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R14_DARK_COATED_FRAME_CANDIDATE'];made=[];panels=[];changed=[];edges={};facetrows=[];center=Vector(json.loads((B/'reports/R08_build_report.json').read_text())['center_world'])
def mesh(name,verts,faces,mat,kind,parent=''):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in verts],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat);ob['element_id']=name;ob['element_type']=kind;ob['parent_facet']=parent;ob['source_ids']=','.join(P['source_ids']);ob['parameter_ids']='reading_lantern_finish.json';ob['status']='conditional_exterior_lantern';ob['confidence_detail']='D candidate profile and panel count';ob['assumption_note']='Inherited exterior shape not independently verified by square interior aperture';made.append(name);return ob
def solid(name,poly,normal,depth,mat,kind,parent=''):
 n=len(poly);return mesh(name,poly+[p-normal*depth for p in poly],[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,kind,parent)
legacy=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('P17_READING_SLOPE_','P17_READING_LANTERN_','P17_READING_CAP_')) and not o.hide_render];assert len(legacy)==24
E=json.loads((B/'config/entry_package.json').read_text())['reading_lantern'];C=json.loads((B/'config/foundation.json').read_text())['calibration'];M=C['pdf_to_utm_matrix'];ex=Vector((M[0][0],M[1][0],0)).normalized();ey=Vector((M[0][1],M[1][1],0)).normalized();sc=C['meters_per_canonical_pixel'];up=Vector((0,0,1))
def ring(rad,n,phase,z):return [center+(ex*math.cos(phase+i*math.tau/n)+ey*math.sin(phase+i*math.tau/n))*rad*sc+up*z for i in range(n)]
outer=ring(E['outer_radius_canonical'],8,math.pi/8,E['curb_top']);inner=ring(E['inner_radius_canonical'],4,0,E['shoulder']);top=ring(E['inner_radius_canonical'],4,0,E['lantern_top']);apex=center+up*E['apex'];sources=[]
apron=metal.copy();apron.name='R47_OPAQUE_APRON_APPEARANCE_CANDIDATE';apron.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.55;apron['source_ids']='116';apron['specification']='Opaque skirt observed; metal type and build-up unverified'
for i in range(8):
 j=(i+1)%8;k=i//2;points=[outer[i],outer[j],inner[(k+1)%4],inner[k]] if i%2==0 else [outer[i],outer[j],inner[(k+1)%4]];sources.append(dict(name=f'READING_SLOPE_{i}',points=points,opaque=True))
for i in range(4):
 j=(i+1)%4;sources.append(dict(name=f'READING_LANTERN_{i}',points=[inner[i],inner[j],top[j],top[i]],opaque=False));sources.append(dict(name=f'READING_CAP_{i}',points=[top[i],top[j],apex],opaque=False))
for src in sources:
 name=src['name'];points=src['points'];o=points[0];u=(points[1]-o).normalized();normal=(points[1]-o).cross(points[2]-o).normalized();cent=sum(points,Vector())/len(points)
 if 'LANTERN' in name:
  if normal.dot(Vector((cent.x-center.x,cent.y-center.y,0)))<0:normal=-normal
 elif normal.z<0:normal=-normal
 v=normal.cross(u).normalized();dev=max(abs((p-o).dot(normal)) for p in points);assert dev<.00001,(name,dev)
 count=P['shaft_columns_per_facet_candidate'] if 'LANTERN' in name else 1;cells=[]
 for i in range(count):
  cell=[points[0].lerp(points[1],i/count),points[0].lerp(points[1],(i+1)/count),points[3].lerp(points[2],(i+1)/count),points[3].lerp(points[2],i/count)] if count>1 else points;coords=[[(p-o).dot(u),(p-o).dot(v)] for p in cell];small=inset(coords,P['glass_edge_inset_m']);assert len(small)>=3;poly=[o+u*a+v*b for a,b in small];panelname=f'R47_{name}_'+('APRON' if src['opaque'] else 'GLASS')+f'_{i}';material=apron if src['opaque'] else glass;solid(panelname,poly,normal,P['glass_thickness_m'],material,'opaque_apron_envelope' if src['opaque'] else 'separate_lantern_glass_panel',name);panels.append(panelname);cells.append(dict(name=panelname,source_polygon=[list(p) for p in cell],normal=list(normal),opaque=src['opaque']))
  for a,b in zip(cell,cell[1:]+cell[:1]):
   key=tuple(sorted(tuple(round(q,5) for q in p) for p in [a,b]));entry=edges.setdefault(key,dict(a=a.copy(),b=b.copy(),normals=[],parents=[]));entry['normals'].append(normal.copy());entry['parents'].append(name)
 facetrows.append(dict(source=name,plane_error_m=dev,cells=cells))
for src in legacy:src.hide_render=True;src.hide_set(True);src['status']='superseded_R47_source116_four_sided_lantern';changed.append(src.name)
frame_rows=[]
for i,e in enumerate(edges.values()):
 a,b=e['a'],e['b'];n=sum(e['normals'],Vector()).normalized();side=n.cross((b-a).normalized()).normalized()*P['frame_width_m']/2;lift=n*P['frame_cap_above_glass_m'];name=f'R47_LANTERN_FRAME_{i:03}';solid(name,[a-side+lift,b-side+lift,b+side+lift,a+side+lift],n,P['frame_depth_m'],metal,'dark_frame_envelope',','.join(e['parents']));frame_rows.append(dict(name=name,start=list(a),end=list(b),parents=e['parents']))
roof=bpy.data.objects['P05_MAIN_ROOF_DECK'];roof.data=roof.data.copy();mat=bpy.data.materials.new('R47_DARK_ROOF_APPEARANCE_CANDIDATE');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=P['flat_roof_base_color_linear'];bs.inputs['Roughness'].default_value=P['flat_roof_roughness'];mat['source_ids']='116';mat['specification']='Unclassified dark roof finish; no hidden build-up';slot=len(roof.data.materials);roof.data.materials.append(mat);top=[];nm=roof.matrix_world.to_3x3().inverted().transposed()
for f in roof.data.polygons:
 if (nm@f.normal).normalized().z>.95:f.material_index=slot;top.append(f.index)
assert top;changed.append(roof.name);bpy.context.scene['stage']='R47 reading lantern frames and dark roof appearance';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R47_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=changed,panels=panels,source_objects_superseded=[o.name for o in legacy],profile_topology="octagonal opaque apron / square glass shaft and cap",facets=facetrows,frames=frame_rows,roof_top_faces=top,roof_material=mat.name,construction_acceptance=False);(B/'reports/R47_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');m=json.loads((B/'references/source_manifest.json').read_text(encoding='utf8'));sources=[x for x in m if x['id'] in P['source_ids']]
for x in sources:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
(B/'reports/R47_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=P['limits']),ensure_ascii=False,indent=2),encoding='utf8');print('R47',len(made),'panels',len(panels))
