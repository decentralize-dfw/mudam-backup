from pathlib import Path
import sys,json,hashlib,datetime
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
m=json.loads((R/'references/terrain_lidar2024/manifest.json').read_text());out=R/'references/terrain_lidar2024/mudam_far_mnt_2024.tif'
with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT='60'):
 with rasterio.open('/vsicurl/'+m['source_url']) as src:
  bounds=transform_bounds('EPSG:32632',src.crs,293425-500,5499960-450,293425+650,5499960+650,densify_pts=21);win=from_bounds(*bounds,src.transform).round_offsets().round_lengths();a=src.read(1,window=win);profile=src.profile.copy();profile.update(width=a.shape[1],height=a.shape[0],transform=src.window_transform(win),compress='deflate',tiled=False);profile.pop('blockxsize',None);profile.pop('blockysize',None)
  with rasterio.open(out,'w',**profile) as dst:dst.write(a,1)
  receipt=dict(source_url=m['source_url'],license=m['license'],local_bounds=[-500,-450,650,650],crs=str(src.crs),resolution=src.res,shape=list(a.shape),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
  out.with_suffix('.json').write_text(json.dumps(receipt,indent=2));print('FAR_DTM_READY',receipt,flush=True)
