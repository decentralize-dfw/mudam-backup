import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from collections import Counter
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R549_CAM_KANAT_DIS_ZEMIN_BAGLANTISI_ADAY_v001.blend'));bpy.data.objects.remove(bpy.data.objects['R548_WEST_MOAT_CONTINUOUS_SLOPE'],do_unlink=True);d=json.loads((R/'reports/R552_SLOPING_MASONRY_DESIGN.json').read_text());xy=[];idx={}
def ix(p):
 p=tuple(round(v,6)for v in p)
 if p not in idx:idx[p]=len(xy);xy.append(p)
 return idx[p]
fs=[tuple(ix(p)for p in t)for t in d['triangles']];n=len(xy);c=d['capCoefficients'];a,b,k=d['faceYfromXZ']
def z(x,y):return c[0]*x+c[1]*y+c[2]+c[3]*max(x+20,0)+c[4]*max(x+16,0)
vs=[(x,y,z(x,y))for x,y in xy]+[(x,a*x+b*(-8.2)+k if abs(y-(a*x+b*z(x,y)+k))<.0001 else y,-8.2)for x,y in xy];edges=Counter(tuple(sorted((f[i],f[(i+1)%3])))for f in fs for i in range(3));faces=fs+[tuple(i+n for i in reversed(f))for f in fs]+[(a,b,b+n,a+n)for(a,b),ct in edges.items()if ct==1];me=bpy.data.meshes.new('R552_WEST_SLOPING_MASONRY_PLINTH');me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));ck=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));assert not any(ck.values()),ck;bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials['R129_HISTORIC_MASONRY_APPEARANCE_CANDIDATE'])
for un in ('UVMap','R55_CONTEXT_METRIC_UV','METRIC_UV_4x3m'):
 uv=me.uv_layers.new(name=un)
 for f in me.polygons:
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.x/4,p.y/3)if abs(f.normal.z)>.5 else(p.x/4,p.z/3)
o['source']=d['method'];out=R/'scenes/MUDAM_R552_BATI_EGIMLI_TAS_SUR_GOVDESI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R552_BUILD.json').write_text(json.dumps(dict(check=ck,reopened=True,removed='R548_WEST_MOAT_CONTINUOUS_SLOPE',source=d['method'],accepted=False),indent=2));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=500;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-20,-2,-5));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-20,1,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=18;s.render.filepath=str(R/'renders/qa/R552_north_grade_close_candidate.png');bpy.ops.render.render(write_still=True)
