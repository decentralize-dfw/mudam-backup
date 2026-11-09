import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
rows=json.loads((R/'reports/R323_MUSEUM_BOUNDARY_CONTACTS.json').read_text())
pixels=[(849,859),(790,805),(796,652),(748,605),(670,548),(600,540),(495,522)]
anchors=[(-120+x*220/1400,95-y*220/1400) for x,y in pixels]
points=[];records=[]
for row in rows:
 a,c=anchors[row['segment']:row['segment']+2];dx,dy=c[0]-a[0],c[1]-a[1];ln=math.hypot(dx,dy);n=(dy/ln,-dx/ln)
 hits=[h for h in row['hits'] if h['z']==-3.4 and h['distanceFromBoundary']<2.5 and h['normal'][0]*n[0]+h['normal'][1]*n[1]<-.3]
 h=min(hits,key=lambda h:h['distanceFromBoundary']) if hits else None
 p=[h['point'][0]+n[0]*.025,h['point'][1]+n[1]*.025] if h else row['xy']
 if not points or math.dist(p,points[-1])>.08:points.append(p)
 records.append(dict(original=row['xy'],result=p,wall=h['object'] if h else None,matched=bool(h)))
def simplify(p,tol=.025):
 if len(p)<3:return p
 a,b=p[0],p[-1];dx,dy=b[0]-a[0],b[1]-a[1];l=dx*dx+dy*dy
 def distance(q):
  t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/l)) if l else 0
  return math.hypot(q[0]-a[0]-dx*t,q[1]-a[1]-dy*t)
 ds=[distance(q) for q in p[1:-1]];m=max(ds)
 if m<=tol:return [a,b]
 k=ds.index(m)+1;return simplify(p[:k+1],tol)[:-1]+simplify(p[k:],tol)
points=simplify(points)
(R/'reports/R324_MUSEUM_CONTACT_BOUNDARY.json').write_text(json.dumps(dict(points=points,records=records,matched=sum(r['matched'] for r in records),unmatched=sum(not r['matched'] for r in records),scope='Only terrace boundary moves to existing exterior wall; museum unchanged. 25mm overlap for contact, no openings sealed.'),indent=2))
s=(R/'scripts/build_r323_west_ramp_terrace.py').read_text()
s=s.replace("poly += [[-120+x*220/1400,95-y*220/1400] for x,y in inner_pixels]","poly += json.loads((R/'reports/R324_MUSEUM_CONTACT_BOUNDARY.json').read_text())['points']")
s=s.replace('MUDAM_R323_BATI_RAMPA_TERAS_ADAY_v001','MUDAM_R324_MUZE_TERAS_TEMAS_ADAY_v001')
s=s.replace('r323_west_ramp_terrain_REVIEW','r324_museum_contact_REVIEW').replace('R323_west_ramp_terrace_v001.png','R324_museum_contact_v001.png').replace('R323_WEST_RAMP_TERRACE.json','R324_MUSEUM_CONTACT_TERRACE.json')
(R/'scripts/build_r324_museum_contact.py').write_text(s)
print('BOUNDARY_READY',len(points),sum(r['matched'] for r in records),len(records))
