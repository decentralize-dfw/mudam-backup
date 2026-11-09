import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];towers=json.loads((R/'.local_source_cache/r154/fort.json').read_text())['towers'];out={}
for label,path in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('candidate','scenes/MUDAM_R501_BATI_SUR_AGAC_KOTU_DUZELTME_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();rows=[]
 for tower in towers:
  cx,cy=tower['center'];sections=[]
  for j in range(16):
   a=j*math.pi/8;points=[]
   for i in range(101):
    r=1.5+i*.05;x=cx+r*math.cos(a);y=cy+r*math.sin(a);h,p,n,*_=s.ray_cast(dg,Vector((x,y,12)),Vector((0,0,-1)),distance=30)
    points.append([r,p.z if h else None,n.z if h else None])
   sections.append(dict(angle=a,points=points))
  rows.append(dict(tower=tower['name'],center=tower['center'],sections=sections))
 out[label]=rows;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=950;s.render.resolution_y=950;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-64,-55,70));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-64,-55,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=34;s.render.filepath=str(R/f'renders/qa/R502_tower_roofs_{label}.png');bpy.ops.render.render(write_still=True)
(R/'reports/R502_ROOF_RADIAL_PROFILES.json').write_text(json.dumps(out))
