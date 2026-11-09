from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/build_r326_north_ruin.py').read_text()
s=s.replace('MUDAM_R324_MUZE_TERAS_TEMAS_ADAY_v001','MUDAM_R326_KUZEY_KALINTI_PLAN_ADAY_v001')
s=s.replace('def xy(p):return (-57+p[0]*44/1200,84.5-p[1]*44/1200)','def xy(p):return (39+p[0]*42/1200,-14.25-p[1]*42/1200)')
s=s.replace("bpy.data.objects['R152_RUIN_PARTITION_01']","bpy.data.objects['R152_RUIN_PARTITION_11']")
a=s.index('outline=');b=s.index('\nplatform=',a)
s=s[:a]+'''outline=[(389,12),(858,194),(600,719),(343,650)]
holes=[[(414,151),(505,173),(532,97),(574,113),(547,191),(610,216),(638,139),(682,157),(654,235),(703,254),(727,185),(812,211),(780,292)],[(659,309),(763,346),(737,392),(632,353)],[(616,411),(721,449),(696,496),(590,455)],[(568,518),(671,553),(608,684),(505,642)],[(448,515),(466,480),(539,529),(525,560)]]''' + s[b:]
s=s.replace('range(1,10)','range(11,19)')
a=s.index('ribs=');b=s.index('# Central open garden',a)
s=s[:a]+'''ribs=[[(566,573),(629,594),(616,623),(553,602)]]
for i,p in enumerate(ribs):
 ob=prism('R327_EAST_RUIN_CROSSWALL_%02d'%i,p,-4.8,-.08,stone);uv(ob);ob['level_id']='SITE';ob['source']='Independent source-traced masonry remnant, R327 matched orthographic source view.'
''' + s[b:]
s=s.replace('[(535,490),(728,386),(894,599),(600,590)]','[(408,209),(654,285),(529,538),(373,556)]')
s=s.replace('R325_NORTH_RUIN','R327_EAST_RUIN')
s=s.replace("'R326_NORTH_RUIN_CROSSWALL_00','R326_NORTH_RUIN_CROSSWALL_01','R326_NORTH_RUIN_CROSSWALL_02','R326_NORTH_RUIN_CROSSWALL_03'","'R327_EAST_RUIN_CROSSWALL_00'")
s=s.replace('MUDAM_R326_KUZEY_KALINTI_PLAN_ADAY_v001.blend\';bpy.ops.wm.save','MUDAM_R327_DOGU_KALINTI_PLAN_ADAY_v001.blend\';bpy.ops.wm.save')
s=s.replace('r326_north_ruin_REVIEW','r327_east_ruin_REVIEW').replace('R326_north_ruin_candidate.png','R327_east_ruin_candidate.png').replace('R326_NORTH_RUIN_PLAN.json','R327_EAST_RUIN_PLAN.json')
s=s.replace('(-35,68,70)','(60,-30,70)').replace('(-35,68,0)','(60,-30,0)').replace('ortho_scale=44','ortho_scale=42')
s=s.replace('R316 source view','R327 source view').replace('north','east')
(R/'scripts/build_r327_east_ruin.py').write_text(s)
print('R327_BUILDER_READY')
