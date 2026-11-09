import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());eye=Vector((-107,-92,6));rot=(Vector((-63,-54,1.7))-eye).to_track_quat('-Z','Y');n=Vector((*f['direction'],0));t=Vector((*f['tangent'],0));origin=Vector((*f['entry'],0));out={}
for label,(px,py) in {'entranceCrown':(510,526),'windowCrown':(717,526),'windowLeftSpring':(675,566),'windowRightSpring':(757,566),'windowSill':(715,626)}.items():
 ray=rot@Vector(((px-600)/1200*36/50,(425-py)/1200*36/50,-1));q=eye+ray*((origin-eye).dot(n)/ray.dot(n));out[label]=dict(pixel=[px,py],world=list(q),tangent=(q-origin).dot(t),z=q.z)
(R/'reports/R432_FRONT_OPENING_PROJECTION.json').write_text(json.dumps(dict(landmarks=out,source='R429_front_source.png',camera=dict(eye=list(eye),target=[-63,-54,1.7],lens=50,resolution=[1200,850]),limits='Blurred ACT arches; top/edge pixels uncertain. Corroborate proportions with R423_68151060 photo. Plane is inherited front facade.'),indent=2));print(out)
