import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(R/path));out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  h=hashlib.sha256();h.update(struct.pack('<16f',*[v for row in o.matrix_world for v in row]));co=[0.0]*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',co);h.update(struct.pack('<%df'%len(co),*co));idx=[0]*len(o.data.loops);o.data.loops.foreach_get('vertex_index',idx);h.update(struct.pack('<%di'%len(idx),*idx));out[o.name]=dict(geometry=h.hexdigest(),hidden=o.hide_render)
 return out
old=snapshot('scenes/MUDAM_R464_AVLU_CAMI_ZEMIN_KESISI_ADAY_v001.blend');new=snapshot('scenes/MUDAM_R501_BATI_SUR_AGAC_KOTU_DUZELTME_ADAY_v001.blend');changed=[k for k in old if k in new and old[k]!=new[k]];removed=sorted(set(old)-set(new));added=sorted(set(new)-set(old));unexpected=[k for k in changed if k not in ['R152_CLASS2_TERRAIN','R152_FORECOURT_0','R457_NORTH_LOADING_COURT','R152_HISTORIC_WALL_563325237'] and not k.startswith('R152_PATH_')];report=dict(unchanged=sum(old[k]==new.get(k) for k in old),changed=changed,removed=removed,added=added,unexpected=unexpected,accepted=False,published=False);assert not removed and not unexpected,report
rows=json.loads((R/'reports/R492_SITE_UV_AUDIT.json').read_text());uvchecks=[]
for row in rows:
 if not row['grass']:continue
 o=bpy.data.objects[row['name']];uv=o.data.uv_layers['UVMap'];err=max((abs(uv.data[l.index].uv.x-((o.matrix_world@o.data.vertices[l.vertex_index].co).x+500)/1150)+abs(uv.data[l.index].uv.y-((o.matrix_world@o.data.vertices[l.vertex_index].co).y+450)/1100) for l in o.data.loops),default=0);uvchecks.append(dict(name=o.name,maxUvError=err));assert err<1e-6,(o.name,err)
report['grassUvReopen']=uvchecks;(R/'reports/R501_INHERITANCE_AND_UV.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='grassUvReopen'})
