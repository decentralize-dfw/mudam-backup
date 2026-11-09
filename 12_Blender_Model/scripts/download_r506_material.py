import urllib.request,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];root=R/'textures/polyhaven_sandstone_blocks_04';root.mkdir(exist_ok=True);rows=[]
for suffix,fmt in [('diff','jpg'),('nor_gl','png'),('rough','jpg')]:
 name=f'sandstone_blocks_04_{suffix}_2k.{fmt}';url=f'https://dl.polyhaven.org/file/ph-assets/Textures/{fmt}/2k/sandstone_blocks_04/{name}';p=root/name
 if not p.exists():
  request=urllib.request.Request(url,headers={'User-Agent':'MUDAM-material-work/1.0'});p.write_bytes(urllib.request.urlopen(request,timeout=90).read())
 rows.append(dict(file=str(p.relative_to(R)),url=url,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(R/'reports/R506_MATERIAL_SOURCE.json').write_text(json.dumps(dict(source='https://polyhaven.com/a/sandstone_blocks_04',author='Rob Tuytel',license='CC0',physicalWidthMetres=3,files=rows,role='Generic compatible stone material, NOT a measured reproduction of museum masonry joints or a facade photograph'),indent=2));print(rows)
