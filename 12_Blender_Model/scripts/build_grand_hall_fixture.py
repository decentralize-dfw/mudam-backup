"""R50: 20 observed cylinders in four five-light crosses, source 028.

All physical sizes, elevation and hidden attachment details remain candidates.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
P=json.loads((B/'config/grand_hall_fixture.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R50_GRAND_HALL_ARMATUR_{version}.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;root=bpy.data.collections.new('R50_GH_LIGHT_FIXTURE_CANDIDATE');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
def point(p,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,z))
center=point(P['center_canonical']);ex=(point([576,447])-center).normalized();ey=(point([575,448])-center).normalized();up=Vector((0,0,1));made=[]
def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
grey=material('R50_GREY_HOUSING_CANDIDATE',(.32,.36,.35),.7,.32);dark=material('R50_DARK_RECESS_CANDIDATE',(.035,.043,.04),.35,.4);lens=material('R50_DIFFUSER_CANDIDATE',(.67,.66,.53),.05,.28)
def mesh(name,verts,faces,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,level_id='GH_HIGH_LEVEL',zone_id='GRAND_HALL',source_ids=','.join(P['source_ids']),status='photo_supported_topology_unmeasured_dimensions',confidence_detail='C observed 20-cylinder arrangement; D physical size and anchorage',parameter_ids='grand_hall_fixture.json',assumption_note='20 cylinders visible in 028. Dimensions, elevation, section, lens optics, suspension and connections are candidates; no manufacturer or photometric claim.').items():ob[k]=v
 made.append(name);return ob
def tube(name,a,b,diam,mat,kind,sides=24):
 t=(b-a).normalized();ref=up if abs(t.z)<.9 else ex;u=t.cross(ref).normalized()*diam/2;v=t.cross(u).normalized()*diam/2;ring=[u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides) for i in range(sides)];ob=mesh(name,[tuple(p+q) for p in [a,b] for q in ring],[tuple(range(sides-1,-1,-1)),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)],mat,kind)
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
def annulus(name,c,outer,inner,z0,z1,mat,kind):
 n=48;vs=[tuple(c+ex*(r*math.cos(i*math.tau/n))+ey*(r*math.sin(i*math.tau/n))+up*z) for r,z in [(outer,z0),(outer,z1),(inner,z0),(inner,z1)] for i in range(n)];fs=[]
 for i in range(n):
  j=(i+1)%n;fs += [(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)]
 ob=mesh(name,vs,fs,mat,kind)
 for f in ob.data.polygons:f.use_smooth=f.index%4<2
 return ob
pitch=P['module_m'];z=P['bottom_z'];height=P['housing_height_m'];ro=P['housing_diameter_m']/2;lights=[];groups=[]
for gi,(gx,gy) in enumerate([(0,-2),(2,0),(0,2),(-2,0)]):
 c=center+ex*(gx*pitch)+ey*(gy*pitch);groups.append(c);annulus(f'R50_GROUP_COLLAR_{gi}',c,.30,.276,z+.24,z+.29,grey,'fixture_group_collar_candidate')
 for li,(dx,dy) in enumerate([(0,0),(-1,0),(1,0),(0,-1),(0,1)]):
  p=c+ex*(dx*pitch)+ey*(dy*pitch);ident=f'{gi}_{li}';housing=annulus('R50_HOUSING_'+ident,p,ro,ro-.018,z,z+height,grey,'light_cylinder_housing');annulus('R50_RECESS_'+ident,p,ro-.019,ro*.58,z+.018,z+.095,dark,'light_recess_candidate');tube('R50_LENS_'+ident,p+up*(z+.092),p+up*(z+.103),ro*1.14,lens,'unmeasured_lens_disc',48);tube('R50_TOP_CAP_'+ident,p+up*(z+height-.014),p+up*(z+height),2*(ro-.018),grey,'housing_top_candidate',48)
  if li:tube('R50_GROUP_ARM_'+ident,c+up*(z+.27),p+up*(z+.27),.027,grey,'fixture_arm_candidate')
  lights.append(dict(group=gi,index=li,lattice=[gx+dx,gy+dy],center=list(p),housing=housing.name))
for gi,c in enumerate(groups):tube(f'R50_BACKFRAME_{gi}',c+up*(z+height*.75),groups[(gi+1)%4]+up*(z+height*.75),.035,grey,'fixture_backframe_candidate')
for gi in range(2):tube(f'R50_CROSSFRAME_{gi}',groups[gi]+up*(z+height*.75),groups[gi+2]+up*(z+height*.75),.035,grey,'fixture_crossframe_candidate')
# Attach at actual existing metal mesh vertices near inner roof corners.
# Geometric contact is verified; these are NOT identified real anchor locations.
frames=[o for o in S.objects if not o.hide_render and o.type=='MESH' and o.name.startswith('P10_MAIN_ROOF_FACE_') and '_EDGE_' in o.name];assert frames
anchors=[]
for i,(cx,cy) in enumerate([(558,427),(592,427),(592,467),(558,467)]):
 target=point([cx,cy],21.12 if cy==427 else 24.86);candidates=[((o.matrix_world@v.co-target).length,o,o.matrix_world@v.co) for o in frames for v in o.data.vertices];_,parent,q=min(candidates,key=lambda row:row[0]);p=center+ex*((-1 if cx<575 else 1)*pitch)+ey*((-1 if cy<447 else 1)*pitch)+up*(z+height*.75)
 tube(f'R50_SUSPENSION_{i}',p,q,.012,grey,'suspension_candidate',12);tube(f'R50_ATTACHMENT_{i}',q-up*.022,q+up*.022,.035,grey,'unresolved_attachment_envelope',16);anchors.append(dict(name=f'R50_SUSPENSION_{i}',start=list(p),end=list(q),parent=parent.name,parent_contact='existing mesh vertex; real fixing location unresolved'))
assert len(lights)==20 and len({tuple(x['lattice']) for x in lights})==20
S['stage']='R50 Grand Hall observed 20-cylinder fixture with candidate dimensions';S['current_file']=out.name;bpy.data.texts.new('R50_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],changed_inherited_objects=[],closed_objects=made,lights=lights,anchors=anchors,center_world=list(center),canonical_x_world=list(ex),canonical_y_world=list(ey),bottom_z=z,housing_height_m=height,observed_cylinders=20,construction_acceptance=False);(B/'reports/R50_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
manifest=json.loads((B/'references/source_manifest.json').read_text());sources=[s for s in manifest if s['id'] in P['source_ids']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R50_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=P['limits']),ensure_ascii=False,indent=2),encoding='utf8');print('R50 saved',len(made),'objects')
