from pathlib import Path
import numpy as np
from PIL import Image
B=Path('12_Blender_Model');n=2048;y,x=np.mgrid[0:n,0:n]/n
warp=x+.008*np.sin(2*np.pi*y)+.004*np.sin(6*np.pi*y+1)
grain=.045*np.sin(2*np.pi*warp*43)+.022*np.sin(2*np.pi*warp*127+.3*np.sin(8*np.pi*y))+.012*np.sin(2*np.pi*warp*293)
tone=1+grain+.035*np.sin(2*np.pi*x*3+.4*np.sin(2*np.pi*y))
linear=np.clip(np.array([.28,.115,.044])[None,None,:]*tone[:,:,None],0,1)
srgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
Image.fromarray(np.uint8(np.clip(srgb*255,0,255))).save(B/'textures/R135_auditorium_wood_basecolor.png')
