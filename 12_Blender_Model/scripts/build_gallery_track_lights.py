"""R70: source-supported fixture family, explicitly conditional partial placement."""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
P=json.loads((B/'config/gallery_track_lights.json').read_text())
C=json.loads((B/'config/foundation.json').read_text())['calibration']
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001'
out=B/'scenes'/f'MUDAM_R70_GALERI_RAY_SPOT_{version}.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']))
root=bpy.data.collections.new('R70_GALLERY_TRACK_LIGHT_CANDIDATES');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
up=Vector((0,0,1));made=[];fixtures=[];tracks=[];H=P['ceiling_z']
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
ex=(point(1,0)-point(0,0)).normalized();ey=(point(0,1)-point(0,0)).normalized()
def material(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
black=material('R70_BLACK_TRACK_SPOT_CANDIDATE',(.018,.020,.021),.55,.32)
lensmat=material('R70_UNLIT_LENS_CANDIDATE',(.035,.038,.040),.4,.18)
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='GROUND_E_GALLERY',level_id='L00',source_ids='061,062,102,101',status='partial_editable_lighting_candidate',confidence_xy='D candidate; ceiling footprint constrained',confidence_z='D inherited 4.35m soffit',confidence_detail='C fixture family; D dimensions',assumption_note='R70: two tracks/eight adjustable heads are a partial unmeasured arrangement. Not a fixed schedule, product specification or lighting calculation; see gallery_track_lights.json.').items():ob[k]=v
 made.append(name);return ob
def box(name,c,dx,dy,dz,mat=black,kind='track_fixture_component_candidate'):
 vs=[c+ex*x+ey*y+up*z for z in [-dz/2,dz/2] for x,y in [(-dx/2,-dy/2),(dx/2,-dy/2),(dx/2,dy/2),(-dx/2,dy/2)]]
 return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,kind)
def cylinder(name,c,axis,rad,z0,z1,mat=black):
 n=40;u=axis.cross(ex).normalized() if abs(axis.dot(ex))<.9 else axis.cross(ey).normalized();v=axis.cross(u).normalized()
 vs=[c+axis*z+rad*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n)) for z in [z0,z1] for i in range(n)]
 fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 ob=mesh(name,vs,fs,mat,'cylindrical_fixture_component_candidate')
 for f in ob.data.polygons:f.use_smooth=abs(f.normal.dot(axis))<.5
 return ob
def ring(name,c,axis,profile,mat=black):
 n=40;u=ex;v=axis.cross(u).normalized();vs=[c+axis*z+r*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n)) for r,z in profile for i in range(n)]
 fs=[(j*n+i,j*n+(i+1)%n,((j+1)%len(profile))*n+(i+1)%n,((j+1)%len(profile))*n+i) for j in range(len(profile)) for i in range(n)]
 ob=mesh(name,vs,fs,mat,'closed_fixture_shell_candidate')
 for f in ob.data.polygons:f.use_smooth=abs(f.normal.dot(axis))<.5
 return ob
for track in P['tracks']:
 a=point(*track['start']);b=point(*track['end']);center=(a+b)/2;length=(b-a).length;key='R70_TRACK_'+track['id']
 back=box(key+'_BACK',center+up*(H-.003),.035,length,.006,kind='ceiling_track_back_candidate')
 sides=[box(key+f'_RAIL_{i}',center+ex*(sign*.0145)+up*(H-.013),.006,length,.026,kind='ceiling_track_rail_candidate').name for i,sign in enumerate([-1,1])]
 tracks.append(dict(id=key,start=list(a),end=list(b),back=back.name,rails=sides))
 for i,t in enumerate(track['fixture_fractions']):
  c=a.lerp(b,t);stem_bottom=H-.12;pivot=c+up*(H-.235);axis=(ey*(math.sin(math.radians(20))*(1 if i%2 else -1))-up*math.cos(math.radians(20))).normalized();prefix=key+f'_HEAD_{i:02d}';parts=[]
  parts.append(box(prefix+'_ADAPTER',c+up*(H-.033),.026,.060,.022).name)
  parts.append(cylinder(prefix+'_STEM',c,up,.008,H-.123,H-.040).name)
  parts.append(box(prefix+'_YOKE_TOP',c+up*(H-.126),.164,.040,.014).name)
  for side in [-1,1]:parts.append(box(prefix+f'_YOKE_{side:+d}',c+ex*(side*.076)+up*(H-.181),.012,.040,.110).name)
  parts.append(cylinder(prefix+'_PIVOT_PIN',pivot,ex,.009,-.086,.086).name)
  body=ring(prefix+'_BODY',pivot,axis,[(.060,-.060),(.060,.125),(.052,.125),(.052,-.060)]);parts.append(body.name)
  parts.append(cylinder(prefix+'_BACK_CAP',pivot,axis,.060,-.066,-.058).name)
  lens=cylinder(prefix+'_LENS',pivot,axis,.050,.126,.132,lensmat);parts.append(lens.name)
  rim=ring(prefix+'_BEZEL',pivot,axis,[(.065,.122),(.065,.146),(.048,.146),(.048,.122)]);parts.append(rim.name)
  fixtures.append(dict(id=prefix,track=key,ceiling_point=list(c+up*H),pivot=list(pivot),axis=list(axis),lens=lens.name,body=body.name,rim=rim.name,parts=parts))
bpy.context.scene['stage']='R70 conditional gallery track and spot fixture detail';bpy.context.scene['current_file']=out.name
bpy.data.texts.new('R70_SOURCE_AND_LIMITS').write(json.dumps(P,ensure_ascii=False,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=[],tracks=tracks,fixtures=fixtures,soffit_z=H,canonical_x_world=list(ex),canonical_y_world=list(ey),construction_acceptance=False)
(B/'reports/R70_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in P['source_ids']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R70_source_receipt.json').write_text(json.dumps(dict(sources=sources,observations=P['observations'],limits=P['limits']),indent=2),encoding='utf8')
print('R70',len(tracks),'tracks',len(fixtures),'heads',len(made),'parts')
