from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R205_ALT_YOL_KOPRUSU_v001.blend'));rows=json.loads((R/'config/r206_closed_roofs.json').read_text());report=[]
for row in rows:
 obj=bpy.data.objects['R176_'+row['name']];base=min(v.co.z for v in obj.data.vertices);c=row['plane'];ox,oy=row['origin'];oldtop=row['old_top']
 def height(x,y):return c[0]*(x-ox)+c[1]*(y-oy)+c[2]
 for v in obj.data.vertices:v.co.z=base+(v.co.z-base)*(height(v.co.x,v.co.y)-base)/(oldtop-base)
 obj.data.update();vs=[];fs=[]
 def face(ps):k=len(vs);vs.extend(ps);fs.append(tuple(range(k,k+len(ps))))
 for tri in row['curb_triangles']:
  face([(x,y,height(x,y)) for x,y in reversed(tri)]);face([(x,y,row['parapet']) for x,y in tri])
 for ring in [row['outer'],row['inner']]:
  for a,b in zip(ring,ring[1:]+ring[:1]):face([(a[0],a[1],height(*a)),(b[0],b[1],height(*b)),(b[0],b[1],row['parapet']),(a[0],a[1],row['parapet'])])
 me=bpy.data.meshes.new('R206_PARAPET_'+row['name']);me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials['R176_PALE_MINERAL']);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
 if row['name']=='NOVOTEL_HIGH':
  tech=bpy.data.objects['R190_NOVOTEL_TECHNICAL']
  for v in tech.data.vertices:
   if abs(v.co.z-oldtop)<.01:v.co.z=height(v.co.x,v.co.y)
 report.append(dict(name=row['name'],base=base,old_roof=oldtop,new_plane=row['plane'],parapet=row['parapet'],plane_inliers=row['inliers'],plane_samples=row['samples'],source_edge_coverage=[row['source_edges']['measured_edges'],row['source_edges']['total_edges']]))
(R/'reports/R206_NOVOTEL_ROOF_REBUILD.json').write_text(json.dumps(dict(accepted=False,buildings=report,method='Whole facade upper limits and planar roofs rebuilt to dominant ACT roof observations; independent closed parapets; technical block base reconnected',limits=['Coping width0.24m assumed','Unobserved perimeter edge tops use median of observed edges','Low roof technical curb/duct grid and facade cadence remain pending']),indent=2))
s=bpy.context.scene;t=Vector((370,440,20));s.camera.location=t+Vector((120,-190,140));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=170;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R206_NOVOTEL_BUTUN_CATILAR_v001.blend'),compress=True);s.render.filepath=str(R/'renders/qa/R206_novotel_roofs_v001.png');bpy.ops.render.render(write_still=True)
