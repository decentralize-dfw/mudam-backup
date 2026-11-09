import bpy,json,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];versions={}
for label,file in [('base','MUDAM_R328_KALINTI_LIDAR_TABAN_ADAY_v001.blend'),('candidate','MUDAM_R334_HENDEK_CAKISMA_TEMIZLIK_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/file));items={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  h=hashlib.sha256();a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());a=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',a);h.update(a.tobytes());h.update(str(tuple(tuple(row) for row in (o.matrix_basis if o.hide_viewport else o.matrix_world))).encode());items[o.name]=h.hexdigest()
 versions[label]=items
a,b=versions['base'],versions['candidate'];changed=[n for n in a.keys()&b.keys() if a[n]!=b[n]];added=sorted(b.keys()-a.keys());removed=sorted(a.keys()-b.keys());allowed=lambda n:n in ['R152_CLASS2_TERRAIN','R326_NORTH_RUIN_CROSSWALL_02','R327_EAST_RUIN_CENTRAL_COURT'] or n.startswith(('R152_HISTORIC_WALL_','R152_RUIN_PARTITION_','R152_PATH_'))
unexpected=[n for n in changed if not allowed(n)];assert not unexpected and all(n.startswith('R152_RUIN_PARTITION_') for n in removed),(unexpected,removed)
report=dict(changed=sorted(changed),added=added,removed=removed,unexpected=unexpected,unchanged=sum(a[n]==b[n] for n in a.keys()&b.keys()),museumGeometryPreserved=True,scope='Geometry positions, face loop indices and object matrices; not a source-fidelity acceptance')
(R/'reports/R334_INHERITANCE.json').write_text(json.dumps(report,indent=2));print('R334_INHERITANCE',report)




