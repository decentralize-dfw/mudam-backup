from pathlib import Path
import sys,json,math,numpy as np
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'.deps'))
from pyproj import Transformer,CRS
ways=json.loads((BASE/'kaynak_veri/osm_ways_utm.json').read_text(encoding='utf-8'))
mudam=next(w for w in ways if w['id']=='9042342')
# Controls digitised from the exterior boundary of the official vector drawing,
# 2016 Wim Delvoye press kit page 5, PyMuPDF top-left page-point coordinates.
control=[
 ('Dogu_cam_salon_ucu',360.6904,233.5626,13,'fit'),
 ('Grand_Hall_dogu_kosesi',404.2654,277.5566,14,'fit'),
 ('Grand_Hall_bati_kosesi',460.5734,277.5566,15,'fit'),
 ('Bati_cam_salon_ucu',505.0714,233.9156,19,'fit'),
 ('Bati_kanat_dirsek',505.0714,259.0246,20,'fit'),
 ('Bati_merdiven_dis_kose',524.4094,278.3626,21,'fit'),
 ('Bati_merdiven_ic_kose',505.0714,297.7016,22,'fit'),
 ('Bati_galeri_dis_kose',505.0714,327.5946,23,'fit'),
 ('Dogu_galeri_dis_kose',360.6904,327.5946,1,'fit'),
 ('Giris_dogu_dis_kose',408.3644,375.1306,0,'check'),
 ('Giris_bati_dis_kose',457.7594,374.6976,24,'check'),
]
rows=[];vals=[]
for name,u,v,idx,role in control:
    if role!='fit':continue
    E,N=mudam['xy'][idx];rows.extend([[u,v,1,0],[-v,u,0,1]]);vals.extend([E,N])
# Reflect y-down drawing into north-up metric space, with ONE uniform scale.
a,b,tx,ty=np.linalg.lstsq(np.array(rows),np.array(vals),rcond=None)[0]
M=np.array([[a,b], [b,-a]])
scale=math.hypot(a,b)
def pdf_to_utm(u,v):return np.array([a*u+b*v+tx,b*u-a*v+ty])
# Canonical coordinates match the 1108 x 960 official level-0 diagram.
k=(505.0714-360.6904)/(862.5-289.5)
offset=np.array([360.6904-k*289.5,233.5626-k*161.5])
def canonical_to_utm(x,y):return pdf_to_utm(*(np.array([x,y])*k+offset))
def utm_to_canonical(E,N):return (np.linalg.solve(M,np.array([E-tx,N-ty]))-offset)/k
for row in control:
    name,u,v,idx,role=row
    estimated=pdf_to_utm(u,v);actual=np.array(mudam['xy'][idx])
    print(name,role,round(float(np.linalg.norm(actual-estimated)),3))
errors=[float(np.linalg.norm(pdf_to_utm(u,v)-np.array(mudam['xy'][idx]))) for _,u,v,idx,_ in control]
report=dict(crs='EPSG:32632',reference='OSM way 9042342',reference_url='https://www.openstreetmap.org/way/9042342',method='4-parameter similarity with y-axis reflection; no anisotropic scaling or local warping',pdf_to_utm_matrix=[[float(a),float(b),float(tx)],[float(b),float(-a),float(ty)]],canonical_to_pdf_scale=k,canonical_to_pdf_offset=offset.tolist(),meters_per_pdf_point=scale,meters_per_canonical_pixel=scale*k,fit_rmse_m=math.sqrt(sum(e*e for e,c in zip(errors,control) if c[4]=='fit')/9),holdout_rmse_m=math.sqrt(sum(e*e for e,c in zip(errors,control) if c[4]=='check')/2),controls=[dict(name=c[0],pdf_xy=c[1:3],osm_vertex=c[3],osm_node_id=mudam['node_ids'][c[3]],role=c[4],residual_m=e,utm=mudam['xy'][c[3]]) for c,e in zip(control,errors)],caveat='Residuals measure agreement with OSM, not surveying accuracy. OSM and diagram simplification remain unquantified. No surveyed control or photogrammetric camera solution.')
(BASE/'kalibrasyon.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('scale',scale*k,'fit RMS',report['fit_rmse_m'],'holdout',report['holdout_rmse_m'])
