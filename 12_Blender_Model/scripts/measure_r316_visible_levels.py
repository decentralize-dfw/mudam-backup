import bpy,json,statistics
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];points=[('north_moat_floor',745,285),('northeast_grass',1070,275),('east_terrace',1040,630),('pavilion_south_moat',770,930),('fort_inner_terrace',685,760),('fort_north_moat',465,640),('front_round_moat',270,865),('north_ruin',555,160),('east_ruin',1170,795),('south_path',1010,950),('west_moat',480,450)];out={}
for label,path in [('source',R/'.local_source_cache/r316/museum_ring_reference.blend'),('model',R/'scenes/MUDAM_R314_ECCL_GUNEY_KOSE_OTURUM_ADAY_v001.blend')]:
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
out['accepted']=False;out['method']='9 vertical samples in0.6m square at manually selected visible source ground locations; vegetation and vertical surfaces may contaminate samples; not global accuracy proof';(R/'reports/R316_VISIBLE_LEVEL_COMPARISON.json').write_text(json.dumps(out,indent=2));print([(a['name'],a['medianZ'],b['medianZ'],b['modelMinusSource']) for a,b in zip(out['source'],out['model'])])

