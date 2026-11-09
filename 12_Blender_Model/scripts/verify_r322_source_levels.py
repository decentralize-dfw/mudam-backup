import bpy,json,statistics
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];points=[('holdout_00', 505, 550), ('holdout_01', 560, 560), ('holdout_02', 635, 560), ('holdout_03', 700, 600), ('holdout_04', 750, 660), ('holdout_05', 760, 730), ('holdout_06', 760, 790), ('holdout_07', 780, 850), ('holdout_08', 825, 880)];out={}
for label,path in [('source',R/'.local_source_cache/r316/museum_ring_reference.blend'),('model',R/'scenes/MUDAM_R322_BATI_MUZE_TERAS_KOT_ADAY_v004.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));vs=[];fs=[];names=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render:continue
  o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in t.vertices] for t in o.data.loop_triangles);names.extend([o.name]*len(o.data.loop_triangles))
 bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=[]
 for name,px,py in points:
  x=-120+px*220/1400;y=95-py*220/1400;hits=[];obs=[]
  for dx in [-.3,0,.3]:
   for dy in [-.3,0,.3]:
    h,n,idx,dist=bvh.ray_cast(Vector((x+dx,y+dy,120)),Vector((0,0,-1)),300)
    if h:hits.append(h.z);obs.append(names[idx])
  z=statistics.median(hits) if hits else None;rows.append(dict(name=name,sourcePixel=[px,py],xy=[x,y],medianZ=z,spread=max(hits)-min(hits) if hits else None,hits=len(hits),objects=sorted(set(obs))))
 out[label]=rows
for a,b in zip(out['source'],out['model']):b['modelMinusSource']=b['medianZ']-a['medianZ'] if a['medianZ'] is not None and b['medianZ'] is not None else None
out['accepted']=False;out['method']='9 vertical samples in0.6m square at manually selected visible source ground locations; vegetation and vertical surfaces may contaminate samples; not global accuracy proof';(R/'reports/R322_INDEPENDENT_GROUND_CHECK.json').write_text(json.dumps(out,indent=2));print([(a['name'],a['medianZ'],b['medianZ'],b['modelMinusSource']) for a,b in zip(out['source'],out['model'])])


