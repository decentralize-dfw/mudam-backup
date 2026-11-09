from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import shapely
from shapely.geometry import Polygon
p=R/'config/r202_river_domains.json';d=json.loads(p.read_text())
for r in d['domains']:r['cuts']=[list(t.exterior.coords)[:-1] for t in shapely.constrained_delaunay_triangles(Polygon(r['outer'],r['holes'])).geoms]
p.write_text(json.dumps(d));print(sum(len(r['cuts']) for r in d['domains']))
s=(R/'scripts/build_r192_transitions.py').read_text();s=s.replace('MUDAM_R191_KUZEY_AVLULAR_v001','MUDAM_R201_KUZEY_KAPALI_CATILAR_v001').replace("rows=json.loads((R/'config/r192_court_transitions.json').read_text())","rows=json.loads((R/'config/r202_river_domains.json').read_text())['domains']")
s=s[:s.index("grass=bpy.data.objects")];s=s.replace("obj.name not in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS']","not (obj.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS'] or obj.name.startswith(('R182_EXTENSION_GROUND','R182_EXTENSION_ROADS')))")
s+='''
water=bpy.data.materials.new('R202_ALZETTE_WATER');water.use_nodes=True;p=water.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.035,.085,.075,1);p.inputs['Roughness'].default_value=.25;p.inputs['Metallic'].default_value=.12
for i,row in enumerate(rows):
 me=bpy.data.meshes.new('R202_ALZETTE_%02d'%i);me.from_pydata(row['vertices'],[],row['faces']);me.update();me.materials.append(water);o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o)
def inside(p,ring):
 h=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:h=not h
 return h
removed=[]
for o in list(bpy.data.objects):
 if not o.name.startswith('R157_TREE_'):continue
 p=o.matrix_world.translation
 if any(inside(p,r['outer']) and not any(inside(p,h) for h in r['holes']) for r in rows):removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
(R/'reports/R202_RIVER_RELATION.json').write_text(json.dumps(dict(accepted=False,source='OSM banks and ACT2024 MNT independent water plane',terrain_changes=changes,removed_tree_roots=removed,limits=['Water plane fit has partial support; shoreline height comparison pending','Road crossings require independently modeled bridge decks; not all crossings accepted']),indent=2))
s=bpy.context.scene;t=Vector((-165,-365,-55));s.camera.location=t+Vector((-180,-200,140));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=340;s.render.resolution_x=1400;s.render.resolution_y=1000;s.cycles.samples=12
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R202_ALT_MAHALLE_NEHIR_v001.blend'),compress=True);s.render.filepath=str(R/'renders/qa/R202_river_ground_v001.png');bpy.ops.render.render(write_still=True)
'''
(R/'scripts/build_r202_river.py').write_text(s)
