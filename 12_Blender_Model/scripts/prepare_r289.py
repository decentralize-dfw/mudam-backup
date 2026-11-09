from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
ds=json.loads((R/'config/r287_east_full_roofs.json').read_text())
traces=[[(320,615),(675,825),(478,1170),(105,955)],[(590,160),(883,333),(875,566),(745,725),(385,500)]]
for i,(d,trace) in enumerate(zip(ds,traces)):
    d['sourceImage']='R288_east_roofs_source.png'
    d['sourcePixels']=trace
    d['polygon']=[[325+x*110/1200,270-y*110/1200] for x,y in trace]
    a,b,c=d['plane'];ox,oy=d['origin']
    d['cornerRoofs']=[a*(x-ox)+b*(y-oy)+c for x,y in d['polygon']]
    d['unresolvedCropEdges']=[1] if i==1 else []
    d['fitScope']='R287 interior height samples only; revised boundary independently traced, not yet accepted'
(R/'config/r289_roof_boundaries.json').write_text(json.dumps(ds,indent=2))
s=(R/'scripts/build_r288_roofs.py').read_text().replace('r287_east_full_roofs.json','r289_roof_boundaries.json').replace('R288','R289').replace('r288','r289')
s=s.replace('/4\n for j in range(4):','/len(p)\n for j in range(len(p)):\n  if j in d[\'unresolvedCropEdges\']:continue')
s=s.replace('(j+1)%4','(j+1)%len(p)')
s=s.replace('(i+1)%4','(i+1)%len(region)').replace('for i in range(4))','for i in range(len(region)))')
s=s.replace("'Source visible slab boundary manually traced'","'Boundary corrected from matched R288 source view; white roof source crop unresolved and no coping added there'")
(R/'scripts/build_r289_roofs.py').write_text(s)
