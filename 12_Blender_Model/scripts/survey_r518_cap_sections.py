exec(open(__file__.replace('survey_r518_cap_sections.py','measure_r518_west_wall_trace.py')).read().split('rows=[]')[0])
points=[Vector((-56+px*76/1400,18-py*76/1400,0)) for px,py in pixels];rows=[]
for i,p in enumerate(points):
 tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();side=Vector((-tangent.y,tangent.x,0));hits=[]
 for j in range(-12,19):
  q=p+side*j*.1;h,co,n,idx,o,m=bpy.context.scene.ray_cast(dg,Vector((q.x,q.y,50)),Vector((0,0,-1)),distance=90)
  if h:hits.append(dict(offset=j*.1,xyz=list(co),nz=n.z))
 rows.append(dict(pixel=pixels[i],hits=hits))
(R/'reports/R518_CAP_SECTIONS.json').write_text(json.dumps(rows,indent=2))
print([(r['pixel'],[(round(h['offset'],1),round(h['xyz'][2],2))for h in r['hits'] if h['nz']>.8 and -.1<h['offset']<1.1])for r in rows])
