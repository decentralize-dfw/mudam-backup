import urllib.request,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];root=R/'textures/polyhaven_withered_grass';root.mkdir(exist_ok=True);rows=[]
for suffix,fmt in [('diff','jpg'),('nor_gl','png'),('rough','jpg')]:
 name=f'withered_grass_{suffix}_2k.{fmt}';url=f'https://dl.polyhaven.org/file/ph-assets/Textures/{fmt}/2k/withered_grass/{name}';p=root/name
 if not p.exists():
  request=urllib.request.Request(url,headers={'User-Agent':'MUDAM-material-work/1.0'});p.write_bytes(urllib.request.urlopen(request,timeout=90).read())
 rows.append(dict(file=str(p.relative_to(R)),url=url,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(R/'reports/R545_MATERIAL_SOURCE.json').write_text(json.dumps(dict(source='https://polyhaven.com/a/withered_grass',author='Charlotte Baglioni',license='CC0',physicalWidthMetres=2,files=rows,role='Generic dry sparse grass PBR matching observed landcover class; not a museum photograph or exact blade pattern'),indent=2));print(rows)
