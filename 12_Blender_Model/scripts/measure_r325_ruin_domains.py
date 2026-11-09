import bpy,json,statistics
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];points=[('north_grass_a',550,180),('north_grass_b',575,190),('north_grass_c',605,197),('north_grass_d',530,183),('north_chamber_a',491,150),('north_chamber_b',540,130),('north_chamber_c',587,142),('north_chamber_d',611,180),('east_grass_a',1115,765),('east_grass_b',1109,811),('east_grass_c',1111,852),('east_chamber_a',1140,721),('east_chamber_b',1174,745),('east_chamber_c',1176,788),('east_chamber_d',1148,825)];out={}
for label,path in [('source',R/'.local_source_cache/r316/museum_ring_reference.blend'),('model',R/'scenes/MUDAM_R324_MUZE_TERAS_TEMAS_ADAY_v001.blend')]:
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
out['accepted']=False;out['method']='9 vertical samples in0.6m square at manually selected visible source ground locations; vegetation and vertical surfaces may contaminate samples; not global accuracy proof';(R/'reports/R325_RUIN_DOMAINS.json').write_text(json.dumps(out,indent=2));print([(a['name'],a['medianZ'],b['medianZ'],b['modelMinusSource']) for a,b in zip(out['source'],out['model'])])



