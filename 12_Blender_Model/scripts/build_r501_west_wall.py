import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R497_ARAZI_YUZEY_NORMAL_ADAY_v001.blend'));fits=json.loads((R/'reports/R501_WEST_WALL_CAP_FITS.json').read_text());o=bpy.data.objects['R152_HISTORIC_WALL_563325237'];old=o.data;oldvs=[o.matrix_world@v.co for v in old.vertices];assert len(oldvs)%4==0
changes=[];vs=[]
for i in range(0,len(oldvs),4):
 ring=oldvs[i:i+4];mid=Vector(((ring[0].x+ring[1].x)/2,(ring[0].y+ring[1].y)/2));choices=[]
 for f in fits:
  a=Vector(f['start']);b=Vector(f['end']);t=(b-a).normalized();s=max(0,min((b-a).length,(mid-a).dot(t)));choices.append(((mid-(a+t*s)).length,f,s))
 _,f,s=min(choices,key=lambda x:x[0]);z=f['coefficients'][0]+f['coefficients'][1]*s
 for j,v in enumerate(ring):
  q=v.copy();q.z=-14 if j<2 else z;vs.append(tuple(o.matrix_world.inverted()@q))
 changes.append(dict(ring=i//4,oldTop=ring[2].z,newTop=z,xy=list(mid),segment=f['segment']))
me=bpy.data.meshes.new('R501_WEST_PAVILION_WALL_GRADE');me.from_pydata(vs,[],[list(p.vertices) for p in old.polygons]);me.update()
for m in old.materials:me.materials.append(m)
for a,b in zip(old.polygons,me.polygons):b.material_index=a.material_index
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));check=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.to_mesh(me);bm.free();assert not any(check.values()),check;o.data=me
uv=me.uv_layers.new(name='R55_CONTEXT_METRIC_UV')
for face in me.polygons:
 for li in face.loop_indices:
  v=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.y/4,v.z/3) if abs(face.normal.x)>.6 else (v.x/4,v.z/3) if abs(face.normal.z)<.7 else(v.x/4,v.y/3)
o['source']='R501 replaces canopy-derived crest with independent cap grades from class1 wall returns; 16 withheld station cells across three segments. Existing mapped horizontal footprint retained. Bottom -14m is hidden closure, not surveyed foundation. End junction to higher R494 wall remains unresolved.'
out=R/'scenes/MUDAM_R501_BATI_SUR_AGAC_KOTU_DUZELTME_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));o=bpy.data.objects['R152_HISTORIC_WALL_563325237'];assert abs(max(v.co.z for v in o.data.vertices)-max(c['newTop'] for c in changes))<1e-5
(R/'reports/R501_WALL_BUILD.json').write_text(json.dumps(dict(check=check,changes=changes,reopened=True,accepted=False,published=False,limits=['Mapped footprint and width retained, not separately re-surveyed.','Western short return 838550868 and higher-wall end junction unresolved.','Hidden bottom closure -14m is not measured foundation.']),indent=2))
for label,path in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('candidate',str(out))]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=850;s.render.resolution_y=650;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(13,-87,7));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((45,-65,-6))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=38;s.render.filepath=str(R/f'renders/qa/R501_west_wall_{label}.png');bpy.ops.render.render(write_still=True)
