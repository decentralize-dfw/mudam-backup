import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];W=R/'reports'
CACHE=R/'.local_source_cache/r588_ground'
CACHE.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R588_BATI_CEPHE_TERAS_KADEMELI_BIRLESIM_ADAY_v010.blend'))
names=['R152_CLASS2_TERRAIN','R523_WEST_MOAT_LOWER_GROUND_0','R588_WEST_CLASS2_GROUND_RESTORATION'];bv={}
for name in names:
 o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles();bv[name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[t.vertices for t in m.loop_triangles],all_triangles=True)
def h(name,x,y):
 p,n,i,d=bv[name].ray_cast(Vector((x,y,20)),Vector((0,0,-1)),60);return p.z if p else None
seam=[]
for y in np.arange(-8,1.15,.25):
 a=h(names[0],-27.2501,float(y));b=h(names[1],-27.2499,float(y))
 if a is not None and b is not None:seam.append(dict(y=float(y),left=a,right=b,gap=abs(a-b)))
S=json.loads((W/'R588_R523_SOURCE_GRADE_AUDIT.json').read_text());controls=S['core']['controls'];hold=[]
for i,(x,y,z)in enumerate(controls):
 if i%4 or not(-31.8<=x<=-25.2 and -8.35<=y<=-1.3):continue
 hits=[h(n,x,y)for n in names];hits=[q for q in hits if q is not None]
 if hits:hold.append(dict(x=x,y=y,source=z,model=max(hits),error=max(hits)-z))
old=json.loads((CACHE/'R588_GROUND_FULL_INPUT.json').read_text())['R152_CLASS2_TERRAIN'];terrain=bpy.data.objects[names[0]];m=terrain.data;m.calc_loop_triangles()
def outside(v):return max(x[0]for x in v)<-33 or min(x[0]for x in v)>-24 or max(x[1]for x in v)<-9.55 or min(x[1]for x in v)>3.8
def key(v):return tuple(sorted(tuple(round(float(a),5)for a in q)for q in v))
orig=[key([old['vertices'][i]for i in t['vertices']])for t in old['triangles']if outside([old['vertices'][i]for i in t['vertices']])]
new=set(key([list(m.vertices[i].co)for i in t.vertices])for t in m.loop_triangles)
missing=[k for k in orig if k not in new]
inherited=json.loads((W/'R588_ORIGINAL_TERRAIN_DEGENERACY.json').read_text());inherited_keys={key(v)for v in inherited['faces']};missing_valid=[k for k in missing if k not in inherited_keys]
assert not missing_valid, ('Valid-area inherited terrain triangles lost',len(missing_valid))
out=dict(seam=seam,seamMax=max(q['gap']for q in seam),independentLowerHeldout=hold,heldoutRMS=float(np.sqrt(np.mean([q['error']**2 for q in hold]))),heldoutMax=max(abs(q['error'])for q in hold),untouchedTerrainTriangles=len(orig),missingUntouchedTerrainTriangles=len(missing),inheritedDegenerateTerrainTrianglesRemoved=len(missing),missingNondegenerateTerrainTriangles=len(missing_valid),validAreaUntouchedTrianglesPreserved=len(orig)-len(missing),inheritedDegeneracyReport='R588_ORIGINAL_TERRAIN_DEGENERACY.json',limits='Independent source check limited to supported lower visible floor; upper edge is candidate topology. No whole museum/source acceptance.')
(W/'R588_V010_CONTACT_CHECK.json').write_text(json.dumps(out,indent=2));print(out)
