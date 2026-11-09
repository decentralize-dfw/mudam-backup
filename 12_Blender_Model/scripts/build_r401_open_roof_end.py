import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R400_KALE_CAM_BANT_AHSAP_TERAS_ADAY_v001.blend'))
d=json.loads((R/'reports/R387_ROOF_INPUT.json').read_text());line=d['crestOutline'];n=len(line);edits=[]
def replace(ob,vs,fs):
 old=ob.data;me=bpy.data.meshes.new(ob.name+'_OPEN_END');me.from_pydata(vs,[],fs);me.update()
 for ma in old.materials:me.materials.append(ma)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob.data=me
 uv=me.uv_layers.new(name='UVMap')
 for l in me.loops:
  v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x-v.y)/4.24264,(v.x+v.y)/1.64049)
 ob['R401_correction']='Photo rooftop_view_2 shows open tower-facing roof end; no transverse glazed wall.'
 edits.append(ob.name)
# Remove only the terminal fascia strip, closing the exposed sheet ends.
ob=bpy.data.objects['R400_SLOPED_PERIMETER_FASCIA'];vs=[tuple(v.co) for v in ob.data.vertices];fs=[list(p.vertices) for p in ob.data.polygons][6:]
fs.extend([list(range(6)),list(range(6,12))]);replace(ob,vs,fs)
# Glass, rails and louvers were created as disconnected closed boxes. Remove
# boxes centered on terminal segment 0; preserve both longitudinal bands.
a=Vector(line[0]);b=Vector(line[1]);t=b-a
for name in ['R400_PERIMETER_CLERESTORY_GLASS','R400_PERIMETER_WINDOW_FRAMES','R400_PERIMETER_HORIZONTAL_LOUVERS']:
 ob=bpy.data.objects[name];me=ob.data;vs=[];fs=[];removed=0
 for k in range(0,len(me.vertices),8):
  pts=[me.vertices[k+j].co.copy() for j in range(8)];p=sum((v.to_2d() for v in pts),Vector((0,0)))/8;u=(p-a).dot(t)/t.length_squared;dist=(p-a-t*u).length
  if -.01<=u<=1.01 and dist<.20:removed+=1;continue
  z=len(vs);vs.extend(tuple(v) for v in pts)
  fs.extend([[z+j for j in f] for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 replace(ob,vs,fs);ob['R401_removed_terminal_boxes']=removed
# The transverse timber ledge is also absent in the photo. Open its end and
# carry the lower measured deck plane out to the terminal footprint.
ob=bpy.data.objects['R389_FORT_PERIMETER_LEDGE'];vs=[tuple(v.co) for v in ob.data.vertices];fs=[list(p.vertices) for p in ob.data.polygons][4:]
fs.extend([[0,n,3*n,2*n],[1,2*n+1,3*n+1,n+1]]);replace(ob,vs,fs)
xy=[d['roofOutline'][0],d['roofOutline'][1],line[1],line[0]];c=d['lowerPlane'];z=lambda p:c[0]*p[0]+c[1]*p[1]+c[2]
vs=[(p[0],p[1],z(p)+dz) for dz in [-.18,0] for p in xy];fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
me=bpy.data.meshes.new('R401_FORT_OPEN_END_TIMBER_DECK');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(bpy.data.materials['R400_WEATHERED_TIMBER_DECK']);replace(ob,vs,fs);ob['level_id']='SITE'
out=R/'scenes/MUDAM_R401_KALE_ACIK_TERAS_UCU_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in edits:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(x['nonManifold'] or x['zeroArea'] for x in checks),checks
report=dict(scene=out.name,accepted=False,published=False,source='references/fort_inpa/rooftop_view_2_Zinneke_CC_BY_SA_3.jpg',changes=edits,checks=checks,limits=['Open roof-end is corrected; tower court, staircase and historic wall detailing still incomplete. No whole-ring acceptance.'])
(R/'reports/R401_OPEN_ROOF_END.json').write_text(json.dumps(report,indent=2))
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-28,-20,4));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-61.6,-53.15,2.8))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=28;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=667;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R401_rooftop_eye_candidate.png');bpy.ops.render.render(write_still=True)
print('R401_READY')
