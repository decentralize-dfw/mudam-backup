from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];d=json.loads((R/'config/r161_context_geometry.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R159_KAYNAK_ORTU_OLCEGI_v001.blend'));s=bpy.context.scene
original={o.name:(len(o.data.vertices),len(o.data.polygons)) for o in s.objects if o.type=='MESH'}
col=bpy.data.collections.new('R161_ROAD_LINKS_WKI_THOMAS_MORE');s.collection.children.link(col)
vs=[];fs=[]
for row in json.loads((R/'.local_source_cache/r161/surfaces.json').read_text()):
 off=len(vs);vs.extend(row['vertices']);fs.extend([[i+off for i in f] for f in row['faces']])
ground=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def height(x,y):
 p,_,_,_=ground.ray_cast(Vector((x,y,170)),Vector((0,0,-1)),500)
 if p is None:raise RuntimeError('Missing ground '+str((x,y)))
 return p.z
def mat(name,c,rough=.7,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*c,1);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
stone=mat('R161_PALE_CONCRETE',(.53,.52,.47));tan=mat('R161_THOMAS_MORE_STONE',(.38,.32,.24));glass=mat('R161_RECESSED_GLAZING',(.075,.12,.14),.23,.35);metal=mat('R161_WINDOW_FRAMES',(.22,.24,.24),.36,.4);roofmat=mat('R161_ROOF_GRAVEL',(.28,.28,.25),.95)
road=bpy.data.materials.get('R157_COMPACTED_MINERAL_PATH') or mat('R161_PATH',(.34,.32,.26));batches={}
def add(name,vertices,faces,m):
 arr=batches.setdefault(name,[[],[],m]);off=len(arr[0]);arr[0].extend(vertices);arr[1].extend([[k+off for k in f] for f in faces])
def box(name,a,b,z0,z1,depth,m):
 if z1-z0<1e-5:return
 a=Vector(a);b=Vector(b)
 if (b-a).length<1e-5:return
 u=(b-a).normalized();n=Vector((u.y,-u.x));p=[a,b,b-n*depth,a-n*depth]
 add(name,[(q.x,q.y,z) for z in (z0,z1) for q in p],[[0,3,2,1],[4,5,6,7]]+[[i,(i+1)%4,(i+1)%4+4,i+4] for i in range(4)],m)
for tri in d['roads']:
 add('R161_ROAD_CONNECTIONS',tri,[[0,1,2]],road)
contacts=[];bays=0
for b in d['buildings']:
 name='R161_'+b['id'];material=stone if b['id']=='24457411' else tan;h=b['height_tag']/b['levels']
 for level,parts in enumerate(b['tiers']):
  lo=b['base']+level*h;hi=lo+h
  for part in parts:
   ring=part['ring']
   for a,bp in zip(ring,ring[1:]+ring[:1]):
    a=Vector(a);bp=Vector(bp);length=(bp-a).length;u=(bp-a).normalized();out=Vector((u.y,-u.x));n=max(1,round(length/(2.4 if b['id']=='24457411' else 1.9)));width=length/n
    box(name+'_BANDS',a+out*.18,bp+out*.18,lo,lo+.85,.52,material)
    box(name+'_BANDS',a+out*.18,bp+out*.18,hi-.35,hi,.52,material)
    for j in range(n):
     l=a+u*j*width;r=l+u*width;box(name+'_PIERS',l,l+u*.22,lo+.85,hi-.35,.35,material)
     ll=l+u*.22-out*.15;rr=r-out*.15;box(name+'_GLASS',ll,rr,lo+.90,hi-.40,.055,glass)
     for z in [lo+.85,hi-.40]:box(name+'_FRAMES',ll,rr,z,z+.05,.09,metal)
     box(name+'_FRAMES',ll,ll+u*.05,lo+.85,hi-.35,.09,metal);bays+=1
    if level==0:
     for j in range(n):
      l=a+u*j*width;r=l+u*width;z=min(height(*l),height(*r));contacts.append(z);box(name+'_FOUNDATION',l,r,min(z-.15,lo-.15),lo+.05,.45,material)
    if level==len(b['tiers'])-1:box(name+'_PARAPET',a,bp,hi,hi+.35,.30,material)
   # Floor/roof plates also form the visible setback terraces.
   for tri in part['triangles']:add(name+'_ROOF',[(x,y,hi-.015) for x,y in tri],[[0,1,2]],roofmat)
 for tri in b['roof_triangles']:add(name+'_BASE',[(x,y,b['base']) for x,y in tri],[[0,1,2]],material)
for name,(v,f,m) in batches.items():
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);col.objects.link(o);mesh.materials.append(m);o['source']='R161 OSM footprint and ACT reference study';o['level_id']='SITE_R161';o['status']='source_based_model_candidate'
assert all((len(bpy.data.objects[n].data.vertices),len(bpy.data.objects[n].data.polygons))==v for n,v in original.items())
out=R/'scenes/MUDAM_R161_YOL_BAGLANTILARI_WKI_THOMAS_MORE_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(out));col=bpy.data.collections['R161_ROAD_LINKS_WKI_THOMAS_MORE'];bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r161_additions.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
for label,eye,target in [('buildings',(-20,120,130),(-90,370,12)),('roads',(330,-230,400),(30,80,-5))]:
 s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=45;s.render.filepath=str(R/f'renders/qa/R161_{label}.png');bpy.ops.render.render(write_still=True)
report=dict(scene=out.name,buildings=[b['name'] for b in d['buildings']],road_patches=d['road_patches'],added_road_area=d['added_road_area'],facade_bays=bays,objects=len(col.objects),existing_geometry_preserved=True,reopened=True,limits=d['limits'],whole_context_complete=False)
(R/'reports/R161_BUILD.json').write_text(json.dumps(report,indent=2));print('R161_COMPLETE',json.dumps(report),flush=True)
