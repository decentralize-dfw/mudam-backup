from pathlib import Path
import io,json,urllib.request,zipfile
B=Path(__file__).resolve().parents[1];r=json.loads((B/'.local_source_cache/r150_tile_resource.json').read_text())
class RangeFile(io.RawIOBase):
 def __init__(self):self.pos=0;self.size=r['filesize']
 def seek(self,offset,whence=0):self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset;return self.pos
 def tell(self):return self.pos
 def read(self,n=-1):
  if n<0:n=self.size-self.pos
  if n==0:return b''
  req=urllib.request.Request(r['url'],headers={'Range':f'bytes={self.pos}-{min(self.size-1,self.pos+n-1)}'})
  with urllib.request.urlopen(req,timeout=90) as f:
   assert f.status==206,'Range unsupported';data=f.read();assert len(data)<=n
  self.pos+=len(data);return data
with zipfile.ZipFile(RangeFile()) as z:
 rows=[dict(name=i.filename,size=i.file_size,compressed=i.compress_size,method=i.compress_type,offset=i.header_offset) for i in z.infolist()];print(json.dumps(rows,indent=2));(B/'.local_source_cache/r150_zip_index.json').write_text(json.dumps(rows,indent=2))
