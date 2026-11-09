from pathlib import Path
import bpy,json,statistics
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_KABUK_v088.blend'))
center=Vector((-81.746925354,-294.516082764,-69));right=Vector((-.97769629955,-.2100233883,0));normal=Vector((-.2100236565,.97769629955,0))
data=json.loads((R/'.local_source_cache/r169/rear_dormer_measurements_v082.json').read_text())
slate=bpy.data.materials['Authored slate - neutral unlit source color not copied'];frame=bpy.data.materials['Painted light window frames'];glass=bpy.data.materials['Glazing subdued blue grey']
roofs=[o for o in bpy.context.scene.objects if o.name.startswith('ARCH_MAIN_ROOF')]
def pt(x,y,d):
 p=center+right*((x-1024)*36/2048)+normal*d;p.z=-69+(395.636-y)*36/2048;return p

def mesh(name,verts,faces,mat):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);m.materials.append(mat);o['method']='Independent planar architecture from registered source opening rectangles';return o

def quad(name,points,mat):return mesh(name,points,[(0,1,2,3)],mat)
windows=[(110,108,180,170,2),(325,105,415,177,2),(1295,97,1380,180,2),(1555,110,1640,180,2),(1710,110,1775,180,2)]
records=[]
for i,(l,t,r,b,panes) in enumerate(windows):
 measurements=[v['offset'] for v in data if l<=v['pixel'][0]<=r];off=statistics.median(measurements)
 # Cap intersections are measured on the independently authored planar main roof.
 l0,r0=l-5,r+5;top=t-6;bottom=b+6;back=[]
 for x in (l0,r0):
  p=pt(x,top,off);hits=[]
  for roof in roofs:
   h,loc,no,ix=roof.ray_cast(p+normal*.05,-normal,distance=8)
   if h:hits.append((p-loc).dot(normal))
  back.append(max(.25,min(hits)) if hits else None)
 if any(v is None for v in back):records.append(dict(index=i,pending='No planar roof intersection',back=back));continue
 depth=max(back)+.12
 # Four face strips leave a real recessed glazed opening.
 for j,(a,c,e,f) in enumerate([(l0,top,r0,t),(l0,b,r0,bottom),(l0,t,l,b),(r,t,r0,b)]):
  quad(f'ARCH_REAR_DORMER_{i}_FACE_{j}',[pt(a,c,off),pt(e,c,off),pt(e,f,off),pt(a,f,off)],slate)
 for j,(a,c,e,f) in enumerate([(l,t,r,t),(r,t,r,b),(r,b,l,b),(l,b,l,t)]):
  quad(f'ARCH_REAR_DORMER_{i}_REVEAL_{j}',[pt(a,c,off),pt(e,f,off),pt(e,f,off-.10),pt(a,c,off-.10)],frame)
 quad(f'ARCH_REAR_DORMER_{i}_GLASS',[pt(l,t,off-.10),pt(r,t,off-.10),pt(r,b,off-.10),pt(l,b,off-.10)],glass)
 for j in range(panes+1):
  x=l+(r-l)*j/panes
  quad(f'ARCH_REAR_DORMER_{i}_FRAME_{j}',[pt(x-1.5,t,off+.01),pt(x+1.5,t,off+.01),pt(x+1.5,b,off+.01),pt(x-1.5,b,off+.01)],frame)
 for j,y in enumerate((t,b)):
  quad(f'ARCH_REAR_DORMER_{i}_HFRAME_{j}',[pt(l,y-1.5,off+.01),pt(r,y-1.5,off+.01),pt(r,y+1.5,off+.01),pt(l,y+1.5,off+.01)],frame)
 for j,edge in enumerate([(l0,top,r0,top),(r0,top,r0,bottom),(r0,bottom,l0,bottom),(l0,bottom,l0,top)]):
  a,c,e,f=edge;quad(f'ARCH_REAR_DORMER_{i}_RETURN_{j}',[pt(a,c,off),pt(e,f,off),pt(e,f,off-depth),pt(a,c,off-depth)],slate)
 quad(f'ARCH_REAR_DORMER_{i}_BACK',[pt(l0,top,off-depth),pt(r0,top,off-depth),pt(r0,bottom,off-depth),pt(l0,bottom,off-depth)],slate)
 records.append(dict(index=i,sourceRectangle=[l,t,r,b],measuredFrontOffset=off,measurementCount=len(measurements),roofReturnDepth=depth,status='candidate; roof aperture integration pending'))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_CATIPENCERE_v089.blend'))
(R/'reports/R169_REAR_DORMERS_v089.json').write_text(json.dumps(dict(accepted=False,records=records,pending=['Roof aperture integration','Source visual comparison','Remaining central upper opening, balcony and chimneys']),indent=2))
s=bpy.context.scene;s.cycles.samples=16;target=Vector((-80,-301,-66));s.camera.location=target+Vector((-20,31,22));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/qa/R169_rear_dormers_v089.png');bpy.ops.render.render(write_still=True)
print('DORMER_CANDIDATE',json.dumps(records))

