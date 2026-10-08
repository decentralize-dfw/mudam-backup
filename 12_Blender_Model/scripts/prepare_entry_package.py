"""Record regional P07/P08 reconstruction inputs and photo-derived lower roof levels."""
from pathlib import Path
import json,math,numpy as np
from camera_math import project
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
F=json.loads((B/'config/foundation.json').read_text());D=json.loads((B/'config/vertical_study.json').read_text());s=F['calibration']['meters_per_canonical_pixel'];Z={p['id']:p['draft_value'] for p in D['parameters']}
multi=json.loads((B/'reports/P06_multiview.json').read_text())['photos']
def photo_height(photo,xy,pixel):
 r=multi[photo];p=np.array(r['camera']);lo,hi=-2,15
 for i in range(60):
  mid=(lo+hi)/2;pred=project(p,[[(575-xy[0])*s,(xy[1]-447)*s,mid]],r['size'])[0]
  if pred[1]>pixel[1]:lo=mid
  else:hi=mid
 h=(lo+hi)/2;pred=project(p,[[(575-xy[0])*s,(xy[1]-447)*s,h]],r['size'])[0]
 return dict(photo=photo,canonical_xy=xy,observed_px=pixel,draft_z=h,residual_x_px=float(pred[0]-pixel[0]))
reads=[photo_height('087',[688,430],[752,581]),photo_height('087',[462,430],[1178,581]),photo_height('119',[688,430],[620,650]),photo_height('119',[462,430],[988,650])]
low=[photo_height('087',[688,334],[728,695]),photo_height('087',[462,334],[1208,695])]
cfg=dict(version=1,status='regional_parametric_study_not_construction',scope='Entry canopy, three facade bays, lower Grand Hall glazing. No global shell acceptance.',sources=['102','PDF2016','101','008','011','013','026','087','093','116','119'],
 entry=dict(roof_triangle=[[478.7,723.3],[575,816],[674.7,721.6]],roof_top_z=Z['Z_ROOF_MAIN_BASE']-1.2,parapet_top_z=Z['Z_ROOF_MAIN_BASE'],soffit_z=Z['Z_ROOF_MAIN_BASE']-2.4,column_side_m=1.2,wall_depth_m=.45,pier_width_m=.45,glass_bottom_z=.18,transom_bottom_z=4.1,transom_height_m=.42,glass_head_z=Z['Z_ROOF_MAIN_BASE']-3.6,frame_width_m=.07,frame_depth_m=.10,glass_thickness_m=.02,vestibule_width_m=2.3,vestibule_depth_m=2.2,vestibule_height_m=2.75,
 chain=[[478.7,723.3],[488.9,712.8],[538,712.8],[562.6,688.1],[589,688.1],[613.9,712.8],[665.1,712.8],[674.7,721.6]],
 provenance={'roof_triangle':'102 faint canopy outline, supported by 008/011/116; six-point camera test in P06_camera_fit_116.json.', 'roof_top_z':'Existing P05 roof deck at H-1.2; conditional section scale.', 'soffit_z':'116 opening/top proportion candidate; not measured.', 'column_side_m':'011 confirms square corner support; 1.2 m is an explicit unmeasured placeholder.', 'wall_depth_m':'Visual envelope parameter, NOT a measured concrete structural thickness.', 'glazing_heights':'013/008 proportions; conditional heights, not construction dimensions.', 'frames_and_glass':'Replaceable visualization dimensions, not measured member sections or glass specification.', 'vestibule':'008/013 confirm projecting glazed revolving-door assembly; revolving mechanism/leaves intentionally unresolved.'}),
 lower_roof=dict(band_bottom_z=float(np.mean([p['draft_z'] for p in reads])),low_eave_z=float(np.mean([p['draft_z'] for p in low])),band_readings=reads,low_eave_readings=low,method='Conditional camera ray at fixed plan XY; solve Z to observed image Y. X residual retained, no image warp.',uncertainty='Camera/plan/source systematic error unquantified. Low eave uses only 087; requires another view. Not an independent metric validation.'),
 unresolved=['Concrete structure vs stone build-up not resolved; modeled entry solids are envelope volumes.','Exact pillar/beam cross-sections, window heads and frame sections remain hypotheses.','Revolving leaves, seals, drive and fixings not modeled.','Side-hall roof endpoint mapping and curved roof elevation require further checks.'])
cam116=json.loads((B/'reports/P06_camera_fit_116.json').read_text());cp=np.array(cam116['candidates']['triangular_canopy']['camera'])
lantern_levels={};lantern_checks=[]
for name,y in [('curb_top',716),('shoulder',694),('lantern_top',653),('apex',633)]:
 lo,hi=10,25
 for i in range(60):
  mid=(lo+hi)/2;v=project(cp,[[0,(642-447)*s,mid]],cam116['size'])[0]
  if v[1]>y:lo=mid
  else:hi=mid
 h=(lo+hi)/2;v=project(cp,[[0,(642-447)*s,h]],cam116['size'])[0];lantern_levels[name]=h
 lantern_checks.append(dict(id=name,photo='116',observed_px=[1319,y],draft_z=h,residual_x_px=float(v[0]-1319)))
cfg['reading_lantern']=dict(center_canonical=[575,642],outer_radius_canonical=23,inner_radius_canonical=15,**lantern_levels,readings=lantern_checks,source='103 documentation space centre and central opening; 116 built lantern. Z fitted after camera; not an independent height check.',uncertainty='Eight-sided form candidate; exact profile, curb and section widths unresolved. Dimensions remain D.')
(B/'config/entry_package.json').write_text(json.dumps(cfg,indent=2,ensure_ascii=False),encoding='utf8')
schedule=[]
for j,segment in enumerate([2,3,4]):
 a,b=cfg['entry']['chain'][segment:segment+2];w=math.dist(a,b)*s-cfg['entry']['pier_width_m']
 for lev,bottom,top in [('L00',cfg['entry']['glass_bottom_z'],cfg['entry']['transom_bottom_z']),('LP1',cfg['entry']['transom_bottom_z']+cfg['entry']['transom_height_m'],cfg['entry']['glass_head_z'])]:
  schedule.append(dict(id=f'ENT-{j+1:02}-{lev}',bay=j+1,level=lev,type='revolving_door_with_fixed_surround' if j==1 and lev=='L00' else 'fixed_glazed_opening',plan_segment=[a,b],draft_clear_width_m=w,draft_bottom_z=bottom,draft_head_z=top,sources=['PDF2016','102','008','013'],confidence_xy='C plan registration',confidence_z='D photo proportion',confidence_detail='U unmeasured',status='pilot_only'))
(B/'config/entry_openings.json').write_text(json.dumps(schedule,indent=2),encoding='utf8')
print('Entry openings:',len(schedule),'lower roof candidates:',cfg['lower_roof'])
