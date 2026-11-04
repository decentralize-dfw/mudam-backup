import bpy,json,hashlib,time,sys
from pathlib import Path
import numpy as np
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');W=Path(__file__).parent
args=sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else []
base=Path(args[0])if args else R/'scenes/MUDAM_R585_DOGU_HENDEK_CIFT_ZEMIN_TEMIZ_ADAY_v001.blend'
final=Path(args[1])if len(args)>1 else R/'scenes/R588_BATI_TERAS_TEMAS_AO_ADAY_v002.blend'
output=Path(args[2])if len(args)>2 else R/'reports/R588_PACKAGE_INHERITANCE.json'
allowed={'R152_CLASS2_TERRAIN','R152_HISTORIC_WALL_759680904','R321_MUSEUM_WEST_MOAT_RETAINING','R322_WEST_MUSEUM_TERRACE','R490_NW_MINERAL_PASSAGE','R523_WEST_MOAT_LOWER_GROUND_0','R546_WEST_MOAT_EDGE_1','R549_WEST_GLASS_EXTERNAL_GROUND_0','R549_WEST_GLASS_EXTERNAL_GROUND_1','R552_WEST_SLOPING_MASONRY_PLINTH','R557_WEST_APPROACH_0','R557_WEST_APPROACH_1'}
def digest(a):return hashlib.sha256(a.tobytes()).hexdigest()
def collect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={}
 for o in bpy.data.objects:
  q={'type':o.type,'transform_hash':digest(np.array(o.matrix_world,dtype=np.float64)),'hide_render':o.hide_render}
  if o.type=='MESH':
   m=o.data;v=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',v);l=np.empty(len(m.loops),dtype=np.int32);m.loops.foreach_get('vertex_index',l);ps=np.empty(len(m.polygons),dtype=np.int32);pc=ps.copy();m.polygons.foreach_get('loop_start',ps);m.polygons.foreach_get('loop_total',pc)
   q.update(position_hash=digest(v),topology_hash=hashlib.sha256(l.tobytes()+ps.tobytes()+pc.tobytes()).hexdigest(),vertices=len(m.vertices),faces=len(m.polygons),loops=len(m.loops))
  out[o.name]=q
 return out
t=time.monotonic();a=collect(base);b=collect(final);changed=[dict(name=n,fields=[k for k,v in a[n].items()if b[n].get(k)!=v])for n in a.keys()&b.keys()if a[n]!=b[n]];added=sorted(b.keys()-a.keys());removed=sorted(a.keys()-b.keys());unexpected=[q for q in changed if q['name']not in allowed];unexpectedadded=[n for n in added if not n.startswith('R588_')];protected=[n for n in a if a[n]['type']=='MESH'and n not in allowed];protected_changed=[n for n in protected if b.get(n)!=a[n]]
report={'base':str(base),'final':str(final),'passed':not(unexpected or unexpectedadded or removed or protected_changed),'method':'Every bpy.data.object: local float32 mesh positions, vertex-loop topology + polygon starts/counts, float64 world transform, hide_render. Materials, normals, UV/AO excluded intentionally.','baselineObjects':len(a),'finalObjects':len(b),'changed':changed,'added':added,'removed':removed,'unexpectedChanges':unexpected,'unexpectedAdditions':unexpectedadded,'protectedBaselineMeshes':len(protected),'protectedChanged':protected_changed,'unchangedExistingObjects':sum(b.get(n)==a[n]for n in a),'museumGeometryUnchanged':not protected_changed,'elapsedSeconds':time.monotonic()-t}
output.write_text(json.dumps(report,indent=2));print('INHERITANCE_RESULT',json.dumps(report),flush=True);assert report['passed'],report
