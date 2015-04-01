#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np, os, Image
from astrotools import *
import datetime as dt
from recognize import recognize, stamptext


t0 = dt.datetime.now()
fitfolder = '../Descargas/suleika_2/'
pngfolder = "./tmp"

# Probando :
#=====================================================================
#~ e = Image.open(pngfolder+"/frame_002.png")
#~ a = np.asarray(e)[300:400,320:400]
#~ print a
#~ i,j = np.unravel_index(a.argmax(), a.shape)
#~ print i,j,a[i,j]

#~ e = Image.open("/home/rodolfo/neosfinder/1 a 041.png")
meta, a = Getdata(fitfolder+"suleika_2_b1x_-041.fit")
print meta
Pause()
#~ FindRefs(a)

# Probando equalizaciones:
#=====================================================================
#~ meta, a = Getdata(fitfolder+"suleika_2_b1x_-002.fit")
#~ size = (1530/2, 1020/2)
#~ while True:
	#~ print "min=%i, max=%i" %(np.amin(a), np.amax(a))
	#~ i0 = int(raw_input("i0:"))
	#~ i1 = int(raw_input("i1:"))
	#~ sharp = int(raw_input("sharp:"))
	#~ png = Fit2png(a, i0=i0, i1=i1, sharp=sharp) 
	#~ im = Image.fromarray(png)
	#~ img1 = im.copy()
	#~ img1.thumbnail(size, Image.BICUBIC)
	#~ img1.show()

# Probando recognize
#=====================================================================
#~ dim = 15
#~ c = []
#~ while len(c) != 1:
	#~ c = recognize("./tmp/Suma.png", dim)
	#~ print dim, len(c)
	#~ dim += 1

# Probando intrapolaciones:
#=====================================================================
#~ meta, a = Getdata(fitfolder+"suleika_2_b1x_-002.fit")
#~ size = (1530/2, 1020/2)
#~ png = Fit2png(a) 
#~ im = Image.fromarray(png)
#~ img1 = im.copy()
#~ img1.thumbnail(size, Image.ANTIALIAS)
#~ img1.save("./tmp/antialias.png")
#~ img1 = im.copy()
#~ img1.thumbnail(size, Image.NEAREST)
#~ img1.save("./tmp/nearest.png")
#~ img1 = im.copy()
#~ img1.thumbnail(size, Image.BILINEAR)
#~ img1.save("./tmp/BILINEAR.png")
#~ img1 = im.copy()
#~ img1.thumbnail(size, Image.BICUBIC)
#~ img1.save("./tmp/BICUBIC.png")  #  <----- LA MEJOR
#~ print "OK"

#~ e = Image.open("/home/rodolfo/neosfinder/1 a 041.png")
#~ a = np.asarray(e)[462-10:460+20,805-20:805+15]
#~ yy, xx = np.where(a > 50) # 
#~ BB = (yy.min(), yy.max(), xx.min(), xx.max())
#~ 
#~ print a.shape
#~ print a[BB[0]-1:BB[1]+1,BB[2]-1:BB[3]+1]
#~ print"uSecs.: ", dt.datetime.now()-t0


# Saving pngs from fits
#=====================================================================
cant = 0
for filename in sorted(os.listdir(fitfolder[:-1])):
	cant += 1
	f = fitfolder+filename
	update_progress(cant,len(os.listdir(fitfolder[:-1])))
	#if cant < 119 : continue
	if not(filename[-4:]==".fit") : continue
	meta,data = Getdata(f)
	print meta

# Saving pngs with crosses from fits
#=====================================================================
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
#=====================================================================
#~ fitlist = []
#~ for filename in sorted(os.listdir(fitfolder[:-1])):
 #~ f = fitfolder+filename
 #~ fitlist.append(f)
 #~ 
#~ exclude = Checkfits(fitlist)
#~ print exclude

print hhmmss2s("01:02:05")



	
			

