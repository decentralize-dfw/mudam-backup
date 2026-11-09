from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R179_UZAK_CEVRE_v001.blend'))
col=bpy.data.collections['R178_INDEPENDENT_STATION'];metal=bpy.data.materials['R178_FRAME'];stone=bpy.data.materials['R178_PLATFORM']
for o in list(bpy.data.objects):
 if o.name.startswith('R178_TRACK_RAIL'):bpy.data.objects.remove(o,do_unlink=True)
source=json.loads((R/'reports/R178_TRACK_SOURCE.json').read_text());ways=json.loads((R/'config/r178_funicular_tracks.json').read_text());fits={}
for row in source:
 a=np.array(row['samples']);fit=np.polyfit(a[:,0],a[:,2],1);fits['A' if row['id']=='466675116' else 'B']=fit
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(m);return o
def beam(name,a,b,w,m):
 a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.01:u=Vector((1,0,0))
 u.normalize();v=axis.cross(u).normalized();vs=[p+u*i*w/2+v*j*w/2 for p in [a,b] for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)

for o in list(col.objects):
 if o.type!='MESH' or o.name.startswith('R178_ROOF'):continue
 for v in o.data.vertices:
  if v.co.z < -3:
   c=fits['A' if v.co.y>237 else 'B'];v.co.z=min(-6,float(c[0]*v.co.x+c[1]))
beds=[]
for row in ways:
 a,b=[Vector((*p,0)) for p in row['xy']];n=Vector((-(b-a).y,(b-a).x,0)).normalized();c=fits[row['tags']['name']]
 def z(p):return min(-6,float(c[0]*p.x+c[1]))
 for side in [-.9,.9]:
  l=a+n*side;r=b+n*side;beam('R178_MEASURED_1800_RAIL',(l.x,l.y,z(l)+.1),(r.x,r.y,z(r)+.1),.08,metal)
 xy=[a-n*2.3,b-n*2.3,b+n*2.3,a+n*2.3];mesh('R178_MEASURED_TRACK_BED',[(p.x,p.y,z(p)-.04) for p in xy],[(0,1,2,3)],stone)
 beds.append(dict(name='TRACK_'+row['id'],xy=[[p.x,p.y] for p in xy],plane=[float(c[0]),0,float(c[1])-.04],origin=[0,0],p90=None))
(R/'config/r180_track_beds.json').write_text(json.dumps(beds,indent=2))
(R/'reports/R180_TRACKS_v001.json').write_text(json.dumps(dict(accepted=False,gauge=1.8,source='OSM gauge1800 and ACT five exposed rail levels per track',fits={k:v.tolist() for k,v in fits.items()},limits=['Terrain corridor cut pending','Station level capped at -6m exterior apron datum']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R180_ISTASYON_RAY_KOT_v001.blend'),compress=True)
print('R180_DONE')
