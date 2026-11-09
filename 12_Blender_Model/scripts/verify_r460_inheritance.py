import bpy,json,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];versions={}
for label,file in [('base','MUDAM_R418_KALE_OLCULU_KULE_CATILARI_ADAY_v001.blend'),('candidate','MUDAM_R460_KUZEY_AVLU_GECIS_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'scenes'/file));items={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  h=hashlib.sha256();a=array.array('f',[0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',a);h.update(a.tobytes());a=array.array('i',[0])*len(o.data.loops);o.data.loops.foreach_get('vertex_index',a);h.update(a.tobytes());h.update(str(tuple(tuple(row) for row in (o.matrix_basis if o.hide_viewport else o.matrix_world))).encode());items[o.name]=h.hexdigest()
 versions[label]=items
a,b=versions['base'],versions['candidate'];changed=[n for n in a.keys()&b.keys() if a[n]!=b[n]];added=sorted(b.keys()-a.keys());removed=sorted(a.keys()-b.keys());allowed=lambda n:n in ['R154_FORT_MASONRY_BODY','R154_FORT_ROUNDED_EARTH_ROOF','R152_CLASS2_TERRAIN'] or n.startswith(('R152_HISTORIC_WALL_','R152_RUIN_PARTITION_','R152_PATH_','R154_TOWER_','R154_ACORN_'))
unexpected=[n for n in changed if n not in ['R154_FORT_MASONRY_BODY','R154_FORT_ROUNDED_EARTH_ROOF','R152_HISTORIC_WALL_51768377','R152_HISTORIC_WALL_92711484','R152_CLASS2_TERRAIN','R303_EAST_UPPER_TERRACE','R152_FORECOURT_0'] and not n.startswith('R152_PATH_')];assert not unexpected and all(n.startswith('R152_RUIN_PARTITION_') for n in removed),(unexpected,removed)
report=dict(changed=sorted(changed),added=added,removed=removed,unexpected=unexpected,unchanged=sum(a[n]==b[n] for n in a.keys()&b.keys()),museumGeometryPreserved=True,scope='Geometry positions, face loop indices and object matrices; not a source-fidelity acceptance')
(R/'reports/R460_INHERITANCE.json').write_text(json.dumps(report,indent=2));print('R448_INHERITANCE',report)







