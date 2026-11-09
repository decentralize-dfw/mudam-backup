from pathlib import Path
import bpy,bmesh,json,numpy as np,math
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'roof_planes_164179202.json').read_text());ang=float(np.load(D/'164179202.npz')['angle']);cs,sn=math.cos(ang),math.sin(ang);planes=[p['coeff'] for p in d['planes'][:3]]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_UST_DUVAR_ADAY_v033.blend'));o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bm=bmesh.new();bm.from_mesh(o.data)
def supported(f):
 p=f.calc_center_median();px=700+(p.x+67)*70;py=550-(p.y+299)*70;x,y=cs*p.x+sn*p.y,-sn*p.x+cs*p.y;z=min(a*x+b*y+c for a,b,c in planes)
 return 350<px<1015 and 120<py<904 and p.z-z>.20 and p.z>-64.5
pending={f for f in bm.faces if supported(f)};comps=[]
while pending:
 seed=pending.pop();group={seed};stack=[seed]
 while stack:
  for e in stack.pop().edges:
   for f in e.link_faces:
    if f in pending:pending.remove(f);group.add(f);stack.append(f)
 vs={v for f in group for v in f.verts};coords=np.array([tuple(v.co) for v in vs]);pix=np.c_[700+(coords[:,0]+67)*70,550-(coords[:,1]+299)*70];comps.append(dict(faces=len(group),area=sum(f.calc_area() for f in group),pixel_min=pix.min(0).tolist(),pixel_max=pix.max(0).tolist(),z_range=[float(coords[:,2].min()),float(coords[:,2].max())]))
comps.sort(key=lambda x:-x['area']);(D/'row_raised_components.json').write_text(json.dumps(comps,indent=2));print(json.dumps(comps[:12],indent=1),flush=True)
