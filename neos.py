#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np, Image
import os
from astrotools import *
import datetime as dt
t0 = dt.datetime.now()
fitfolder = '../Descargas/suleika/'
pngfolder = "./equalized"

e = Image.open("/home/rodolfo/neosfinder/1 a 041.png")
a = Getdata(fitfolder+"suleika_3_b1x_-041.fit")
FindRefs(a)

#~ e = Image.open("/home/rodolfo/neosfinder/1 a 041.png")
#~ a = np.asarray(e)[462-10:460+20,805-20:805+15]
#~ yy, xx = np.where(a > 50) # 
#~ BB = (yy.min(), yy.max(), xx.min(), xx.max())
#~ 
#~ print a.shape
#~ print a[BB[0]-1:BB[1]+1,BB[2]-1:BB[3]+1]
#~ print"uSecs.: ", dt.datetime.now()-t0


# Saving pngs from fits
#~ cant = 0
#~ for filename in sorted(os.listdir(fitfolder[:-1])):
	#~ cant += 1
	#~ f = fitfolder+filename
	#~ update_progress(cant,len(os.listdir(fitfolder[:-1])))
	#~ #if cant < 119 : continue
	#~ if not(cant==2) : continue
	#~ data = Getdata(f)
	#~ Savepng("debug/"+filename[:-4],data,i0=4000,i1=10000,sharp=2.3)

# Saving pngs with crosses from fits
#~cant = 0
#~for filename in sorted(os.listdir(fitfolder[:-1])):
	#~cant += 1
	#~f = fitfolder+filename
	#~update_progress(cant,len(os.listdir(fitfolder[:-1])))
	 #if cant < 119 : continue
	#~if not(cant==1) : continue
	#~data = Getdata(f)
	#~refs = FindRefs(data)
	#~png = Fit2png(data,i0=4000,i1=10000,sharp=2.3).astype(np.uint8)
	#~png = png - np.amin(png)
	#~png = Putcross(png,refs)
	#~e = Image.fromarray(png)
	#~e.save("./equalized/debug/"+filename[:-4]+".png")
	
 # Checking fits
#~ fitlist = []
#~ for filename in sorted(os.listdir(fitfolder[:-1])):
 #~ f = fitfolder+filename
 #~ fitlist.append(f)
 #~ 
#~ exclude = Checkfits(fitlist)
#~ print exclude




	
			

