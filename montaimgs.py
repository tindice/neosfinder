#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''  Busco Refs en fits.
	Alinear xor los png equalizados
'''
print "processing ..."

import numpy as np
from PIL import Image, ImageOps
import os, datetime as dt
from astrotools import *

fitfolder = os.path.expanduser('~/Descargas/suleika/')
#~ print fitfolder

pngfolder = "./equalized/"
cant = 0
totalx, totaly = 0,0
# Recorrer imagenes FIT -------------------------------
filelist = sorted(os.listdir(fitfolder[:-1]))
totalfiles = len(filelist)
shiftlog = open("./shift.log", "w")

t0 = dt.datetime.now()
exclude = Checkfits(fitfolder, filelist, log=False)

print"Checkfits: ", dt.datetime.now()-t0

t0 = dt.datetime.now()
print "processing %s*.fit files..." %(fitfolder)
for filename in filelist:
	if filename[-7:-4]=="150": break
	update_progress(cant,totalfiles)
	if filename[-4:] != ".fit" or filename in exclude:
		shiftlog.write("%s\t --- Excluded ---\n" %(filename+spc))
		continue		# -- next file
	cant += 1
	f = fitfolder+filename
	# Uso primera imagen como base para alinear -----------
	if cant == 1: 
		spc = " " * (len(filename) - 4)
		shiftlog.write("File%s\t dx\t dy\tadx\tady\n" %(spc))
		data = Getdata(f)
		pngsum = Fit2png(data).astype(np.uint8)
		refsy, refsx = FindRefs(data)
		continue		# -- next file
		
	prevrefsy = refsy
	prevrefsx = refsx
	refsy, refsx = FindRefs(data)
	
	# Buscar desplazamientos relativos -----------------
	dx = refsx-prevrefsx
	dy = refsy-prevrefsy
	# Quitando repetidos ------------
	dx = np.unique(dx)
	dy = np.unique(dy)
	
	# Elegir el mejor dx ensayando alineaciones------
	Height, Width = data.shape
	png = Fit2png(data).astype(np.uint8)
	for n in range(0,len(dy)):
		ali = np.maximum(Shift(png,dy=-totaly-dy[n]), pngsum)
		lumi = ali.mean()
		if n==0 or lumi < lumin:
			lumin = lumi
			besty = dy[n]
		# ahora para dx -------------
	for n in range(0,len(dx)):
		ali = np.maximum(Shift(png,dx=-totalx-dx[n],dy=-totaly-besty), pngsum)
		lumi = ali.mean()
		if n==0 or lumi < lumin:
			lumin = lumi
			besty = dx[n]
	# Check Out of Field:		
	if abs(totalx+bestx) >Width/2 or abs(totaly+besty) >Height/2:
		shiftlog.write("%s\t %i\t %i\t %i\t %i Field Out.\n" %(filename,bestx,besty,totalx,totaly))
		continue		# -- next file
			
	totalx += bestx		# acumulo desplazamientos absolutos:
	totaly += besty
	shiftlog.write("%s\t %i\t %i\t %i\t %i\n" %(filename,bestx,besty,totalx,totaly))
	# Alineamos ----------------------------------
	pngsum = np.maximum(Shift(png,-totalx,-totaly), pngsum)
		
	e = Image.fromarray(pngsum)
	e.save("out_1 a %s.png" %(filename[-7:-4]) )
print"Saving to 150: ", dt.datetime.now()-t0

shiftlog.close()		
			

