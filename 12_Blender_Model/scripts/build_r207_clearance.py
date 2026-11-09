from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R206_NOVOTEL_BUTUN_CATILAR_v001.blend'));domains=[]
def add(name,outer,holes=[]):domains.append(dict(name=name,outer=outer,holes=holes,bounds=[min(p[0] for p in outer),max(p[0] for p in outer),min(p[1] for p in outer),max(p[1] for p in outer)]))
for r in json.loads((R/'config/r176_authored_parts.json').read_text()):add(r['name'],r['outer'],r['holes'])
r=json.loads((R/'config/r183_suites_architecture.json').read_text());add('NOVOTEL_SUITES',r['outer'])
for r in json.loads((R/'config/r188_all_background_domains.json').read_text()):add(r['name'],r['outer'],r['holes'])
for r in json.loads((R/'config/r178_roof_planes.json').read_text())+json.loads((R/'config/r180_track_beds.json').read_text()):add('STATION_'+r.get('name','rail'),r['xy'])
for i,r in enumerate(json.loads((R/'config/r202_river_domains.json').read_text())['domains']):add('RIVER_'+str(i),r['outer'],r['holes'])
r=json.loads((R/'config/r205_river_crossing.json').read_text());add('FORT_OLISY_BRIDGE',r['footprint']);r=json.loads((R/'config/r200_bridge_alignment.json').read_text());add('RAIL_VIADUCT',r['footprint'])
def inside(p,ring):
 h=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:h=not h
 return h
removed=[];checked=0
for o in list(bpy.data.objects):
 if not o.name.startswith(('R157_TREE_','R158_TREE_')):continue
 checked+=1;p=o.matrix_world.translation;matches=[]
 for r in domains:
  lo,hi,bo,to=r['bounds']
  if lo<=p.x<=hi and bo<=p.y<=to and inside(p,r['outer']) and not any(inside(p,h) for h in r['holes']):matches.append(r['name'])
 if matches:
  # Trees genuinely beneath a high viaduct may remain; only crowns reaching its deck are collisions.
  if matches==['RAIL_VIADUCT']:
   top=max((o.matrix_world@Vector(v)).z for v in o.bound_box)
   if top<-48:continue
  removed.append(dict(name=o.name,root=list(p),domains=matches));bpy.data.objects.remove(o,do_unlink=True)
counts={}
for r in removed:
 for name in r['domains']:counts[name]=counts.get(name,0)+1
(R/'reports/R207_ACTUAL_TREE_CLEARANCE.json').write_text(json.dumps(dict(accepted=False,checked=checked,removed_count=len(removed),counts=counts,removed=removed,correction='R197 and R202 checked obsolete R157 prefix and removed zero trees. This pass checks the actual R158 scene instances.',limits=['Only root-domain or viaduct-crown collision removal; adjacent overhanging crowns retained','No species or complete vegetation fidelity claim']),indent=2));print('REMOVED',len(removed),counts,flush=True)
s=bpy.context.scene;t=Vector((-184,-368,-73));s.camera.location=t+Vector((-35,-50,35));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=50;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R207_GERCEK_BITKI_CAKISMA_TEMIZLIGI_v001.blend'),compress=True);s.render.filepath=str(R/'renders/qa/R207_crossing_clearance_v001.png');bpy.ops.render.render(write_still=True)
