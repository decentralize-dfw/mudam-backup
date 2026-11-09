from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_MANSARD_v078.blend'))
d=json.loads((D/'architectural_rear_hip_plane_v079.json').read_text());c=np.array(d['coeff']);origin=np.array(d['origin']);xy=np.array(d['corners']);z=(xy-origin)@c[:2]+c[2];pts=[Vector((*p,h)) for p,h in zip(xy,z)]
slate=bpy.data.materials['Authored slate - neutral unlit source color not copied'];plaster=bpy.data.materials['Mineral plaster provisional palette'];stone=bpy.data.materials['Painted light window frames']
def mesh(name,v,f,mat=None):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 if mat:me.materials.append(mat)
 return o
# Replace only the main rear roof's overlapping triangular domain with the measured architectural plane.
cut=mesh('temporary_triangular_roof_cut',[(*p,h) for h in [-80,-50] for p in xy],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
roof=bpy.data.objects['ARCH_MAIN_ROOF_1'];bpy.context.view_layer.objects.active=roof;m=roof.modifiers.new('Rear roof projection domain','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
new=mesh('ARCH_REAR_PROJECTING_ROOF',pts,[(0,2,1)],slate);m=new.modifiers.new('Roof thickness assumption 0.12m','SOLIDIFY');m.thickness=.12
# Front plane and short return walls of the measured rear projection.
f=json.loads((D/'facade_planes_v062.json').read_text());normal=np.array(f['sides'][0]['normal']);q=np.array(f['q']);limit=normal@q[0]+f['sides'][0]['offset'];back=[]
for p in xy[:2]:back.append(p-normal*(normal@p-limit))
outline=[xy[0],xy[1],back[1],back[0]]
for i in [0,1,3]:
 a=outline[i];b=outline[(i+1)%4];ha=(a-origin)@c[:2]+c[2];hb=(b-origin)@c[:2]+c[2];mesh('ARCH_REAR_PROJECTION_WALL_'+str(i),[(*a,-75),(*b,-75),(*b,hb),(*a,ha)],[(0,1,2,3)],plaster)
# Distinct raised edge copings observed on the source; section dimension provisional.
for i,j in [(0,2),(2,1)]:
 a=pts[i];b=pts[j];direction=(b-a).normalized();cross=Vector((-direction.y,direction.x,0)).normalized()*.07;up=Vector((0,0,.16));mesh('ARCH_REAR_ROOF_COPING_'+str(i),[a-cross,b-cross,b+cross,a+cross,a-cross+up,b-cross+up,b+cross+up,a+cross+up],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],stone)
s=bpy.context.scene;s['acceptance']='Unaccepted architectural candidate. Source-supported rear roof projection, raw fit p90 0.275m; facade apertures and side/rear roofs still pending.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_ARKA_CIKMA_v079.blend'))
target=Vector((-80,-301,-66));s.camera.location=target+Vector((-20,31,30));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/qa/R169_architectural_rear_v079.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_ARCHITECTURAL_REAR_v079.json').write_text(json.dumps(dict(accepted=False,fit=d,method='Independent roof triangle, wall planes and coping solids; no source mesh/texture.',remaining=['Rear openings','Side and rear roof band','Chimneys','Ground contact','Full visual/GLB acceptance']),indent=2));print('REAR_ARCHITECTURE_SAVED')
