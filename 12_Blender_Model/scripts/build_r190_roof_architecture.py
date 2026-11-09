from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R189_KUZEY_SERT_ZEMIN_v002.blend'))
rows=json.loads((R/'config/r190_roof_measurements.json').read_text())
def mat(name,c,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.75;p.inputs['Metallic'].default_value=metal;return m
warm=mat('R190_WARM_ROOF',(.27,.105,.06));deck=mat('R190_TERRACE_DECK',(.3,.28,.23));metal=mat('R190_ROOF_METAL',(.26,.29,.29),.45)
def slab(name,xy,z0,z1,material):
 n=len(xy);vs=[(x,y,z) for z in (z0,z1) for x,y in xy];ts=tessellate_polygon([[Vector((x,y,0)) for x,y in xy]])
 fs=[tuple(reversed(t)) for t in ts]+[tuple(n+i for i in t) for t in ts]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(material);o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def beam(name,a,b,z,width,height):
 a,b=Vector(a),Vector(b);n=Vector((-(b-a).y,(b-a).x)).normalized()*width/2
 return slab(name,[a+n,b+n,b-n,a-n],z,z+height,metal)
for r in rows:
 if r['name']=='MAMA_TERRACE':slab('R190_'+r['name'],r['xy'],34.005,34.035,deck)
 elif r['name']=='MAMA_WARM_ROOF':slab('R190_'+r['name'],r['xy'],34.005,34.055,warm)
 else:slab('R190_'+r['name'],r['xy'],34.055 if r['name'].startswith('MAMA') else 30.2,r['median'],metal)
# Architectural canopy frame traced from visible terrace perimeter and grid.
r=rows[0];a,b,c,d=map(Vector,r['xy'])
for i in range(5):beam('R190_TERRACE_LONG_'+str(i),a.lerp(b,i/4),d.lerp(c,i/4),34.08,.10,.12)
for i in range(4):beam('R190_TERRACE_CROSS_'+str(i),a.lerp(d,i/3),b.lerp(c,i/3),34.08,.10,.12)
for i,(p,q) in enumerate(zip(r['xy'],r['xy'][1:]+r['xy'][:1])):beam('R190_TERRACE_EDGE_'+str(i),p,q,34.08,.14,.15)
(R/'reports/R190_ROOFS_v001.json').write_text(json.dumps(dict(accepted=False,source_measurements=rows,limits=['Terrace deck source has mixed levels33.6..34m; retained34m main roof requires architectural level resolution','Frame rhythm traced visually; no exact section size claim','Technical blocks modeled independently from measured median top heights','Novotel low-roof duct grid and all building-ground connections still pending']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R190_KUZEY_CATILAR_v001.blend'),compress=True)
s=bpy.context.scene;t=Vector((345,435,20));s.camera.location=t+Vector((160,-230,160));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=210;s.render.filepath=str(R/'renders/qa/R190_roof_architecture_v001.png');bpy.ops.render.render(write_still=True)
