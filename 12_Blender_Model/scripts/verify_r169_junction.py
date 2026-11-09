from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];caps=json.loads((R/'.local_source_cache/r169/dormer_caps_33.json').read_text())['caps'][:4];base=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'][0]['base'];results=[]
for version,name in [(13,'MUDAM_R169_CATI_CIKMALARI_ADAY_v013.blend'),(14,'MUDAM_R169_CATI_BIRLESIM_ADAY_v014.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/name));o=bpy.data.objects['R169_MEASURED_ENVELOPE'];bpy.context.view_layer.update();blocked=[]
 for cap,py in zip(caps,[401,399,397,395]):
  a,b=[Vector((*p,z)) for p,z in zip(cap['xy'][:2],cap['z'][:2])];t=Vector((b.x-a.x,b.y-a.y,0));w=t.length;t.normalize();inward=Vector((t.y,-t.x,0));bottom=base+7.5+(500-py)*26/1600;n=0
  for ix in range(1,6):
   for iz in range(1,8):
    u=w*ix/6;top=a.z+(b.z-a.z)*ix/6;z=bottom+(top-bottom)*iz/8;p=a+t*u-inward*3;p.z=z;hit,loc,*_=o.ray_cast(p,inward,distance=3.001);n+=int(hit and (loc-p).length<2.999)
  blocked.append(n)
 points=[]
 for f in o.data.polygons:
  vs=[o.data.vertices[i].co for i in f.vertices]
  if all(not(25<v.x<51 and -284<v.y<-261) for v in vs):points.append(sorted(tuple(round(x,6) for x in v) for v in vs))
 digest=hashlib.sha256(repr(sorted(points)).encode()).hexdigest();results.append(dict(version=version,roof_occlusions_per_35_rays=blocked,other_buildings_hash=digest,other_faces=len(points)))
assert results[0]['other_buildings_hash']==results[1]['other_buildings_hash'];assert sum(results[1]['roof_occlusions_per_35_rays'])==0,results
(R/'reports/R169_JUNCTION_VERIFICATION_v014.json').write_text(json.dumps(dict(results=results,accepted=False,scope='140 dormer-front sightlines and unchanged other-building geometry; not whole-building acceptance'),indent=2));print('JUNCTION_CHECK',results)
