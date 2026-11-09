import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R425_KULE_FOTOGRAF_TEPelikleri_ADAY_v001.blend'));rows=[]
for name in ['R152_HISTORIC_WALL_51768377','R152_HISTORIC_WALL_92711484']:
 o=bpy.data.objects[name];groups={}
 for v in o.data.vertices:
  p=o.matrix_world@v.co;k=(round(p.x,3),round(p.y,3));groups.setdefault(k,[]).append((v.index,p.z))
 for (x,y),g in groups.items():
  if (name.endswith('92711484') and x<-66 and y<-31) or (name.endswith('51768377') and x<-45 and y<-61):rows.append(dict(name=name,xy=[x,y],bottom=min(z for i,z in g),top=max(z for i,z in g),indices=[i for i,z in g if z==max(a[1] for a in g)]))
(R/'reports/R428_FRONT_WALL_COLUMNS.json').write_text(json.dumps(rows,indent=2));print('columns',len(rows))
