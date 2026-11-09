import bpy,bmesh,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R506_KULE_TASI_PBR_ADAY_v001.blend'));d=json.loads((R/'reports/R504_SOUTH_ROOF_PARAMETERS.json').read_text());cx,cy,r=d['edge']['fit'];ratio=r/4.7;inner=4.32*ratio-.015;outer=4.525;ox,oy=-57.4,-63.1;assert math.hypot(cx-ox,cy-oy)+inner<outer;c=json.loads((R/'reports/R399_FRONT_COURT_PLANES.json').read_text())['tower_forecourt']['plane'];o=bpy.data.objects['R420_SOUTH_LOW_COURT_CONTACT'];N=192;vs=[];fs=[]
for xx,yy,rr,dz in [(cx,cy,inner,0),(ox,oy,outer,0),(ox,oy,outer,-.12),(cx,cy,inner,-.12)]:
 for i in range(N):a=i*math.tau/N;x=xx+rr*math.cos(a);y=yy+rr*math.sin(a);vs.append((x,y,c[0]*x+c[1]*y+c[2]-.012+dz))
for k in range(4):
 for i in range(N):fs.append((k*N+i,k*N+(i+1)%N,((k+1)%4)*N+(i+1)%N,((k+1)%4)*N+i))
me=bpy.data.meshes.new('R507_SOUTH_MEASURED_COURT_CONTACT');me.from_pydata(vs,[],fs);me.update()
for m in o.data.materials:me.materials.append(m)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));checks=dict(nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces));bm.to_mesh(me);bm.free();assert not any(checks.values());o.data=me;o['source']='R507 annular measured court grade connects shifted/resized south tower to unchanged outer court boundary. Original material and outer footprint preserved.'
out=R/'scenes/MUDAM_R507_GUNEY_KULE_ZEMIN_TEMASI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));(R/'reports/R507_BUILD.json').write_text(json.dumps(dict(checks=checks,reopened=True,innerRadius=inner,outerRadius=outer,outerBoundaryUnchanged=True,accepted=False,published=False),indent=2))
