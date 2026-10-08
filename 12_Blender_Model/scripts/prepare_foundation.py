"""P00/P03 inputs. Preserve source bytes; establish exact coordinate checks."""
from pathlib import Path
import json,hashlib,platform,ctypes,math,sys
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';A=R/'10_Olcekli_Plan_ve_Fotograf_Analizi'
for folder in ['scenes','references','reports','renders/qa','config']:(B/folder).mkdir(exist_ok=True,parents=True)
C=json.loads((A/'kalibrasyon.json').read_text(encoding='utf-8'))
inventory=json.loads((R/'00_Kaynaklar/envanter.json').read_text(encoding='utf-8'))
audit=json.loads((A/'06_Tek_Tek_Denetim/fotograf_denetimi.json').read_text(encoding='utf-8'))
M=C['pdf_to_utm_matrix'];k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset']
def xy(p):
 u=k*p[0]+off[0];v=k*p[1]+off[1]
 return [M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960]
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
manifest=[]
for p in inventory:
 if p['status']!='ok':continue
 path=R/p['path'];assert path.is_file(),p['id']
 digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==p['sha256'],p['id']
 manifest.append(dict(id=p['id'],path=p['path'],sha256=digest,source_url=p['source'],credit=p['credit'],source_date='unknown; do not infer from download date',modified=False))
extra=R/'08_Belgeler/Mudam_Wim_Delvoye_2016_kat_semalari.pdf'
manifest.append(dict(id='PDF2016',path=extra.relative_to(R).as_posix(),sha256=hashlib.sha256(extra.read_bytes()).hexdigest(),source_url=None,credit='Mudam, Wim Delvoye 2016 press kit, page 5; existing local calibration source',source_date='2016',modified=False,provenance_gap='Exact original download URL not retained in local inventory'))
additional=B/'references/upper_gallery_2007/manifest.json'
if additional.exists():
 for p in json.loads(additional.read_text(encoding='utf8')):
  assert hashlib.sha256((R/p['path']).read_bytes()).hexdigest()==p['sha256']
  manifest.append(p)
write(B/'references/source_manifest.json',manifest)
checks=[]
for cp in C['controls']:
 u,v=cp['pdf_xy'];canonical=[(u-off[0])/k,(v-off[1])/k];world=xy(canonical)
 expected=[M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960]
 err=math.dist(world,expected);assert err<1e-7
 checks.append(dict(name=cp['name'],canonical=canonical,local_xy=world,osm_local_xy=[cp['utm'][0]-293425,cp['utm'][1]-5499960],numerical_transfer_error_m=err,source_osm_residual_m=cp['residual_m'],role=cp['role']))
origin=xy([0,0]);vx=[a-b for a,b in zip(xy([1,0]),origin)];vy=[a-b for a,b in zip(xy([0,1]),origin)]
assert abs(math.hypot(*vx)-C['meters_per_canonical_pixel'])<1e-8
assert vx[0]*vy[1]-vx[1]*vy[0]<0 # canonical image Y points down
write(B/'reports/P03_coordinate_checks.json',dict(checks=checks,basis_x=vx,basis_image_y=vy,blender_y='north positive; atlas y must be negated',max_numeric_error_m=max(p['numerical_transfer_error_m'] for p in checks),survey_accuracy_claim=False))
class Mem(ctypes.Structure):
 _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ['total','available','totalpage','availpage','totalvirtual','availvirtual','ext']]
mem=Mem();mem.length=ctypes.sizeof(mem);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
write(B/'reports/P00_environment.json',dict(os=platform.platform(),python=platform.python_version(),ram_bytes=mem.total,blender='4.2.0',gpu='NVIDIA GeForce RTX 4070 Laptop GPU',vram_mib=8188,source_files_verified=len(manifest),photo_reviews=len(audit)))
# Model sketches are explicit editable diagrams. They are not concrete slab extents.
polygons={
 'PAV':[(42,264),(92,215),(122,215),(171,264),(171,294),(122,344),(92,344),(42,294)],
 'LINK':[(171,264),(289,264),(289,294),(171,294)],
 'GH':[(462,334),(688,334),(688,463),(594,555),(465,555),(462,438)],
 'ENT':[(465,555),(689,555),(689,710),(617,710),(595,690),(557,690),(537,710),(465,710)],
 'EAST_GARDEN':[(289,161),(462,334),(462,438),(289,265)],
}
# West curve is a reference outline; sampled from schematic perimeter, not mirrored east.
curve=[]
for i in range(33):
 t=i/32;curve.append(((1-t)**2*688+2*(1-t)*t*745+t*t*862,(1-t)**2*334+2*(1-t)*t*218+t*t*161))
polygons['WEST_CAFE']=curve+[(862,258),(688,432)]
write(B/'config/foundation.json',dict(version='v001',calibration=C,polygons=polygons,
 measured_levels={'LM1':None,'L00':0,'LP1':None},
 display_offsets={'LM1':-12,'L00':0,'LP1':12},
 display_offsets_note='Exploded diagram spacing ONLY. Not building elevations. Architectural meshes remain at local Z=0 in their floor parent.',
 source_trace_note='Visitor diagram contours and 2016 vector ink are reference geometry, never wall thickness.',
 photo_ids=['021','043','049','051','055','066','067','097','115']))
write(B/'config/reference_gate.json',dict(review_date='2026-10-08',photo_visual_audit_complete=True,photos_reviewed=105,verified_camera_poses=0,reference_foundation_enabled=True,production_geometry_enabled=False,reason='P00/P03 reference foundation is authorized and enabled. Legacy build_mudam.py remains disabled: unverified heights, line-width walls and incorrect window/roof assumptions must not be reused. P04 studies may use clearly separated draft parameters.'))
print('P00 source hashes verified:',len(manifest),'P03 control points:',len(checks))
