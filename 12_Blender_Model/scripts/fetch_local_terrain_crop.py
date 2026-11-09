from pathlib import Path
import sys,json,hashlib,datetime,urllib.request
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'.local_source_cache/gis_runtime'))
import rasterio,pyproj,numpy as np
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
out=B/'references/terrain_lidar2024';out.mkdir(exist_ok=True)
d=json.load(urllib.request.urlopen('https://data.public.lu/api/1/datasets/6749719a27724dbceac6f282/',timeout=45));res=next(x for x in d['resources'] if x['title']=='mnt-cog-lidar2024.tif');url=res['url']
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT='60'):
 with rasterio.open('/vsicurl/'+url) as src:
  bounds=transform_bounds('EPSG:32632',src.crs,293425-90,5499960-100,293425+100,5499960+110,densify_pts=21)
  win=from_bounds(*bounds,src.transform).round_offsets().round_lengths();a=src.read(1,window=win);profile=src.profile.copy();profile.update(width=a.shape[1],height=a.shape[0],transform=src.window_transform(win),compress='deflate',tiled=False);profile.pop('blockxsize',None);profile.pop('blockysize',None)
  p=out/'mudam_mnt_2024_crop.tif'
  with rasterio.open(p,'w',**profile) as dst:dst.write(a,1)
  receipt=dict(dataset=d['title'],dataset_id=d['id'],license=d.get('license'),source_url=url,resource=res,crs=str(src.crs),resolution=src.res,bounds=list(rasterio.windows.bounds(win,src.transform)),source_window=[win.col_off,win.row_off,win.width,win.height],utm32_requested_bounds=[293335,5499860,293525,5500070],height_min=float(a.min()),height_max=float(a.max()),shape=list(a.shape),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),limits=['Ground-class digital terrain surface; buildings and vegetation filtered.','Building model absolute vertical datum not yet registered. Do not use raw national heights as local scene z.'])
  (out/'manifest.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt,ensure_ascii=False,indent=2))
