"""P10: planar clipping preserves triangular edge modules instead of fan subdivision."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from roof_panel_math import clip,area,inset
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001'
P=json.loads((B/'config/roof_panel_system.json').read_text());out=B/'scenes'/f'MUDAM_P10_CAM_CATI_{version}.blend'
if out.exists():raise RuntimeError('Choose a new version')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene
root=bpy.data.collections.new('P10_MAIN_ROOF_PANELS_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
def collection(name):
 c=bpy.data.collections.new(name);root.children.link(c);return c
glasscol=collection('P10_GLASS_PANELS');framecol=collection('P10_SURFACE_FRAMES');edgecol=collection('P10_PERIMETER_FRAMES')
def mat(name,color,metal=0,trans=0,rough=.3):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Transmission Weight'].default_value=trans;p.inputs['IOR'].default_value=1.5;return m
glass=mat('P10_GLASS_PREVIEW',(.37,.59,.60),trans=.92,rough=.09);metal=mat('P10_FRAME_PREVIEW',(.19,.23,.23),metal=.7,rough=.3)
made=[];facets=[];frame_keys=set();closed=[]
def mesh(name,verts,faces,col,material,kind,facet):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(material)
 for key,value in dict(element_id=name,element_type=kind,zone_id='GH_ROOF',level_id='ROOF',source_ids=','.join(P['source_ids']),status='conditional_panel_reconstruction',confidence_xy='C/D source-calibrated envelope; candidate grid',confidence_z='D section ratio',confidence_detail='D unmeasured profiles',parameter_ids='roof_panel_system.json',parent_facet=facet,export_group='P10_CONDITIONAL',assumption_note='Grid and all thicknesses are visualization hypotheses; internal structural system unresolved.').items():ob[key]=value
 made.append(ob.name);closed.append(ob.name);return ob
def extrude(name,points,normal,depth,col,material,kind,facet):
 n=len(points);vs=[tuple(p) for p in points]+[tuple(p-normal*depth) for p in points];faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh(name,vs,faces,col,material,kind,facet)
def beam(name,a,b,normal,width,depth,col,kind,facet,dedup=True):
 if (b-a).length<.025:return
 key=tuple(sorted(tuple(round(v,5) for v in p) for p in [a,b]))
 if dedup and key in frame_keys:return
 frame_keys.add(key);side=normal.cross((b-a).normalized()).normalized()*width/2
 lift=normal*P['frame_cap_above_glass_m']
 return extrude(name,[a-side+lift,b-side+lift,b+side+lift,a+side+lift],normal,depth,col,metal,kind,facet)
sources=[ob for ob in list(S.objects) if ob.name.startswith(('P06_MAIN_ROOF_FACE_','P06_MAIN_LANTERN_','P06_MAIN_CAP_')) and not ob.hide_render]
for src in sources:
 name=src.name;points=[src.matrix_world@v.co for v in src.data.vertices];origin=points[0];u=(points[1]-origin).normalized();normal=(points[1]-origin).cross(points[2]-origin).normalized();v=normal.cross(u).normalized();poly=[[(p-origin).dot(u),(p-origin).dot(v)] for p in points]
 # Orient v towards polygon interior; use exterior normal separately for glass thickness.
 if sum(p[1] for p in poly)<0:v=-v;poly=[[(p-origin).dot(u),(p-origin).dot(v)] for p in points]
 exterior=src.data.polygons[0].normal.normalized()
 if exterior.length<.9:raise RuntimeError(name)
 deviation=max(abs((p-origin).dot(normal)) for p in points)
 assert deviation<.001,(name,deviation)
 xmin=min(p[0] for p in poly);xmax=max(p[0] for p in poly);ymin=min(p[1] for p in poly);ymax=max(p[1] for p in poly);width=xmax-xmin;height=ymax-ymin;index=int(name.rsplit('_',1)[1])
 if 'ROOF_FACE' in name:nx=P['main_strip_columns'] if index%2==0 else P['main_wide_columns'];ny=P['main_slope_rows']
 elif 'LANTERN' in name:nx=3 if width>2 else 1;ny=max(1,round(height/P['lantern_module_height_m']))
 else:nx=3 if width>2 else 1;ny=P['cap_rows']
 def world(q):return origin+u*q[0]+v*q[1]
 panels=0;covered=0;raw_edges=[]
 for row in range(ny):
  for column in range(nx):
   cell=poly[:]
   for axis,value,sign in [(0,xmin+width*column/nx,1),(0,xmin+width*(column+1)/nx,-1),(1,ymin+height*row/ny,1),(1,ymin+height*(row+1)/ny,-1)]:cell=clip(cell,axis,value,sign)
   if len(cell)<3 or area(cell)<1e-7:continue
   covered+=area(cell);pane=inset(cell,P['glass_inset_m']);panels+=1
   if len(pane)<3:raise RuntimeError('Inset removes pane '+name)
   ob=extrude(f'P10_{name[4:]}_GLASS_{row:02}_{column:02}',[world(q) for q in pane],exterior,P['glass_thickness_m'],glasscol,glass,'roof_glass_panel',name);ob['panel_row']=row;ob['panel_column']=column;ob['untrimmed_area_m2']=area(cell)
   for a,b in zip(cell,cell[1:]+cell[:1]):raw_edges.append((world(a),world(b)))
 for i,(a,b) in enumerate(raw_edges):beam(f'P10_{name[4:]}_GRID_{i:04}',a,b,exterior,P['secondary_face_width_m'],P['secondary_depth_m'],framecol,'surface_mullion',name)
 for i,(a,b) in enumerate(zip(points,points[1:]+points[:1])):beam(f'P10_{name[4:]}_EDGE_{i}',a,b,exterior,P['perimeter_face_width_m'],P['perimeter_depth_m'],edgecol,'perimeter_frame',name,False)
 src.hide_render=True;src.hide_set(True);src['status']='superseded_by_P10_separate_panels'
 facets.append(dict(source=name,area_m2=area(poly),partition_area_m2=covered,partition_error_m2=abs(covered-area(poly)),panel_count=panels,grid=[nx,ny],planarity_error_m=deviation))
 assert abs(covered-area(poly))<.0001,name
S['stage']='P10 main roof panel reconstruction; unmeasured frame sizes and internal tension structure pending';S['current_file']=out.name
txt=bpy.data.texts.new('P10_READ_ME');txt.write(json.dumps(P,indent=2))
S.camera=bpy.data.objects['P07_PHOTO_119_CONDITIONAL'];S.render.resolution_x=1600;S.render.resolution_y=754;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.filepath=str(B/'renders/qa/P10_119.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
for key,size in [('119',(1600,754)),('087',(1920,1281)),('116',(2000,1333))]:
 S.camera=bpy.data.objects['P07_PHOTO_'+key+'_CONDITIONAL'];S.render.resolution_x,S.render.resolution_y=size;S.render.filepath=str(B/f'renders/qa/P10_{key}.png');bpy.ops.render.render(write_still=True)
report=dict(file=out.relative_to(R).as_posix(),objects=len(made),closed_objects=closed,panel_count=len(glasscol.objects),surface_frame_count=len(framecol.objects),perimeter_count=len(edgecol.objects),facets=facets,structural_detail_complete=False,global_acceptance=False)
(B/'reports/P10_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('P10_SAVED',out,'panels',len(glasscol.objects))
