"""R58: source008/011/012 supersede the unsupported thin three-rail bridge study."""
from pathlib import Path
import bpy,bmesh,json,sys,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R57_GIRIS_PASPAS_IZGARA_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R58_KOPRU_CAM_KORKULUK_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));P=json.loads((B/'config/site_bridges.json').read_text());root=bpy.data.collections.new('R58_BRIDGE_ROUND_RAIL_GLASS');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);up=Vector((0,0,1));made=[];changed=[];rows=[]
metal=bpy.data.materials.new('R58_PALE_METAL_GUARD_CANDIDATE');metal.use_nodes=True;bs=metal.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.29,.34,.36,1);bs.inputs['Metallic'].default_value=.65;bs.inputs['Roughness'].default_value=.42;glass=bpy.data.materials['P10_GLASS_PREVIEW']
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);root.objects.link(o);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='APPROACH',level_id='L00_APPROACH',source_ids='008,011,012,OSM759554470,OSM759554472',status='conditional_photo_guard_candidate',confidence_xy='C OSM endpoint with60mm inward candidate; D column-face attachment',confidence_z='D inherited overall height',confidence_detail='C round rail plus glass topology; D sections',assumption_note='012/008/011 show large round upper member, plate supports and low glass infill. Dimensions, spacing and glass thickness unmeasured. Column attachment reconciles approximate OSM endpoints locally without moving floor plans.').items():o[k]=v
 made.append(name);return o
def prism(name,poly,axis,thickness,mat,kind):
 vs=[tuple(p+axis*d) for d in [-thickness/2,thickness/2] for p in poly];N=len(poly);fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];return mesh(name,vs,fs,mat,kind)
def cylinder(name,a,b,r):
 direction=(b-a).normalized();v=direction.cross(up).normalized();N=48;vs=[tuple(c+(v*math.cos(i*math.tau/N)+up*math.sin(i*math.tau/N))*r) for c in [a,b] for i in range(N)];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];ob=mesh(name,vs,fs,metal,'large_round_bridge_handrail_candidate')
 for f in ob.data.polygons:f.use_smooth=f.index>=2
 return ob
col=bpy.data.objects['P07_CORNER_SUPPORT_ENVELOPE'];foot=[col.matrix_world@v.co for v in col.data.vertices if abs((col.matrix_world@v.co).z)<1e-5];assert len(foot)==4
tip=max(foot,key=lambda p:p.x+p.y);adj=sorted([p for p in foot if p!=tip],key=lambda p:(p-tip).length)[:2];north=max(adj,key=lambda p:p.y);east=max(adj,key=lambda p:p.x)
for way,face in [('759554470',(tip+north)/2),('759554472',(tip+east)/2)]:
 ps=[Vector((x-293425,y-5499960,0)) for x,y in next(w['xy'] for w in P['ways'] if w['id']==way)];outer=max(ps,key=lambda p:(p-tip).length);old_inner=min(ps,key=lambda p:(p-tip).length);a=face;initial_axis=(outer-a).normalized();inward=initial_axis.cross(up).normalized();bridge=next(w for w in P['ways'] if w['id']==('759551375' if way=='759554470' else '759551376'));center=sum((Vector((x-293425,y-5499960,0)) for x,y in bridge['xy']),Vector())/len(bridge['xy']);inward=-inward if inward.dot(center-outer)<0 else inward;b=outer+inward*.06;axis=(b-a).normalized();normal=axis.cross(up).normalized();length=(b-a).length;count=math.ceil(length/2.5);pitch=length/count;radius=.16;zc=1.05-radius;posts=[];panels=[];tubes=[]
 # Stone column supports the building end; do not invent an extra plate against it.
 for i in range(1,count+1):
  t=max(.14,min(length-.14,i*pitch));c=a+axis*t;half=.10;profile=[c-axis*half,c+axis*half]
  for j in range(13):
   xx=half-j*(2*half/12);profile.append(c+axis*xx+up*(zc-math.sqrt(radius*radius-xx*xx)))
  posts.append(prism(f'R58_POST_{way}_{i:02d}',profile,normal,.08,metal,'saddle_plate_bridge_support_candidate').name)
 tubes.append(cylinder(f'R58_TUBE_{way}',a-axis*.025+up*zc,b+up*zc,radius).name)
 for i in range(count):
  t0=i*pitch;t1=(i+1)*pitch
  g0=t0+(.03 if i==0 else .11);g1=t1-(.245 if i==count-1 else .11);c0=a+axis*g0;c1=a+axis*g1
  panels.append(prism(f'R58_GLASS_{way}_{i:02d}',[c0+up*.08,c1+up*.08,c1+up*.62,c0+up*.62],normal,.022,glass,'low_bridge_glass_infill_candidate').name)
  prism(f'R58_BASE_CHANNEL_{way}_{i:02d}',[c0,c1,c1+up*.085,c0+up*.085],normal,.045,metal,'glass_base_channel_candidate')
 rows.append(dict(way=way,start=list(a),end=list(b),old_inner=list(old_inner),old_outer=list(outer),outer_inset_m=.06,attachment_shift_m=(a-old_inner).length,length=length,pitch=pitch,post_count=count,post_names=posts,glass_names=panels,tube_names=tubes,rail_radius=radius,rail_center_z=zc,top_z=1.05))
for ob in list(bpy.context.scene.objects):
 if ob.name.startswith(('R34_POST_','R34_RAIL_')):ob.hide_render=True;ob.hide_set(True);changed.append(ob.name)
bpy.context.scene['stage']='R58 bridge round rails and low glass infill';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R58_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=made,changed_inherited_objects=changed,guard_runs=rows,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['008','011','012']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R58_source_receipt.json').write_text(json.dumps(dict(sources=sources,position_source='config/site_bridges.json archived OSM plus existing P07 column faces',limits=['Photo-supported round rail/plate/glass topology supersedes R34 unsupported intermediate rods.','Overall height1.05m, tube320mm, glass22mm, plate80mm and spacing<=2.5m are unmeasured candidates.','Inner endpoints locally attached to visible column; outer ends inset60mm to support full plate footprint; original OSM endpoint discrepancies explicitly recorded. No source plan, column, deck or terrain moved.','No hidden anchors, glass specification, structural or regulatory approval.']),indent=2),encoding='utf8');print('R58',len(made),'objects',[(r['way'],r['attachment_shift_m']) for r in rows])
