from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/build_r291_south_roof.py').read_text().replace('R291','R292').replace('r291','r292')
s=s.replace('r292_south_roof.json','r291_south_roof.json')
left=[(630,240),(659,226),(676,236),(700,224),(740,250),(631,270),(685,275),(590,305),(630,330),(538,360),(565,377),(486,447),(511,432),(442,511),(391,595),(390,627),(365,669),(351,691),(350,717),(390,717),(390,745)]
right=[(372,848),(421,805),(445,800),(469,791),(472,749),(533,746),(797,286),(820,270),(880,323),(868,349),(895,391),(926,388),(884,420),(927,428),(952,428),(884,459),(901,488),(921,475),(860,518)]
lights=[(x,y,15,24,[.55,-.835]) for x,y in left]+[(x,y,15,24,[.835,-.55]) for x,y in right]
lights[21]=(372,848,14,40,[.835,-.55])
a=s.index('lights=[');b=s.index('lightRecords=[]',a);s=s[:a]+'lights='+repr(lights)+'\n'+s[b:]
s=s.replace('150+px*.1875,300-py*.1875','175+px*.125,152-py*.125').replace('l*.1875/2','l*.125/2').replace('w*.1875/2','w*.125/2')
round_code='''
from math import sin,cos,pi
for k,(px,py,r) in enumerate([(445,599,9),(445,631,10),(458,665,10),(466,689,9),(495,695,9),(503,660,9)]):
 center=xy(px,py);pp=[tuple(center+Vector((cos(j*pi/12),sin(j*pi/12)))*r*.125) for j in range(24)]
 z=ds[0]['plane'][0]*(center.x-ds[0]['origin'][0])+ds[0]['plane'][1]*(center.y-ds[0]['origin'][1])+ds[0]['plane'][2]
 cutter=prism('TEMP_ROUND_APERTURE',pp,z-1,z+1,ma);boolean(slab,cutter)
 prism(f'R292_ROUND_GLASS_{k}',pp,z-.06,z-.02,glass)
 for j in range(24):
  a=Vector(pp[j]);b=Vector(pp[(j+1)%24]);aa=center+(a-center)*.86;bb=center+(b-center)*.86
  prism(f'R292_ROUND_REVEAL_{k}_{j}',[tuple(a),tuple(b),tuple(bb),tuple(aa)],z-.25,z+.16,bpy.data.materials['R262_PALE_COPING'])
 lightRecords.append(dict(sourcePixel=[px,py],circleRadius=r*.125,polygon=pp))
'''
s=s.replace('def clip(points,a,b,sign,inside):',round_code+'\ndef clip(points,a,b,sign,inside):')
s=s.replace('37 rectangular rooflights modeled; round lights and remaining perimeter openings unresolved','40 rectangular and 6 round rooflights independently traced from R291 close source; remainder outside slab unresolved')
(R/'scripts/build_r292_south_roof.py').write_text(s)
