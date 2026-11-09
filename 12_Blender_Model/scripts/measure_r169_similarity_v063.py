from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path('12_Blender_Model');rows=[]
def box(a):
 p=np.pad(a,3,mode='reflect');s=np.pad(p,((1,0),(1,0))).cumsum(0).cumsum(1);return (s[7:,7:]-s[:-7,7:]-s[7:,:-7]+s[:-7,:-7])/49
for view in ['rear','front','top']:
 def im(tag):return np.asarray(Image.open(R/f'renders/qa/R169_similarity_v063_{tag}_{view}.png').convert('RGB'),dtype=float)/255
 a,b,m=im('source'),im('model'),im('mask');mask=box(m[:,:,0]>.95)>.999;x=a@np.array([.2126,.7152,.0722]);y=b@np.array([.2126,.7152,.0722]);mx,my=box(x),box(y);ss=((2*mx*my+.01**2)*(2*(box(x*y)-mx*my)+.03**2))/((mx*mx+my*my+.01**2)*(box(x*x)-mx*mx+box(y*y)-my*my+.03**2));rows.append(dict(view=view,pixels=int(mask.sum()),ssim=float(ss[mask].mean()),mae=float(abs(a-b)[mask].mean())))
print(rows);(R/'reports/R169_VISUAL_SIMILARITY_v063.json').write_text(json.dumps(dict(views=rows,scope='Projected visible model surface only; missing source coverage and hidden facades are not certified; not overall context similarity.',accepted=False),indent=2))


