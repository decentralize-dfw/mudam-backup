from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parents[1];now=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=R/'config/context_reconstruction_queue.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
d['current_local_master']='MUDAM_R209_NOVOTEL_CATILAR_v001.blend'
d['local_candidate_accepted']=False
d['next_actions'].insert(0,'CURRENT R209 local master: R198/199 independent southwest ruin and central connecting masonry; R200 full273.717m mapped rail viaduct (ACTgrade supported onlyfirst164.83m); R201 Suites closed roof; R202/204 mappedAlzette and banks; R205 mapped lowerroadbridge; R206 Novotel dominant roofplanes29.616/16.150m and measuredparapets; R207 removes52actual R158 tree roots from building/river/rail footprints; R208 local2.5Dground normals andatlas/MicroUVrepair; R209 source-traced Novotel roofdivisions. All remain local candidates without final GLB/reopen/source acceptance. Small courtyard white seams, generic unverified facade cadence, fort source agreement, rail approach continuity, missing detailed architecture remain. Currentproduction509c3ce+receipt1cfa395 at20:22:50UTC is ONLY verifiedroad9+7backgroundmasses andprior134lower masses. Do not publish entiremaster or duplicate R169v088 row. Continue only11userregions. Historicalnext_actions below are superseded where inconsistent.')
d['updatedUTC']=now;p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'reports/R171_11_REGION_STATUS.json';d=json.loads(p.read_text());d['updatedUTC']=now;d['localMaster']='MUDAM_R209_NOVOTEL_CATILAR_v001.blend'
for r in d['regions']:
 if r['id']==1:r['implemented']+='; closed southwest ruin walls/floor and central connecting masonry';r['remaining']='Whole fort source agreement, terrace/wall/ground continuity and GLB/reopen acceptance'
 if r['id']==4:r['implemented']='Independent273.717m curved mapped railway viaduct, paired tracks, mapped lower roadbridge; source-supported grade forfirst164.83m only';r['remaining']='Railapproaches, outside-source grade/arch rhythm uncertainty, roadbridge approach connections and visual/export acceptance'
 if r['id']==6:r['implemented']+='; Novotel main roof planes corrected to29.616/16.150m, closed parapets and Suites roof, source-traced raised roof divisions';r['remaining']='Roof/source visual acceptance, Mama terrace level, facade module verification, all building ground relations'
 if r['id'] in [7,8]:r['remaining']='Connecting landscape and roads remain incomplete; simple masses already published509c3ce'
 if r['id']==10:r['remaining']='Ground edge connections and source visual/GLB acceptance; actualR158root audit found no station footprint roots to remove'
 if r['id']==11:r['implemented']+='; mapped river/banks,52actualtreecollisions removed, localterrain normals/UVrepair';r['remaining']='Complete all aprons and grade relations; courtyard white slivers remain; newlocalmaster notexportaccepted'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
