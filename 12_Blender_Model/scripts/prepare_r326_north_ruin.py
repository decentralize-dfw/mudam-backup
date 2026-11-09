from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/build_r325_north_ruin_platform.py').read_text()
s=s.replace("def xy(p):return (-120+p[0]*220/1400,95-p[1]*220/1400)","def xy(p):return (-57+p[0]*44/1200,84.5-p[1]*44/1200)")
s=s.replace("outline=[(452,181),(577,108),(635,212),(468,211)]","outline=[(250,479),(778,167),(1045,631),(306,616)]")
a=s.index('holes=');b=s.index('\nplatform=',a)
s=s[:a]+"holes=[[(292,478),(750,220),(799,296),(344,568)],[(748,384),(826,337),(850,378),(774,421)],[(790,474),(880,430),(900,472),(811,518)],[(841,557),(932,530),(962,574),(863,600)],[(462,565),(505,501),(580,520),(592,550),(524,529),(484,579)]]"+s[b:]
a=s.index("wall=bpy.data.objects");b=s.index('# Central open garden',a)
s=s[:a]+'''old=[];changed=0
for i in range(1,10):
 ob=bpy.data.objects.get('R152_RUIN_PARTITION_%02d'%i)
 if ob:
  old.extend(v.co.z for v in ob.data.vertices);changed+=len(ob.data.vertices);bpy.data.objects.remove(ob,do_unlink=True)
ribs=[[(364,437),(389,423),(428,489),(404,503)],[(458,383),(482,369),(521,435),(497,449)],[(552,328),(576,314),(618,385),(592,400)],[(650,271),(675,257),(715,325),(690,340)]]
for i,p in enumerate(ribs):
 ob=prism('R326_NORTH_RUIN_CROSSWALL_%02d'%i,p,-4.8,-.08,stone);uv(ob);ob['level_id']='SITE';ob['source']='Independent source-traced planar cross-wall, R325 matched orthographic source view.'
''' + s[b:]
s=s.replace("[(520,180),(580,146),(613,207),(533,202)]","[(535,490),(728,386),(894,599),(600,590)]").replace("holes[2]","holes[4]")
a=s.index('suspect=[]');b=s.index("out=R/",a)
s=s[:a]+'''suspect=[]
def contains(x,y):
 points=[xy(p) for p in outline];inside=False
 for a,b in zip(points,points[1:]+points[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('R158_TREE_'):
  bounds=[o.matrix_world@Vector(p) for p in o.bound_box];x=sum(p.x for p in bounds)/8;y=sum(p.y for p in bounds)/8
  if contains(x,y):o.hide_render=True;o.hide_viewport=True;suspect.append(o.name)
''' + s[b:]
s=s.replace("'R152_RUIN_PARTITION_02'","'R326_NORTH_RUIN_CROSSWALL_00','R326_NORTH_RUIN_CROSSWALL_01','R326_NORTH_RUIN_CROSSWALL_02','R326_NORTH_RUIN_CROSSWALL_03'")
s=s.replace('MUDAM_R325_KUZEY_KALINTI_PLATFORM_ADAY_v001','MUDAM_R326_KUZEY_KALINTI_PLAN_ADAY_v001').replace('r325_north_ruin_REVIEW','r326_north_ruin_REVIEW').replace('R325_north_ruin_candidate.png','R326_north_ruin_candidate.png').replace('R325_NORTH_RUIN_PLATFORM.json','R326_NORTH_RUIN_PLAN.json')
s=s.replace("revisedWallTop=-.22","revisedWallTop=-.08").replace("treesForInspection=suspect","sourceCourtTreesHidden=suspect")
(R/'scripts/build_r326_north_ruin.py').write_text(s)
print('R326_READY')
