from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import numpy as np
from shapely.geometry import Polygon
from PIL import Image,ImageDraw
d=json.loads((R/'reports/R386_ROOF_EDGES.json').read_text());old=json.loads((R/'reports/R340_ROOF_BUILD_INPUT.json').read_text());roof=[];crest=[];proof=[]
# The end closure is retained from the visible end of the metal deck. Other
# stations locate two distinct architectural discontinuities, not scan faces.
for r in d['stations'][2:]:
 i=r['i'];bands=r['bands'];threshold=2.45 if i in [10,11] else 2.10
 metal=next((a-.1 for a,n,z in bands if z is not None and z>threshold),None)
 wall=next((a-.1 for a,n,z in bands if z is not None and z>3.0),None)
 assert metal is not None and wall is not None,(i,metal,wall)
 # Where both transitions share a 20cm measurement bin, keep a finite 8cm
 # modeled junction. This is within bin resolution, not a surveyed width.
 metal=min(metal,wall-.08)
 pt=np.array(r['point']);normal=np.array(r['normal'])
 roof.append((pt+normal*metal).tolist());crest.append((pt+normal*wall).tolist());proof.append(dict(station=i,roofOffset=metal,wallOffset=wall,edgeResolutionM=.2))
# Roof end has a real junction beside the middle tower, not an invented full ring.
roof=[old['roofOutline'][0],old['roofOutline'][1]]+list(reversed(roof))
crest=[[-55.58,-51.55],[-60.85,-46.0]]+list(reversed(crest))
# Put perimeter back in cyclic order: end-west -> west edge -> head -> east edge -> end-east.
assert Polygon(roof).is_valid,'roof crossed';assert Polygon(crest).is_valid,'crest crossed'
im=Image.open(R/'renders/qa/R336_fort_roof_source.png').convert('RGB');dr=ImageDraw.Draw(im)
for line,color in [(roof,'red'),(crest,'yellow')]:
 px=[((x+74.5)*1100/65,(-1.5-y)*1100/65) for x,y in line];dr.line(px+[px[0]],fill=color,width=3)
im.save(R/'renders/qa/R387_architectural_roof_boundaries.png')
(R/'reports/R387_ROOF_INPUT.json').write_text(json.dumps(dict(roofOutline=roof,crestOutline=crest,lowerPlane=old['lower']['plane'],upperPlane=old['upper']['plane'],raisedOutline=old['raisedOutline'],controls=proof,accepted=False,source='R336 plan view; R386 classified cross-profile architectural edge measurements; end junction retained from source trace',limits=['0.2m profile bins; end junction requires oblique comparison','Outer earth cover is not included in this package']),indent=2))
print('R387',Polygon(roof).area,Polygon(crest).area)
